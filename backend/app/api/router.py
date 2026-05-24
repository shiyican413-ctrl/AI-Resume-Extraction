from fastapi import APIRouter

from app.api.v1.debug import router as debug_router
from app.api.v1.health import router as health_router
from app.api.v1.match import router as match_router
from app.api.v1.resumes import router as resumes_router
from app.api.v1.results import router as results_router

router = APIRouter()
router.include_router(health_router)
router.include_router(debug_router)
router.include_router(resumes_router)
router.include_router(match_router)
router.include_router(results_router)
