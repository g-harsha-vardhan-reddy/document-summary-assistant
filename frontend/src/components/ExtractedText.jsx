function ExtractedText({
  extractedText,
  copiedSection,
  onCopy,
}) {
  if (!extractedText) {
    return null;
  }

  return (
    <div className="result-card">
      <div className="result-title-row">
        <div className="result-title">
          <span className="result-icon">
            📚
          </span>

          <h3>
            Extracted Text
          </h3>
        </div>

        <button
          type="button"
          className="copy-button"
          onClick={onCopy}
        >
          {copiedSection === "extracted"
            ? "✓ Copied"
            : "📋 Copy"}
        </button>
      </div>

      <div className="extracted-text">
        {extractedText}
      </div>
    </div>
  );
}

export default ExtractedText;