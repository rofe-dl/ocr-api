from fastapi import UploadFile
from ocr_api.models.ocr_schema import OCRResponse


async def handle_text_extraction(image_file: UploadFile) -> OCRResponse:
    # TODO: Implement
    return OCRResponse(
        success=True,
        text=str(image_file.size / 1000),
        confidence=0.0,
        cached=False,
        metadata=None
    )
