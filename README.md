# AI 赋能的智能简历分析系统

本项目是一个面向招聘场景的智能简历分析系统，支持上传 PDF 简历，自动解析文本内容，提取候选人关键信息，并结合岗位 JD 计算简历与岗位的匹配度评分。

项目目标是在阿里云 Serverless 环境下完成一个可在线演示的后端服务，并提供简洁可用的前端页面，帮助招聘者快速完成简历初筛。

## 核心功能

- PDF 简历上传与多页文本解析
- 简历文本清洗、分段与结构化处理
- 基本信息提取：姓名、电话、邮箱、地址
- 扩展信息提取：求职意向、期望薪资、工作年限、学历背景、项目经历
- 岗位 JD 关键词提取与能力要求分析
- 简历与岗位需求匹配评分
- JSON 格式返回结构化分析结果
- 缓存已解析简历与评分结果，减少重复计算
- 前端页面支持上传简历、输入 JD、查看分析报告

## 技术选型

| 模块 | 技术 |
| --- | --- |
| 后端框架 | Python + FastAPI |
| 运行环境 | 阿里云函数计算 FC |
| API 暴露 | 阿里云 API 网关 / FC HTTP 触发器 |
| PDF 解析 | PyMuPDF，pdfplumber 作为兜底 |
| AI 模型 | 阿里云 DashScope 通义千问 / 兼容 OpenAI API 的大模型 |
| 缓存 | Redis / 阿里云 Tair |
| 文件存储 | 阿里云 OSS，可选 |
| 前端 | React + Vite |
| 前端部署 | GitHub Pages |

## 项目结构

```text
resume-ai-analyzer/
├── backend/
│   ├── app/
│   │   ├── api/                 # RESTful API 路由
│   │   ├── core/                # 配置、日志、异常处理
│   │   ├── models/              # Pydantic 数据模型
│   │   ├── services/            # PDF 解析、AI 抽取、匹配评分、缓存
│   │   └── main.py              # FastAPI 应用入口
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── src/
│   ├── package.json
│   └── README.md
├── docs/
│   ├── 系统架构设计.md
│   ├── 功能清单.md
│   ├── API接口文档.md
│   ├── 部署说明.md
│   └── 现场演示脚本.md
└── README.md
```

## 快速开始

后端本地运行：

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

前端本地运行：

```bash
cd frontend
npm install
npm run dev
```

## 环境变量

```bash
DASHSCOPE_API_KEY=你的模型服务密钥
REDIS_URL=redis://localhost:6379/0
OSS_ACCESS_KEY_ID=你的 OSS AccessKey
OSS_ACCESS_KEY_SECRET=你的 OSS Secret
OSS_BUCKET=resume-ai-analyzer
OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
```

## 文档导航

- [系统架构设计](docs/系统架构设计.md)
- [功能清单](docs/功能清单.md)
- [API 接口文档](docs/API接口文档.md)
- [部署说明](docs/部署说明.md)
- [现场演示脚本](docs/现场演示脚本.md)

## 提交信息

- GitHub 仓库地址：https://github.com/shiyican413-ctrl/AI-Resume-Extraction
- 线上演示地址：待补充
- 作者姓名：待补充
- 联系方式：待补充
