from fastapi import HTTPException, UploadFile
from typing import List
import time
import asyncio

from ocr_api.models.ocr_schema import OCRResponse, BatchOCRResponse, BatchOCRItemResult
import ocr_api.services.ocr_service as ocr_service

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_BATCH_SIZE = 10
ALLOWED_FILE_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/gif"}


async def handle_text_extraction(image_file: UploadFile) -> OCRResponse:
    start_time = time.perf_counter()

    image_content = await image_file.read()

    if image_file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Your file size cannot be more than 10 MB.")
    elif image_file.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(status_code=400, detail="File type not supported. Supported: JPG, PNG, GIF")

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


async def handle_batch_text_extraction(image_files: List[UploadFile]) -> BatchOCRResponse:
    start_time = time.perf_counter()

    if not image_files:
        raise HTTPException(status_code=400, detail="No files provided.")

    if len(image_files) > MAX_BATCH_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Batch size exceeds maximum limit of {MAX_BATCH_SIZE} images per request.",
        )

    items = []

    for file_obj in image_files:
        if file_obj.content_type not in ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"File type of '{file_obj.filename}' not supported. Supported: JPG, PNG, GIF",
            )

        content = await file_obj.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400, detail=f"File '{file_obj.filename}' exceeds maximum allowed size of 10 MB."
            )

        items.append((content, file_obj))

    raw_results = await ocr_service.batch_process_images(items)

    formatted_results = [BatchOCRItemResult(**res) for res in raw_results]
    time_taken = round((time.perf_counter() - start_time) * 1000, 2)

    return BatchOCRResponse(
        success=True,
        total_images=len(formatted_results),
        results=formatted_results,
        processing_time_ms=time_taken,
    )
