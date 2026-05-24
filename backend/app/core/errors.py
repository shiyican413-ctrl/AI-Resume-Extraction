from dataclasses import dataclass


@dataclass
class APIError(Exception):
    message: str
    error_code: str
    status_code: int = 400


ERROR_MESSAGES = {
    "INVALID_FILE_TYPE": "文件格式不支持",
    "FILE_TOO_LARGE": "文件过大",
    "PDF_PARSE_FAILED": "PDF 解析失败",
    "RESUME_NOT_FOUND": "简历不存在",
    "EXTRACT_NOT_FOUND": "请先执行简历信息提取",
    "JD_EMPTY": "岗位描述不能为空",
    "AI_SERVICE_ERROR": "AI 模型服务调用失败",
    "INTERNAL_ERROR": "服务内部错误",
}
