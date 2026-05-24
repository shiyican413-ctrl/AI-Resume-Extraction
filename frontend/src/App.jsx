import { useRef, useState } from "react";

import { extractResume, matchResume, saveDebugEnv, uploadResume } from "./api/client";
import ResultPanel from "./components/ResultPanel";

const MODES = [
  { key: "normal", label: "普通模式" },
  { key: "fast", label: "极速模式" },
  { key: "precise", label: "精准模式" },
];

export default function App() {
  const fileInputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [mode, setMode] = useState("normal");
  const [dragging, setDragging] = useState(false);
  const [uploadStatus, setUploadStatus] = useState("idle");
  const [uploadMessage, setUploadMessage] = useState("尚未上传文件");
  const [jdText, setJdText] = useState("");
  const [resumeMeta, setResumeMeta] = useState(null);
  const [extractData, setExtractData] = useState(null);
  const [matchData, setMatchData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [debugKey, setDebugKey] = useState("");
  const [debugSaving, setDebugSaving] = useState(false);
  const [debugMessage, setDebugMessage] = useState("");
  const jdFilled = jdText.trim().length > 0;
  const parseDone = Boolean(extractData);
  const matchDone = Boolean(matchData);

  function resetSelectedFile(status = "idle", message = "尚未上传文件") {
    setFile(null);
    setResumeMeta(null);
    setExtractData(null);
    setMatchData(null);
    setUploadStatus(status);
    setUploadMessage(message);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }

  function readFileFromInput(nextFile) {
    if (!nextFile) {
      return;
    }
    if (nextFile.type && nextFile.type !== "application/pdf") {
      resetSelectedFile("error", "请选择 PDF 格式的简历文件");
      setError("仅支持 PDF 文件");
      return;
    }
    setError("");
    setFile(nextFile);
    setResumeMeta(null);
    setExtractData(null);
    setMatchData(null);
    setUploadStatus("ready");
    setUploadMessage(`已选择文件：${nextFile.name}，点击“开始解析”后上传`);
  }

  function onDrop(event) {
    event.preventDefault();
    setDragging(false);
    const dropped = event.dataTransfer.files?.[0];
    readFileFromInput(dropped || null);
  }

  async function runAnalysis() {
    if (!file) {
      setError("请先选择 PDF 简历文件");
      return;
    }

    setError("");
    setLoading(true);
    setExtractData(null);
    setMatchData(null);
    setUploadStatus("uploading");
    setUploadMessage(`正在上传：${file.name}`);
    let uploadDone = false;

    try {
      const upload = await uploadResume(file);
      uploadDone = true;
      setResumeMeta(upload);
      setUploadStatus("success");
      setUploadMessage(`上传成功：${upload.file_name}`);

      const extract = await extractResume(upload.resume_id, mode);
      setExtractData(extract);

      if (jdText.trim()) {
        const match = await matchResume(upload.resume_id, jdText, mode);
        setMatchData(match);
      }
    } catch (e) {
      if (!uploadDone) {
        setUploadStatus("error");
        setUploadMessage(e.message || "上传失败，请重试");
      }
      setError(e.message || "分析失败");
    } finally {
      setLoading(false);
    }
  }

  async function saveDebugKey() {
    if (!debugKey.trim()) {
      setDebugMessage("请输入模型 API Key");
      return;
    }

    setDebugSaving(true);
    setDebugMessage("");
    try {
      await saveDebugEnv(debugKey);
      setDebugMessage("已生成阿里百炼 .env，后续解析将使用大模型");
    } catch (e) {
      setDebugMessage(e.message || "生成 .env 失败");
    } finally {
      setDebugSaving(false);
    }
  }

  return (
    <div className="landing">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark" aria-hidden="true" />
          <span className="brand-text">AI 赋能-智能简历分析系统</span>
        </div>
        <nav className="topnav">
          <a href="#product">产品</a>
          <a href="#company">公司</a>
          <a href="#docs">开发文档</a>
        </nav>
        <div className="top-actions">
          <label className="debug-key-wrap">
            <span>百炼 Key</span>
            <input
              type="password"
              value={debugKey}
              onChange={(e) => setDebugKey(e.target.value)}
              placeholder="输入阿里百炼 API Key"
              aria-label="阿里百炼 API Key"
            />
          </label>
          <button type="button" className="btn btn-primary" onClick={saveDebugKey} disabled={debugSaving}>
            {debugSaving ? "生成中..." : "生成 env"}
          </button>
        </div>
        {debugMessage ? <div className="debug-message">{debugMessage}</div> : null}
      </header>

      <main className="hero">
        <h1 className="hero-title">简历解析体验</h1>

        <div className="mode-switch" role="tablist" aria-label="解析模式">
          {MODES.map((item) => (
            <button
              key={item.key}
              type="button"
              className={`mode-btn ${mode === item.key ? "active" : ""}`}
              onClick={() => setMode(item.key)}
              aria-selected={mode === item.key}
            >
              {item.label}
            </button>
          ))}
        </div>

        <section className="step-cards" aria-label="流程步骤">
          <article className={`step-card ${uploadStatus === "success" ? "done" : "active"}`}>
            <span className="step-icon" aria-hidden="true">↑</span>
            <h3>上传简历</h3>
            <p>上传您的简历文件</p>
          </article>
          <article className={`step-card ${loading ? "active" : parseDone ? "done" : ""}`}>
            <span className="step-icon" aria-hidden="true">▤</span>
            <h3>解析简历</h3>
            <p>提取简历内容并分析</p>
          </article>
          <article className={`step-card ${parseDone && (!jdFilled || matchDone) ? "done" : ""}`}>
            <span className="step-icon" aria-hidden="true">✓</span>
            <h3>完成导入</h3>
            <p>{jdFilled ? "简历解析与匹配完成" : "简历解析完成，可选做岗位匹配"}</p>
          </article>
        </section>

        <input
          ref={fileInputRef}
          type="file"
          accept="application/pdf"
          className="hidden-file"
          onChange={(e) => readFileFromInput(e.target.files?.[0] || null)}
        />

        <section
          className={`upload-panel ${dragging ? "dragging" : ""}`}
          onClick={() => fileInputRef.current?.click()}
          onDragOver={(e) => {
            e.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={onDrop}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
              e.preventDefault();
              fileInputRef.current?.click();
            }
          }}
        >
          <svg viewBox="0 0 24 24" className="upload-icon" aria-hidden="true">
            <path
              d="M3 8.5a2.5 2.5 0 0 1 2.5-2.5h2.27a1 1 0 0 0 .8-.4l1.35-1.8A1 1 0 0 1 10.72 3h2.56a1 1 0 0 1 .8.4l1.35 1.8a1 1 0 0 0 .8.4h2.27A2.5 2.5 0 0 1 21 8.5v10A2.5 2.5 0 0 1 18.5 21h-13A2.5 2.5 0 0 1 3 18.5v-10Z"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.7"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <path
              d="M8.5 12.5a3.5 3.5 0 0 0 7 0"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.7"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          <p className="upload-main">点击 或 拖拽</p>
          <p className="upload-sub">即可上传简历文件（PDF）</p>
          <p className="upload-file">{file ? `已选择：${file.name}` : "尚未选择文件"}</p>
          <p className={`upload-status ${uploadStatus}`}>{uploadMessage}</p>
        </section>

        <section className="jd-panel">
          <label htmlFor="jd-input">岗位 JD</label>
          <textarea
            id="jd-input"
            placeholder="请输入岗位 JD，例如：3年以上 Python 后端经验，熟悉 FastAPI、Redis、MySQL..."
            value={jdText}
            onChange={(e) => setJdText(e.target.value)}
          />
        </section>

        <button type="button" className="analyze-btn" onClick={runAnalysis} disabled={loading}>
          {loading ? "分析中..." : "开始解析"}
        </button>

        <div className="meta-row">
          <span>模式：{MODES.find((item) => item.key === mode)?.label}</span>
          <span>接口：{import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1"}</span>
        </div>
        {resumeMeta ? (
          <div className="meta-row">
            <span>简历ID：{resumeMeta.resume_id}</span>
            <span>文件名：{resumeMeta.file_name}</span>
          </div>
        ) : null}
        {error ? <div className="error">{error}</div> : null}

        <section className="result-shell">
          <h2>解析结果</h2>
          <ResultPanel extractData={extractData} matchData={matchData} />
        </section>
      </main>
    </div>
  );
}
