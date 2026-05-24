import base64
from io import BytesIO
import json
import re

import httpx
import pypdfium2 as pdfium

from app.core.config import get_settings

SKILL_LIBRARY = [
    "Python", "Java", "Go", "C++", "JavaScript", "TypeScript", "FastAPI", "Django", "Flask",
    "Spring", "MySQL", "PostgreSQL", "Redis", "MongoDB", "Docker", "Kubernetes", "Linux",
    "Git", "CI/CD", "NLP", "机器学习", "深度学习", "Serverless", "阿里云", "AWS", "Azure",
    "微服务", "消息队列", "Kafka", "RabbitMQ", "Elasticsearch",
]

EDU_LEVELS = ["博士", "硕士", "本科", "大专", "高中"]


def _extract_name(text: str) -> str:
    patterns = [
        r"姓名[:：\s]+([\u4e00-\u9fa5]{2,4})",
        r"Name[:：\s]+([A-Za-z\s]{2,40})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    return ""


def _extract_phone(text: str) -> str:
    match = re.search(r"(?<!\d)(1[3-9]\d{9})(?!\d)", text)
    return match.group(1) if match else ""


def _extract_email(text: str) -> str:
    match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    return match.group(0) if match else ""


def _extract_address(text: str) -> str:
    match = re.search(r"(?:地址|现居地|居住地)[:：\s]+([^\n]{2,30})", text)
    return match.group(1).strip() if match else ""


def _extract_position(text: str) -> str:
    match = re.search(r"(?:求职意向|应聘岗位|目标岗位)[:：\s]+([^\n]{2,50})", text)
    return match.group(1).strip() if match else ""


def _extract_salary(text: str) -> str:
    match = re.search(r"(?:期望薪资|薪资期望)[:：\s]+([^\n]{2,30})", text)
    return match.group(1).strip() if match else ""


def _extract_years(text: str) -> str:
    matches = re.findall(r"(\d+)\s*年", text)
    if not matches:
        return ""
    max_year = max(int(item) for item in matches)
    return f"{max_year}年"


def _extract_education(text: str) -> str:
    for level in EDU_LEVELS:
        if level in text:
            return level
    return ""


def _extract_projects(text: str) -> list[dict]:
    match = re.search(r"(?:项目经历|项目经验)([\s\S]{0,1200})", text)
    if not match:
        return []
    block = match.group(1)
    lines = [line.strip(" -•\t") for line in block.splitlines() if line.strip()]
    projects = []
    for idx, line in enumerate(lines[:6]):
        if len(line) < 4:
            continue
        projects.append({
            "name": line[:30],
            "description": lines[idx + 1][:120] if idx + 1 < len(lines) else "",
        })
        if len(projects) >= 3:
            break
    return projects


def _extract_skills(text: str) -> list[str]:
    text_lower = text.lower()
    found: list[str] = []
    for skill in SKILL_LIBRARY:
        if skill.lower() in text_lower:
            found.append(skill)
    return sorted(set(found))


def extract_regex_info(text: str) -> dict:
    return {
        "basic_info": {
            "name": _extract_name(text),
            "phone": _extract_phone(text),
            "email": _extract_email(text),
            "address": _extract_address(text),
        },
        "job_intention": {
            "position": _extract_position(text),
            "expected_salary": _extract_salary(text),
        },
        "background": {
            "years_of_experience": _extract_years(text),
            "education": _extract_education(text),
            "projects": _extract_projects(text),
        },
        "skills": _extract_skills(text),
    }


def _extract_json_from_text(raw_text: str) -> dict | None:
    candidate = raw_text.strip()
    if candidate.startswith("```"):
        candidate = re.sub(r"^```(?:json)?", "", candidate).strip()
        candidate = candidate.rstrip("`").strip()

    try:
        return json.loads(candidate)
    except Exception:
        pass

    match = re.search(r"\{[\s\S]*\}", raw_text)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except Exception:
        return None


def _chat_completion_json(
    model: str,
    messages: list[dict],
    temperature: float = 0.1,
    timeout: float = 30.0,
) -> dict | None:
    settings = get_settings()
    if not settings.model_api_key:
        return None

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }
    headers = {
        "Authorization": f"Bearer {settings.model_api_key}",
        "Content-Type": "application/json",
    }
    url = f"{settings.model_base_url.rstrip('/')}/chat/completions"

    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            raw = resp.json()["choices"][0]["message"]["content"]
            return _extract_json_from_text(raw)
    except Exception:
        return None


def enrich_with_ai(text: str, model_name: str | None = None) -> dict | None:
    settings = get_settings()
    prompt = (
        "你是简历信息抽取助手。请从简历文本提取字段，并严格返回 JSON，不要返回解释。"
        "JSON 字段必须包含：basic_info, job_intention, background, skills。"
        "其中 background.projects 必须是数组，每项包含 name 和 description。"
    )
    model = model_name or settings.model_name
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": text[:12000]},
    ]
    return _chat_completion_json(model=model, messages=messages)


def _ocr_page_text(page_png: bytes, model_name: str) -> str:
    base64_image = base64.b64encode(page_png).decode("utf-8")
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                    "min_pixels": 32 * 32 * 3,
                    "max_pixels": 2048 * 2048,
                },
                {
                    "type": "text",
                    "text": "请完整提取图片中的简历文字，保持段落与顺序，不要解释。",
                },
            ],
        }
    ]
    settings = get_settings()
    if not settings.model_api_key:
        return ""

    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": 0.01,
    }
    headers = {
        "Authorization": f"Bearer {settings.model_api_key}",
        "Content-Type": "application/json",
    }
    url = f"{settings.model_base_url.rstrip('/')}/chat/completions"

    try:
        with httpx.Client(timeout=45.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            return str(resp.json()["choices"][0]["message"]["content"] or "").strip()
    except Exception:
        return ""


def ocr_pdf_text(content: bytes, model_name: str, max_pages: int = 3) -> str:
    pages_text: list[str] = []
    try:
        pdf = pdfium.PdfDocument(content)
    except Exception:
        return ""

    page_count = min(len(pdf), max_pages)
    for idx in range(page_count):
        try:
            page = pdf[idx]
            bitmap = page.render(scale=2.0)
            pil_image = bitmap.to_pil()
            buf = BytesIO()
            pil_image.save(buf, format="PNG")
            page_text = _ocr_page_text(buf.getvalue(), model_name=model_name)
            if page_text:
                pages_text.append(page_text)
        except Exception:
            continue
    return "\n\n".join(pages_text).strip()


def merge_extract_result(base: dict, ai_result: dict | None) -> dict:
    if not ai_result:
        return base

    merged = json.loads(json.dumps(base, ensure_ascii=False))

    for key in ["basic_info", "job_intention", "background"]:
        if key in ai_result and isinstance(ai_result[key], dict):
            merged[key].update({k: v for k, v in ai_result[key].items() if v})

    ai_skills = ai_result.get("skills") if isinstance(ai_result.get("skills"), list) else []
    merged["skills"] = sorted(set(merged.get("skills", []) + [str(item) for item in ai_skills]))

    if not isinstance(merged["background"].get("projects"), list):
        merged["background"]["projects"] = []

    return merged
