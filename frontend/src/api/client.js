const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, options);
  const rawText = await response.text();

  let data = null;
  if (rawText) {
    try {
      data = JSON.parse(rawText);
    } catch {
      data = null;
    }
  }

  if (!response.ok) {
    const message = data?.message || `请求失败（HTTP ${response.status}）`;
    throw new Error(message);
  }

  if (!data || data.success !== true) {
    throw new Error(data?.message || "请求失败");
  }

  return data.data;
}

export async function uploadResume(file) {
  const formData = new FormData();
  formData.append("file", file);
  return request("/resumes/upload", {
    method: "POST",
    body: formData,
  });
}

export async function extractResume(resumeId, mode = "normal") {
  return request(`/resumes/${resumeId}/extract?mode=${encodeURIComponent(mode)}`, { method: "POST" });
}

export async function matchResume(resumeId, jdText, mode = "normal") {
  return request("/match", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resume_id: resumeId, jd_text: jdText, mode }),
  });
}

export async function saveDebugEnv(apiKey) {
  return request("/debug/env", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ api_key: apiKey }),
  });
}
