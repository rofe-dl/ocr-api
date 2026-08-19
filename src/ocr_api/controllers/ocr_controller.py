from fastapi import HTTPException, UploadFile
from ocr_api.models.ocr_schema import OCRResponse
import ocr_api.services.ocr_service as ocr_service
import time
import asyncio

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_FILE_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}


async def handle_text_extraction(image_file: UploadFile) -> OCRResponse:
    # math = 10 / 0 # Test unhandled error
    # raise HTTPException(status_code=400, detail='Bro this aint valid') # Test error handler
    start_time = time.perf_counter()

    image_content = await image_file.read()

    if image_file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Your file size cannot be more than 10 MB.")
    elif image_file.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=400, detail="File type not supported. Supported file types: JPG, PNG, GIF"
        )

    metadata, (text, confidence) = await asyncio.gather(
        ocr_service.get_image_metadata(image_content, image_file), ocr_service.process_image(image_content)
    )

    time_taken = round((time.perf_counter() - start_time) * 1000, 2)

    return OCRResponse(
        success=True,
        text=text,
        confidence=confidence,
        cached=False,
        metadata=metadata,
        processing_time_ms=time_taken,
    )
