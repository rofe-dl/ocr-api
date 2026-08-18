from pydantic import BaseModel


class ImageMetadata(BaseModel):
    width: int
    height: int
    format: str
    mode: str


class OCRResponse(BaseModel):
    success: bool
    text: str
    confidence: float
    # processing_time_ms: float
    cached: bool = False
    metadata: str | None = None
