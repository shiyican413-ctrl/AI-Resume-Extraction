from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Resume Analyzer"
    api_prefix: str = "/api/v1"
    max_file_size_mb: int = 10
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    model_api_key: str = Field(default="", alias="DASHSCOPE_API_KEY")
    model_base_url: str = Field(
        default="https://dashscope.aliyuncs.com/compatible-mode/v1",
        alias="MODEL_BASE_URL",
    )
    model_name: str = Field(default="qwen-plus", alias="MODEL_NAME")
    model_name_fast: str = Field(default="qwen3.5-flash", alias="MODEL_NAME_FAST")
    model_name_precise: str = Field(default="qwen3.5-plus", alias="MODEL_NAME_PRECISE")
    model_name_precise_ocr: str = Field(default="qwen-vl-ocr-latest", alias="MODEL_NAME_PRECISE_OCR")
    precise_max_ocr_pages: int = Field(default=3, alias="PRECISE_MAX_OCR_PAGES")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024

    @property
    def cors_origins_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
