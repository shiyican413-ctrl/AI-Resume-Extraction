from fastapi import APIRouter

from app.core.response import success_response

router = APIRouter(prefix="/results", tags=["results"])


@router.get("/{task_id}")
def get_result(task_id: str) -> dict:
    return success_response(
        {
            "task_id": task_id,
            "status": "finished",
            "result": {},
        }
    )
