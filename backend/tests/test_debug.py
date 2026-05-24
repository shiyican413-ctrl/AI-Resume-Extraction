from fastapi.testclient import TestClient

from app.api.v1 import debug
from app.main import app


client = TestClient(app)


def test_save_debug_env_writes_env_file(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    monkeypatch.setattr(debug, "ENV_FILE_PATH", env_file)

    response = client.post("/api/v1/debug/env", json={"api_key": "sk-test-key"})

    assert response.status_code == 200
    assert response.json()["data"]["configured"] is True
    assert response.json()["data"]["provider"] == "aliyun-bailian"
    env_text = env_file.read_text(encoding="utf-8")
    assert "DASHSCOPE_API_KEY=sk-test-key" in env_text
    assert "MODEL_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1" in env_text
    assert "MODEL_NAME=qwen-plus" in env_text


def test_save_debug_env_requires_key():
    response = client.post("/api/v1/debug/env", json={"api_key": " "})

    assert response.status_code == 400
    assert response.json()["message"] == "请输入模型 API Key"
