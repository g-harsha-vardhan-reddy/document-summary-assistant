function SummaryResult({
  summary,
  copiedSection,
  onCopy,
}) {
  if (!summary) {
    return null;
  }

  return (
    <div className="result-card">
      <div className="result-title-row">

        <div className="result-title">
          <span className="result-icon">
            📝
          </span>

          <h3>
            Summary
          </h3>
        </div>

        <button
          type="button"
          className="copy-button"
          onClick={onCopy}
        >
          {copiedSection === "summary"
            ? "✓ Copied"
            : "📋 Copy"}
        </button>

      </div>

      <div className="summary-text">
        {summary}
      </div>
    </div>
  );
}

export default SummaryResult;