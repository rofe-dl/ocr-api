from fastapi import APIRouter, UploadFile, Request

from ocr_api.models.ocr_schema import BatchOCRResponse, OCRResponse
from ocr_api.models.error_response import ErrorResponse
import ocr_api.controllers.ocr_controller as ocr_controller

from typing import List

router = APIRouter(tags=["OCR"])


@router.post(
    "/text-extraction",
    response_model=OCRResponse,
    responses={
        400: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def extract_text(request: Request, image: UploadFile) -> OCRResponse:
    return await ocr_controller.handle_text_extraction(image)


@router.post(
    "/batch-text-extraction",
    response_model=BatchOCRResponse,
    responses={
        400: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def extract_text_batch(images: List[UploadFile]) -> BatchOCRResponse:
    return await ocr_controller.handle_batch_text_extraction(images)
