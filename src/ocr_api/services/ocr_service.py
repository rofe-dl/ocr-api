from fastapi import HTTPException, UploadFile

from google.cloud import vision
from google.cloud.vision_v1 import ImageAnnotatorAsyncClient

from PIL import Image

import logging
import io
from typing import Tuple, Dict

from ocr_api.models.ocr_schema import ImageMetadata

logger = logging.getLogger("error_logger")


async def process_image(content: bytes) -> Tuple[str, float]:
    client = ImageAnnotatorAsyncClient()

    image = vision.Image(content=content)
    feature = vision.Feature(type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)
    request = vision.AnnotateImageRequest(image=image, features=[feature])

    responses = await client.batch_annotate_images(requests=[request])
    response = responses.responses[0]

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

    return (text.strip(), avg_confidence)


async def batch_process_images():
    pass


async def get_image_metadata(image_content: bytes, image_file: UploadFile) -> ImageMetadata:
    base_metadata = {"filename": image_file.filename, "size_bytes": image_file.size}

    try:
        with Image.open(io.BytesIO(image_content)) as img:
            width, height = img.size
            img_format = img.format

            return base_metadata | {"width": width, "height": height, "image_format": img_format}

    except Exception as e:
        logger.exception(f"Could not read image metadata: {e}")
        return {}
