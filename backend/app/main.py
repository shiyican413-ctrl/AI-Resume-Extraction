from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import router as api_router
from app.core.config import get_settings
from app.core.errors import APIError
from app.core.response import error_response

settings = get_settings()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(APIError)
async def api_error_handler(_, exc: APIError):
    return JSONResponse(status_code=exc.status_code, content=error_response(exc.message, exc.error_code))


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_, exc: RequestValidationError):
    return JSONResponse(status_code=422, content=error_response(str(exc), "INVALID_REQUEST"))


@app.exception_handler(Exception)
async def unhandled_error_handler(_, __):
    return JSONResponse(status_code=500, content=error_response("服务内部错误", "INTERNAL_ERROR"))


app.include_router(api_router, prefix=settings.api_prefix)
