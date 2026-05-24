from fastapi.testclient import TestClient

from app.main import app
from app.services.store import store


client = TestClient(app)


def test_match_requires_extract_before_scoring():
    record = store.put_resume("resume.pdf", b"%PDF-1.4 fake")

    response = client.post(
        "/api/v1/match",
        json={
            "resume_id": record.resume_id,
            "jd_text": "Python 后端开发",
            "mode": "normal",
        },
    )

    assert response.status_code == 400
    assert response.json()["error_code"] == "EXTRACT_NOT_FOUND"


def test_invalid_upload_clearly_reports_file_type_error():
    response = client.post(
        "/api/v1/resumes/upload",
        files={"file": ("resume.txt", b"plain text", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["error_code"] == "INVALID_FILE_TYPE"
