import React from "react";

function toDisplayText(value) {
  if (value === null || value === undefined || value === "") {
    return "-";
  }
  if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }
  try {
    return JSON.stringify(value, null, 0);
  } catch {
    return String(value);
  }
}

function normalizeTextArray(value) {
  if (!Array.isArray(value)) {
    return [];
  }
  return value
    .map((item) => toDisplayText(item))
    .filter((item) => item !== "-");
}

function joinTextList(value) {
  if (Array.isArray(value)) {
    return value.map((item) => String(item).trim()).filter(Boolean).join("、");
  }
  return value ? String(value).trim() : "";
}

function formatEducationItem(item) {
  if (!item || typeof item !== "object" || Array.isArray(item)) {
    return toDisplayText(item);
  }

  const parts = [];
  const degree = item.degree || item["学历"] || item.education;
  const school = item.school || item["学校"] || item.university;
  const major = item.major || item["专业"];
  const period = item.period || item["时间"] || item.date;
  const courses = item.major_courses || item["主修课程"] || item.courses;

  [degree, school, major, period].forEach((value) => {
    const text = joinTextList(value);
    if (text) {
      parts.push(text);
    }
  });

  const coursesText = joinTextList(courses);
  if (coursesText) {
    parts.push(`主修：${coursesText}`);
  }

  return parts.length ? parts.join("，") : toDisplayText(item);
}

function formatEducation(value) {
  if (Array.isArray(value)) {
    const items = value.map((item) => formatEducationItem(item)).filter((item) => item !== "-");
    return items.length ? items.join("；") : "-";
  }
  return formatEducationItem(value);
}

export default function ResultPanel({ extractData, matchData }) {
  if (!extractData && !matchData) {
    return <div className="result-empty">上传并开始解析后，这里会展示结构化结果。</div>;
  }

  const skillList = normalizeTextArray(extractData?.skills);
  const matchedKeywords = normalizeTextArray(matchData?.matched_keywords);
  const missingKeywords = normalizeTextArray(matchData?.missing_keywords);

  return (
    <div className="result-content">
      {extractData ? (
        <section className="result-block">
          <h3>信息提取结果</h3>
          <div className="info-grid">
            <div><span>姓名</span><strong>{toDisplayText(extractData.basic_info?.name)}</strong></div>
            <div><span>电话</span><strong>{toDisplayText(extractData.basic_info?.phone)}</strong></div>
            <div><span>邮箱</span><strong>{toDisplayText(extractData.basic_info?.email)}</strong></div>
            <div><span>地址</span><strong>{toDisplayText(extractData.basic_info?.address)}</strong></div>
            <div><span>求职意向</span><strong>{toDisplayText(extractData.job_intention?.position)}</strong></div>
            <div><span>期望薪资</span><strong>{toDisplayText(extractData.job_intention?.expected_salary)}</strong></div>
            <div><span>工作年限</span><strong>{toDisplayText(extractData.background?.years_of_experience)}</strong></div>
            <div><span>学历</span><strong>{formatEducation(extractData.background?.education)}</strong></div>
          </div>
          <p className="cache-note">缓存命中：{extractData.cache_hit ? "是" : "否"}</p>
          <p className="result-label">AI 简短总结</p>
          <p className="summary-text">{toDisplayText(extractData.summary)}</p>
          <p className="result-label">技能关键词</p>
          <div className="keyword-wrap">
            {skillList.length ? (
              skillList.map((skill) => (
                <span key={skill} className="keyword">{skill}</span>
              ))
            ) : (
              <span className="result-tip">暂无识别到技能关键词</span>
            )}
          </div>
        </section>
      ) : null}

      {matchData ? (
        <section className="result-block">
          <h3>岗位匹配结果</h3>
          <p className="score-total">{matchData.score?.total ?? 0}</p>
          <div className="score-grid">
            <div><span>技能分</span><strong>{matchData.score?.skill_score ?? 0}</strong></div>
            <div><span>经验分</span><strong>{matchData.score?.experience_score ?? 0}</strong></div>
            <div><span>学历分</span><strong>{matchData.score?.education_score ?? 0}</strong></div>
            <div><span>AI 分</span><strong>{matchData.score?.ai_score ?? 0}</strong></div>
          </div>
          <p className="result-label">评估总结</p>
          <p className="summary-text">{toDisplayText(matchData.summary)}</p>
          <p className="result-label">命中关键词</p>
          <div className="keyword-wrap">
            {matchedKeywords.length ? (
              matchedKeywords.map((item) => (
                <span key={item} className="keyword">{item}</span>
              ))
            ) : (
              <span className="result-tip">暂无</span>
            )}
          </div>
          <p className="result-label">缺失关键词</p>
          <div className="keyword-wrap">
            {missingKeywords.length ? (
              missingKeywords.map((item) => (
                <span key={item} className="keyword missing">{item}</span>
              ))
            ) : (
              <span className="result-tip">暂无</span>
            )}
          </div>
          <p className="cache-note">缓存命中：{matchData.cache_hit ? "是" : "否"}</p>
        </section>
      ) : (
        <div className="result-tip">填写岗位 JD 后再次解析，即可生成匹配评分。</div>
      )}
    </div>
  );
}
