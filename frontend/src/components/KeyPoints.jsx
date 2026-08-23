function KeyPoints({
  keyPoints,
  copiedSection,
  onCopy,
  cleanKeyPoint,
}) {
  if (!keyPoints || keyPoints.length === 0) {
    return null;
  }

  return (
    <div className="result-card">
      <div className="result-title-row">
        <div className="result-title">
          <span className="result-icon">
            🔑
          </span>

          <h3>
            Key Points
          </h3>
        </div>

        <button
          type="button"
          className="copy-button"
          onClick={onCopy}
        >
          {copiedSection === "keypoints"
            ? "✓ Copied"
            : "📋 Copy"}
        </button>
      </div>

      <ul className="key-points">
        {keyPoints.map((point, index) => (
          <li key={index}>
            <span className="bullet">
              •
            </span>

            <span className="point-text">
              {cleanKeyPoint(point)}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default KeyPoints;