from pydantic import BaseModel
from typing import Optional, List


class ImageMetadata(BaseModel):
    filename: Optional[str] = None
    size_bytes: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    image_format: Optional[str] = None


class OCRResponse(BaseModel):
    success: bool
    text: str
    confidence: float
    processing_time_ms: float
    cached: bool = False
    metadata: ImageMetadata | None = None


class BatchOCRItemResult(BaseModel):
    filename: str
    success: bool
    text: str
    confidence: float
    metadata: ImageMetadata | None = None
    error: Optional[str] = None


class BatchOCRResponse(BaseModel):
    success: bool
    total_images: int
    results: List[BatchOCRItemResult]
    processing_time_ms: float
