# API 接口文档

## 1. 通用约定

基础路径：

```text
/api/v1
```

统一响应格式：

```json
{
  "success": true,
  "message": "ok",
  "data": {}
}
```

错误响应格式：

```json
{
  "success": false,
  "message": "文件格式不支持",
  "error_code": "INVALID_FILE_TYPE"
}
```

## 2. 健康检查

### GET /health

用于检查后端服务是否正常运行。

响应示例：

```json
{
  "success": true,
  "message": "ok",
  "data": {
    "status": "healthy"
  }
}
```

## 3. 上传简历

### POST /resumes/upload

上传单个 PDF 简历文件，并返回简历 ID。

请求类型：

```text
multipart/form-data
```

请求参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| file | File | 是 | PDF 简历文件 |

响应示例：

```json
{
  "success": true,
  "message": "上传成功",
  "data": {
    "resume_id": "resume_202405240001",
    "resume_hash": "f3b9a1...",
    "file_name": "张三_后端开发.pdf"
  }
}
```

## 4. 提取简历信息

### POST /resumes/{resume_id}/extract

解析指定简历文本，并使用 AI 提取结构化信息。

响应示例：

```json
{
  "success": true,
  "message": "解析成功",
  "data": {
    "resume_id": "resume_202405240001",
    "cache_hit": false,
    "basic_info": {
      "name": "张三",
      "phone": "13800138000",
      "email": "zhangsan@example.com",
      "address": "杭州市"
    },
    "job_intention": {
      "position": "Python 后端开发工程师",
      "expected_salary": "20k-30k"
    },
    "background": {
      "years_of_experience": "3年",
      "education": "本科，计算机科学与技术",
      "projects": [
        {
          "name": "智能招聘系统",
          "description": "负责简历解析、岗位匹配和评分模块开发"
        }
      ]
    },
    "skills": ["Python", "FastAPI", "Redis", "MySQL", "Serverless"]
  }
}
```

## 5. 简历与岗位匹配

### POST /match

输入简历 ID 和岗位 JD，返回匹配评分。

请求示例：

```json
{
  "resume_id": "resume_202405240001",
  "jd_text": "岗位要求：3年以上 Python 后端开发经验，熟悉 FastAPI、Redis、MySQL，有云服务部署经验。"
}
```

响应示例：

```json
{
  "success": true,
  "message": "匹配完成",
  "data": {
    "resume_id": "resume_202405240001",
    "cache_hit": false,
    "score": {
      "total": 86,
      "skill_score": 90,
      "experience_score": 85,
      "education_score": 80,
      "ai_score": 84
    },
    "matched_keywords": ["Python", "FastAPI", "Redis", "云服务部署"],
    "missing_keywords": ["MySQL"],
    "summary": "候选人与岗位匹配度较高，后端开发经验和技术栈较符合 JD 要求。建议进一步确认数据库项目经验深度。"
  }
}
```

## 6. 获取结果

### GET /results/{task_id}

用于获取异步任务结果。MVP 版本可以先不实现异步任务，此接口作为扩展预留。

响应示例：

```json
{
  "success": true,
  "message": "ok",
  "data": {
    "task_id": "task_202405240001",
    "status": "finished",
    "result": {}
  }
}
```

## 7. 错误码

| 错误码 | 说明 |
| --- | --- |
| INVALID_FILE_TYPE | 文件格式不支持 |
| FILE_TOO_LARGE | 文件过大 |
| PDF_PARSE_FAILED | PDF 解析失败 |
| RESUME_NOT_FOUND | 简历不存在 |
| JD_EMPTY | 岗位描述不能为空 |
| AI_SERVICE_ERROR | AI 模型服务调用失败 |
| INTERNAL_ERROR | 服务内部错误 |

