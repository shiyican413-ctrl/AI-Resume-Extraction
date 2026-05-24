from pydantic import BaseModel


class APIResponse(BaseModel):
    success: bool
    message: str
    data: dict


class APIErrorResponse(BaseModel):
    success: bool
    message: str
    error_code: str
