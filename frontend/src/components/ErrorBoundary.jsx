import React from "react";

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, errorMessage: "" };
  }

  static getDerivedStateFromError(error) {
    return {
      hasError: true,
      errorMessage: error?.message || "页面渲染异常",
    };
  }

  componentDidCatch(error) {
    // Keep a trace in console for local debugging.
    console.error("Render error:", error);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div
          style={{
            minHeight: "100vh",
            display: "grid",
            placeItems: "center",
            padding: "24px",
            background: "#f8fafc",
            color: "#25314d",
            fontFamily: '"Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif',
          }}
        >
          <div style={{ maxWidth: "560px", textAlign: "center" }}>
            <h2 style={{ marginTop: 0 }}>页面出现异常</h2>
            <p style={{ color: "#6c7a94" }}>
              {this.state.errorMessage}
            </p>
            <button
              type="button"
              onClick={() => window.location.reload()}
              style={{
                border: 0,
                borderRadius: "8px",
                background: "#5f6fe8",
                color: "#fff",
                fontSize: "14px",
                fontWeight: 700,
                padding: "10px 16px",
                cursor: "pointer",
              }}
            >
              刷新页面
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
