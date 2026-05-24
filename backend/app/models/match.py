from pydantic import BaseModel


class MatchRequest(BaseModel):
    resume_id: str
    jd_text: str
    mode: str = "normal"
