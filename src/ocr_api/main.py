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

app.include_router(api_router)
