function Suggestions({
  suggestions,
  copiedSection,
  onCopy,
  cleanSuggestion,
}) {
  if (!suggestions || suggestions.length === 0) {
    return null;
  }

  return (
    <div className="result-card">
      <div className="result-title-row">
        <div className="result-title">
          <span className="result-icon">
            💡
          </span>

          <h3>
            Suggestions
          </h3>
        </div>

        <button
          type="button"
          className="copy-button"
          onClick={onCopy}
        >
          {copiedSection === "suggestions"
            ? "✓ Copied"
            : "📋 Copy"}
        </button>
      </div>

      <div className="suggestions">
        {suggestions.map((suggestion, index) => (
          <div
            className="suggestion-item"
            key={index}
          >
            <span className="suggestion-number">
              {index + 1}
            </span>

            <span className="suggestion-text">
              {cleanSuggestion(suggestion)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Suggestions;
