from fastapi import HTTPException, UploadFile
import redis.asyncio as aioredis

from google.cloud import vision
from google.cloud.vision_v1 import ImageAnnotatorAsyncClient

from PIL import Image

import logging
import io
from typing import Tuple, Dict, List, Any
import asyncio
import hashlib
import json

logger = logging.getLogger("error_logger")


def _get_image_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _calculate_confidence_and_text(response: vision.AnnotateImageResponse) -> Tuple[str, float]:
    if response.error.message:
        raise HTTPException(status_code=500, detail=response.error.message)

    annotation = response.full_text_annotation
    text = annotation.text if annotation else ""

    total_confidence = 0.0
    count = 0

    if annotation:
        for page in annotation.pages:
            for block in page.blocks:
                for paragraph in block.paragraphs:
                    for word in paragraph.words:
                        if word.confidence:
                            total_confidence += word.confidence
                            count += 1

    avg_confidence = 0.0
    if count > 0:
        avg_confidence = round(total_confidence / count, 2)
    elif text:
        avg_confidence = 1.0

    return text.strip(), avg_confidence


async def process_image(content: bytes, redis: aioredis.Redis) -> Tuple[str, float, bool]:
    image_hash = _get_image_hash(content)

    if cached_response := await redis.get(f"ocr:{image_hash}"):
        return tuple(json.loads(cached_response))

    client = ImageAnnotatorAsyncClient()

    image = vision.Image(content=content)
    feature = vision.Feature(type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)
    request = vision.AnnotateImageRequest(image=image, features=[feature])

    responses = await client.batch_annotate_images(requests=[request])
    text, confidence = _calculate_confidence_and_text(responses.responses[0])

    # caches response for future
    await redis.setex(f"ocr:{image_hash}", 21600, json.dumps((text, confidence, True)))

    # boolean denotes if its a cached response or not
    return text, confidence, False


async def batch_process_images(
    images_bytes_and_files: List[Tuple[bytes, UploadFile]],
) -> List[Dict[str, Any]]:
    client = ImageAnnotatorAsyncClient()
    feature = vision.Feature(type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)

    requests = []
    metadata_tasks = []

    for content, file_obj in images_bytes_and_files:
        image = vision.Image(content=content)

        requests.append(vision.AnnotateImageRequest(image=image, features=[feature]))
        metadata_tasks.append(get_image_metadata(content, file_obj))

    # make the network request and metadata collection concurrently
    all_results = await asyncio.gather(*metadata_tasks, client.batch_annotate_images(requests=requests))

    # result of the batch network request is in the last index of all_results
    metadatas = all_results[:-1]
    batch_responses = all_results[-1]

    results = []
    for i, (content, file_obj) in enumerate(images_bytes_and_files):
        # gather each file's response and corresponding metadata together into one dict
        response = batch_responses.responses[i]
        file_metadata = metadatas[i]

        try:
            text, confidence = _calculate_confidence_and_text(response)
            results.append(
                {
                    "filename": file_obj.filename or f"image_{i}",
                    "success": True,
                    "text": text,
                    "confidence": confidence,
                    "metadata": file_metadata,
                    "error": None,
                }
            )
        except Exception as err:
            logger.exception(f"Error processing {file_obj.filename}: {err}")
            results.append(
                {
                    "filename": file_obj.filename or f"image_{i}",
                    "success": False,
                    "text": "",
                    "confidence": 0.0,
                    "metadata": file_metadata,
                    "error": str(err),
                }
            )

    return results


async def get_image_metadata(image_content: bytes, image_file: UploadFile) -> Dict[str, Any]:
    base_metadata = {"filename": image_file.filename, "size_bytes": image_file.size}

    try:
        with Image.open(io.BytesIO(image_content)) as img:
            width, height = img.size
            img_format = img.format

            return base_metadata | {"width": width, "height": height, "image_format": img_format}

    except Exception as e:
        logger.exception(f"Could not read image metadata: {e}")
        return base_metadata
