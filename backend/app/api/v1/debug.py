from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import get_settings
from app.core.errors import APIError
from app.core.response import success_response

router = APIRouter(prefix="/debug", tags=["debug"])

BACKEND_DIR = Path(__file__).resolve().parents[3]
ENV_FILE_PATH = BACKEND_DIR / ".env"
ALIYUN_MODEL_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
ALIYUN_MODEL_NAME = "qwen-plus"
ALIYUN_MODEL_NAME_FAST = "qwen3.5-flash"
ALIYUN_MODEL_NAME_PRECISE = "qwen3.5-plus"
ALIYUN_MODEL_NAME_PRECISE_OCR = "qwen-vl-ocr-latest"


class DebugEnvRequest(BaseModel):
    api_key: str


def build_env_content(api_key: str) -> str:
    settings = get_settings()
    return "\n".join(
        [
            f"DASHSCOPE_API_KEY={api_key}",
            f"MODEL_BASE_URL={ALIYUN_MODEL_BASE_URL}",
            f"MODEL_NAME={ALIYUN_MODEL_NAME}",
            f"MODEL_NAME_FAST={ALIYUN_MODEL_NAME_FAST}",
            f"MODEL_NAME_PRECISE={ALIYUN_MODEL_NAME_PRECISE}",
            f"MODEL_NAME_PRECISE_OCR={ALIYUN_MODEL_NAME_PRECISE_OCR}",
            f"PRECISE_MAX_OCR_PAGES={settings.precise_max_ocr_pages}",
            f"MAX_FILE_SIZE_MB={settings.max_file_size_mb}",
            f"CORS_ORIGINS={settings.cors_origins}",
            "",
        ]
    )


@router.post("/env")
def save_debug_env(request: DebugEnvRequest) -> dict:
    api_key = request.api_key.strip()
    if not api_key:
        raise APIError("请输入模型 API Key", "INVALID_REQUEST", 400)

    ENV_FILE_PATH.write_text(build_env_content(api_key), encoding="utf-8")
    get_settings.cache_clear()

    return success_response(
        {
            "configured": True,
            "provider": "aliyun-bailian",
            "env_file": str(ENV_FILE_PATH),
        },
        message="调试环境变量已生成",
    )
