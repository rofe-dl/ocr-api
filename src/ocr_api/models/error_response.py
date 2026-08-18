from pydantic import BaseModel


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    error_stack: str
