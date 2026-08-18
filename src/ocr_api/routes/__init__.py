from fastapi import APIRouter
from ocr_api.routes.ocr_route import router as ocr_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(ocr_router)
