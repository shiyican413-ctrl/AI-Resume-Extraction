from fastapi import APIRouter, File, Query, UploadFile

from app.core.config import get_settings
from app.core.errors import APIError
from app.core.response import success_response
from app.services.extractor import build_resume_summary, enrich_with_ai, extract_regex_info, merge_extract_result, ocr_pdf_text
from app.services.model_mode import extract_model_for_mode, normalize_mode, ocr_model_for_mode
from app.services.pdf_parser import parse_pdf_text
from app.services.store import store
from app.services.text_cleaner import clean_text

router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)) -> dict:
    settings = get_settings()

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise APIError("文件格式不支持", "INVALID_FILE_TYPE", 400)

    content = await file.read()
    if len(content) > settings.max_file_size_bytes:
        raise APIError("文件过大", "FILE_TOO_LARGE", 400)

    record = store.put_resume(file.filename, content)
    return success_response(
        {
            "resume_id": record.resume_id,
            "resume_hash": record.resume_hash,
            "file_name": record.file_name,
        },
        message="上传成功",
    )


@router.post("/{resume_id}/extract")
def extract_resume(resume_id: str, mode: str = Query(default="normal")) -> dict:
    settings = get_settings()
    record = store.get_resume(resume_id)
    if not record:
        raise APIError("简历不存在", "RESUME_NOT_FOUND", 404)

    normalized_mode = normalize_mode(mode)
    cache_key = store.extract_cache_key(record.resume_hash, normalized_mode)
    if cache_key in store.extract_cache:
        cached = store.extract_cache[cache_key]
        cached_data = dict(cached)
        if not cached_data.get("summary"):
            cached_data["summary"] = build_resume_summary(cached_data)
            store.extract_cache[cache_key] = {**cached, "summary": cached_data["summary"]}
        cached_data["cache_hit"] = True
        return success_response(cached_data, message="解析成功")

    try:
        raw_text = parse_pdf_text(record.content)
    except Exception:
        raise APIError("PDF 解析失败", "PDF_PARSE_FAILED", 400)

    if not raw_text.strip():
        raise APIError("PDF 解析失败", "PDF_PARSE_FAILED", 400)

    ocr_text = ""
    ocr_model = ocr_model_for_mode(normalized_mode)
    if ocr_model:
        ocr_text = ocr_pdf_text(
            record.content,
            model_name=ocr_model,
            max_pages=max(1, settings.precise_max_ocr_pages),
        )

    combined_text = "\n\n".join([item for item in [raw_text, ocr_text] if item.strip()])
    cleaned = clean_text(combined_text or raw_text)
    base_result = extract_regex_info(cleaned)
    ai_result = enrich_with_ai(cleaned, model_name=extract_model_for_mode(normalized_mode))
    merged = merge_extract_result(base_result, ai_result)

    payload = {
        "resume_id": resume_id,
        "mode": normalized_mode,
        "cache_hit": False,
        **merged,
    }
    store.extract_cache[cache_key] = payload

    return success_response(payload, message="解析成功")
