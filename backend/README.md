# AI Resume Analyzer Backend

## Run

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Env

Copy `.env.example` to `.env` and fill optional model key.

```bash
DASHSCOPE_API_KEY=
MODEL_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
MODEL_NAME=qwen-plus
MODEL_NAME_FAST=qwen3.5-flash
MODEL_NAME_PRECISE=qwen3.5-plus
MODEL_NAME_PRECISE_OCR=qwen-vl-ocr-latest
PRECISE_MAX_OCR_PAGES=3
MAX_FILE_SIZE_MB=10
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Without `DASHSCOPE_API_KEY`, the system still works with rule-based extraction and scoring.

