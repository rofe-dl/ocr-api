from fastapi import FastAPI
from ocr_api.routes import api_router
from ocr_api.utils.errors import register_error_handlers
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="OCR API",
)

register_error_handlers(app)

# TODO: Rate limiter
# TODO: Additional endpoints to check errors and logs
# TODO: Add type-hinting to all functions
# TODO: Try weird images, rotated images or images with no text

app.include_router(api_router)
