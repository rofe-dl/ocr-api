from fastapi import APIRouter, UploadFile, Request, HTTPException, Depends, File
import redis.asyncio as aioredis

from ocr_api.models.ocr_schema import BatchOCRResponse, BatchOCRItemResult, OCRResponse
from ocr_api.models.error_response import ErrorResponse
import ocr_api.services.ocr_service as ocr_service
from ocr_api.dependencies import get_redis, limiter

from typing import List
import time
import asyncio

router = APIRouter(tags=["OCR"])

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_BATCH_SIZE = 10
ALLOWED_FILE_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/gif"}


@router.post(
    "/text-extraction",
    response_model=OCRResponse,
    responses={
        400: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
@limiter.limit("10/minute")
async def extract_text(
    request: Request, image: UploadFile | None = File(None), redis: aioredis.Redis = Depends(get_redis)
) -> OCRResponse:
    if not image:
        raise HTTPException(status_code=400, detail="Please upload an image file.")

    start_time = time.perf_counter()

    image_content = await image.read()

    if image.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Your file size cannot be more than 10 MB.")
    elif image.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(status_code=400, detail="File type not supported. Supported: JPG, PNG, GIF")

    metadata, (text, confidence, is_cached) = await asyncio.gather(
        ocr_service.get_image_metadata(image_content, image), ocr_service.process_image(image_content, redis)
    )

    time_taken = round((time.perf_counter() - start_time) * 1000, 2)

    return OCRResponse(
        success=True,
        text=text,
        confidence=confidence,
        cached=is_cached,
        metadata=metadata,
        processing_time_ms=time_taken,
    )


@router.post(
    "/batch-text-extraction",
    response_model=BatchOCRResponse,
    responses={
        400: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
@limiter.limit("5/minute")
async def extract_text_batch(request: Request, images: List[UploadFile] = []) -> BatchOCRResponse:
    if len(images) == 0:
        raise HTTPException(status_code=400, detail="Please upload image files.")

    start_time = time.perf_counter()

    if not images:
        raise HTTPException(status_code=400, detail="No files provided.")

    if len(images) > MAX_BATCH_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Batch size exceeds maximum limit of {MAX_BATCH_SIZE} images per request.",
        )

    items = []

    for file_obj in images:
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
