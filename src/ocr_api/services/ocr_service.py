from fastapi import HTTPException
from google.cloud import vision
from google.cloud.vision_v1 import ImageAnnotatorAsyncClient
from typing import Tuple


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


async def get_image_metadata(image):
    pass
