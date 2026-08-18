from fastapi import FastAPI
from ocr_api.routes import api_router
from ocr_api.utils.errors import register_error_handlers

app = FastAPI(
    title="OCR API",
)

register_error_handlers(app)

# TODO: Rate limiter
# TODO: File size middleware
# TODO: Additional endpoints to check errors and logs
# TODO: Add type-hinting to all functions

app.include_router(api_router)
