from pydantic import BaseModel


class UploadResult(BaseModel):
    resume_id: str
    resume_hash: str
    file_name: str


class ProjectItem(BaseModel):
    name: str = ""
    description: str = ""


class ExtractResult(BaseModel):
    resume_id: str
    cache_hit: bool
    basic_info: dict
    job_intention: dict
    background: dict
    skills: list[str]


class MatchResult(BaseModel):
    resume_id: str
    cache_hit: bool
    score: dict
    matched_keywords: list[str]
    missing_keywords: list[str]
    summary: str
