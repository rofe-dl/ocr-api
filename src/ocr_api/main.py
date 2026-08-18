from fastapi import FastAPI
from ocr_api.routes import api_router

app = FastAPI(
    title="OCR API",
)

# TODO: Rate limiter
# TODO: Error handler
# TODO: File size middleware

app.include_router(api_router)
