from pydantic import BaseModel


class ImageMetadata(BaseModel):
    filename: str
    size_bytes: int
    width: int
    height: int
    image_format: str


class OCRResponse(BaseModel):
    success: bool
    text: str
    confidence: float
    processing_time_ms: float
    cached: bool = False
    metadata: ImageMetadata | None = None
