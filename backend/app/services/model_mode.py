from app.core.config import get_settings

ALLOWED_MODES = {"normal", "fast", "precise"}


def normalize_mode(mode: str | None) -> str:
    if not mode:
        return "normal"
    value = mode.strip().lower()
    return value if value in ALLOWED_MODES else "normal"


def extract_model_for_mode(mode: str) -> str:
    settings = get_settings()
    if mode == "fast":
        return settings.model_name_fast
    if mode == "precise":
        return settings.model_name_precise
    return settings.model_name


def match_model_for_mode(mode: str) -> str:
    return extract_model_for_mode(mode)


def ocr_model_for_mode(mode: str) -> str | None:
    settings = get_settings()
    if mode == "precise":
        return settings.model_name_precise_ocr
    return None
