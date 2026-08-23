function UploadBox({
  file,
  previewUrl,
  isDragging,
  loading,
  onFileChange,
  onDragEnter,
  onDragOver,
  onDragLeave,
  onDrop,
  onClearFile,
}) {
  return (
    <section
      className={`upload-card ${
        isDragging ? "dragging" : ""
      }`}
      onDragEnter={onDragEnter}
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onDrop={onDrop}
    >
      <div className="upload-icon">
        📄
      </div>

      <h2>
        Upload Your Document
      </h2>

      <p className="drop-text">
        Drag & drop your document here
      </p>

      <p className="or-text">
        or
      </p>

      <label
        htmlFor="file-upload"
        className="file-button"
      >
        Choose File
      </label>

      <input
        id="file-upload"
        type="file"
        accept=".pdf,.png,.jpg,.jpeg"
        onChange={onFileChange}
      />

      <p className="supported">
        Supported formats: PDF, PNG, JPG, JPEG
      </p>

      {file && (
        <div className="selected-file">
          <span className="file-label">
            SELECTED DOCUMENT
          </span>

          <span className="file-name">
            📄 {file.name}
          </span>

          <span className="file-size">
            {(file.size / 1024 / 1024).toFixed(2)} MB
          </span>

          <button
            type="button"
            className="clear-file-button"
            onClick={onClearFile}
            disabled={loading}
          >
            ✕ Remove Document
          </button>
        </div>
      )}

      {file && previewUrl && (
        <div className="preview-container">
          <div className="preview-header">
            <h3>
              Document Preview
            </h3>
          </div>

          <div className="preview-content">
            {file.type === "application/pdf" ? (
              <iframe
                src={previewUrl}
                title="PDF Preview"
                className="pdf-preview"
              />
            ) : (
              <img
                src={previewUrl}
                alt="Document Preview"
                className="image-preview"
              />
            )}
          </div>
        </div>
      )}
    </section>
  );
}

export default UploadBox;