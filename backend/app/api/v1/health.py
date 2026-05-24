from fastapi import APIRouter

from app.core.response import success_response

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return success_response({"status": "healthy"})
