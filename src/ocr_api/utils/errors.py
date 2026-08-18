from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from ocr_api.models.error_response import ErrorResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("error_logger")


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(ErrorResponse(success=False, error=str(exc.detail))),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # logger.exception(f"Unhandled exception | {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=jsonable_encoder(
            ErrorResponse(
                success=False, error="Something has gone wrong! Please try again later."
            )
        ),
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
