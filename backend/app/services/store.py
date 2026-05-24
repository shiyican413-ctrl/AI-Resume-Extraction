import hashlib
import time
from dataclasses import dataclass


@dataclass
class ResumeRecord:
    resume_id: str
    resume_hash: str
    file_name: str
    content: bytes


class InMemoryStore:
    def __init__(self) -> None:
        self.resume_by_id: dict[str, ResumeRecord] = {}
        self.resume_id_by_hash: dict[str, str] = {}
        self.extract_cache: dict[str, dict] = {}
        self.match_cache: dict[str, dict] = {}

    def put_resume(self, file_name: str, content: bytes) -> ResumeRecord:
        resume_hash = hashlib.sha256(content).hexdigest()
        existing_id = self.resume_id_by_hash.get(resume_hash)
        if existing_id:
            return self.resume_by_id[existing_id]

        resume_id = f"resume_{int(time.time() * 1000)}"
        record = ResumeRecord(
            resume_id=resume_id,
            resume_hash=resume_hash,
            file_name=file_name,
            content=content,
        )
        self.resume_by_id[resume_id] = record
        self.resume_id_by_hash[resume_hash] = resume_id
        return record

    def get_resume(self, resume_id: str) -> ResumeRecord | None:
        return self.resume_by_id.get(resume_id)

    @staticmethod
    def extract_cache_key(resume_hash: str, mode: str) -> str:
        return f"{resume_hash}:{mode}"

    @staticmethod
    def match_cache_key(resume_hash: str, jd_hash: str, mode: str) -> str:
        return f"{resume_hash}:{jd_hash}:{mode}"


store = InMemoryStore()
