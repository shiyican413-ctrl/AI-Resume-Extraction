import json
import re

import httpx

from app.core.config import get_settings

EDU_ORDER = {"高中": 1, "大专": 2, "本科": 3, "硕士": 4, "博士": 5}

KEYWORD_LIBRARY = [
    "Python", "Java", "Go", "FastAPI", "Django", "Flask", "MySQL", "PostgreSQL", "Redis",
    "Docker", "Kubernetes", "Serverless", "微服务", "消息队列", "Kafka", "RabbitMQ", "NLP",
    "机器学习", "深度学习", "Elasticsearch", "云服务", "阿里云", "AWS", "CI/CD",
]


def _extract_required_years(jd_text: str) -> int:
    match = re.search(r"(\d+)\s*年以上", jd_text)
    return int(match.group(1)) if match else 0


def _extract_resume_years(resume_years_text: str) -> int:
    match = re.search(r"(\d+)", resume_years_text or "")
    return int(match.group(1)) if match else 0


def _extract_required_education(jd_text: str) -> str:
    for level in ["博士", "硕士", "本科", "大专", "高中"]:
        if level in jd_text:
            return level
    return ""


def _extract_jd_keywords(jd_text: str) -> list[str]:
    jd_lower = jd_text.lower()
    keywords = []
    for key in KEYWORD_LIBRARY:
        if key.lower() in jd_lower:
            keywords.append(key)
    return sorted(set(keywords))


def _education_score(candidate_education: str, required_education: str) -> int:
    if not required_education:
        return 80
    candidate = EDU_ORDER.get(candidate_education, 0)
    required = EDU_ORDER.get(required_education, 0)
    return 100 if candidate >= required else max(40, int(100 * (candidate / required)))


def _experience_score(resume_years_text: str, jd_text: str) -> int:
    required = _extract_required_years(jd_text)
    candidate = _extract_resume_years(resume_years_text)
    if required <= 0:
        return 80
    if candidate >= required:
        return 100
    return max(30, int((candidate / required) * 100))


def _skill_score(resume_skills: list[str], jd_keywords: list[str]) -> tuple[int, list[str], list[str]]:
    if not jd_keywords:
        return 80, [], []
    resume_set = {item.lower() for item in resume_skills}
    matched = [key for key in jd_keywords if key.lower() in resume_set]
    missing = [key for key in jd_keywords if key.lower() not in resume_set]
    score = int((len(matched) / len(jd_keywords)) * 100)
    return score, matched, missing


def _summary(total: int, matched: list[str], missing: list[str]) -> str:
    level = "较高" if total >= 80 else "中等" if total >= 60 else "较低"
    matched_text = "、".join(matched[:6]) if matched else "暂无"
    missing_text = "、".join(missing[:6]) if missing else "暂无"
    return (
        f"候选人与岗位匹配度{level}。命中关键词：{matched_text}。"
        f"缺失关键词：{missing_text}。建议结合项目细节进一步面试确认。"
    )


def _extract_json_from_text(raw_text: str) -> dict | None:
    body = raw_text.strip()
    if body.startswith("```"):
        body = re.sub(r"^```(?:json)?", "", body).strip()
        body = body.rstrip("`").strip()
    try:
        return json.loads(body)
    except Exception:
        pass
    match = re.search(r"\{[\s\S]*\}", raw_text)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except Exception:
        return None


def _ai_score(resume_info: dict, jd_text: str, model_name: str | None = None) -> int | None:
    settings = get_settings()
    if not settings.model_api_key:
        return None

    prompt = (
        "你是招聘评估助手。请基于候选人信息和岗位JD给出0-100的匹配分。"
        "只返回JSON，如 {\"ai_score\": 82}。"
    )
    payload = {
        "model": model_name or settings.model_name,
        "messages": [
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": json.dumps(
                    {"resume": resume_info, "jd_text": jd_text},
                    ensure_ascii=False,
                ),
            },
        ],
        "temperature": 0.1,
    }
    headers = {
        "Authorization": f"Bearer {settings.model_api_key}",
        "Content-Type": "application/json",
    }
    url = f"{settings.model_base_url.rstrip('/')}/chat/completions"

    try:
        with httpx.Client(timeout=20.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            raw = resp.json()["choices"][0]["message"]["content"]
            data = _extract_json_from_text(raw)
            if not data:
                return None
            value = int(data.get("ai_score"))
            return min(100, max(0, value))
    except Exception:
        return None


def compute_match(
    resume_extract_result: dict,
    jd_text: str,
    ai_model_name: str | None = None,
) -> dict:
    jd_keywords = _extract_jd_keywords(jd_text)
    skill_score, matched, missing = _skill_score(resume_extract_result.get("skills", []), jd_keywords)
    experience_score = _experience_score(
        resume_extract_result.get("background", {}).get("years_of_experience", ""),
        jd_text,
    )
    education_score = _education_score(
        resume_extract_result.get("background", {}).get("education", ""),
        _extract_required_education(jd_text),
    )

    rule_score = int(skill_score * 0.5 + experience_score * 0.3 + education_score * 0.2)
    ai_score = _ai_score(resume_extract_result, jd_text, model_name=ai_model_name)
    final_ai_score = ai_score if ai_score is not None else rule_score
    total_score = int(rule_score * 0.7 + final_ai_score * 0.3)

    return {
        "score": {
            "total": total_score,
            "skill_score": skill_score,
            "experience_score": experience_score,
            "education_score": education_score,
            "ai_score": final_ai_score,
        },
        "matched_keywords": matched,
        "missing_keywords": missing,
        "summary": _summary(total_score, matched, missing),
        "jd_keywords": jd_keywords,
    }
