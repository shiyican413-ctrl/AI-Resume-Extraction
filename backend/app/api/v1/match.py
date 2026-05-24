import hashlib

from fastapi import APIRouter

from app.core.errors import APIError
from app.core.response import success_response
from app.models.match import MatchRequest
from app.services.matcher import compute_match
from app.services.model_mode import match_model_for_mode, normalize_mode
from app.services.store import store

router = APIRouter(tags=["match"])


@router.post("/match")
def match_resume(request: MatchRequest) -> dict:
    if not request.jd_text.strip():
        raise APIError("岗位描述不能为空", "JD_EMPTY", 400)

    record = store.get_resume(request.resume_id)
    if not record:
        raise APIError("简历不存在", "RESUME_NOT_FOUND", 404)

    normalized_mode = normalize_mode(request.mode)
    extract_key = store.extract_cache_key(record.resume_hash, normalized_mode)
    extract_result = store.extract_cache.get(extract_key)
    if not extract_result:
        raise APIError("请先执行简历信息提取", "RESUME_NOT_FOUND", 400)

    jd_hash = hashlib.sha256(request.jd_text.strip().encode("utf-8")).hexdigest()
    cache_key = store.match_cache_key(record.resume_hash, jd_hash, normalized_mode)

    if cache_key in store.match_cache:
        cached = dict(store.match_cache[cache_key])
        cached["cache_hit"] = True
        return success_response(cached, message="匹配完成")

    score_result = compute_match(
        extract_result,
        request.jd_text,
        ai_model_name=match_model_for_mode(normalized_mode),
    )
    payload = {
        "resume_id": request.resume_id,
        "mode": normalized_mode,
        "cache_hit": False,
        **score_result,
    }
    store.match_cache[cache_key] = payload
    return success_response(payload, message="匹配完成")
