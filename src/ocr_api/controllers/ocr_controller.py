from fastapi import UploadFile
from ocr_api.models.ocr_schema import OCRResponse
import ocr_api.services.ocr_service as ocr_service


async def handle_text_extraction(image_file: UploadFile) -> OCRResponse:
    # math = 10 / 0 # Test unhandled error
    # raise HTTPException(status_code=400, detail='Bro this aint valid') # Test error handler

    # TODO: Implement
    return OCRResponse(
        success=True,
        text=str(image_file.size / 1000),
        confidence=0.0,
        cached=False,
        metadata=None,
        processing_time_ms=1.0,
    )
