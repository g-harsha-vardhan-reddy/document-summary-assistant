import { useEffect, useState } from "react";
import "./App.css";

import UploadBox from "./components/UploadBox";
import SummaryResult from "./components/SummaryResult";
import KeyPoints from "./components/KeyPoints";
import ExtractedText from "./components/ExtractedText";
import Suggestions from "./components/Suggestions";

function App() {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState("");

  const [summaryLength, setSummaryLength] =
    useState("medium");

  const [summary, setSummary] = useState("");
  const [keyPoints, setKeyPoints] = useState([]);
  const [extractedText, setExtractedText] =
    useState("");
  const [suggestions, setSuggestions] =
    useState([]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [isDragging, setIsDragging] =
    useState(false);

  const [downloaded, setDownloaded] =
    useState(false);

  const [copiedSection, setCopiedSection] =
    useState("");

  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  const clearResults = () => {
    setSummary("");
    setKeyPoints([]);
    setExtractedText("");
    setSuggestions([]);

    setError("");
    setDownloaded(false);
    setCopiedSection("");
  };

  const isValidFile = (selectedFile) => {
    if (!selectedFile) {
      return false;
    }

    const allowedTypes = [
      "application/pdf",
      "image/png",
      "image/jpeg",
    ];

    const allowedExtensions = [
      ".pdf",
      ".png",
      ".jpg",
      ".jpeg",
    ];

    const fileName =
      selectedFile.name.toLowerCase();

    const validType =
      allowedTypes.includes(
        selectedFile.type
      );

    const validExtension =
      allowedExtensions.some(
        (extension) =>
          fileName.endsWith(extension)
      );

    return validType || validExtension;
  };

  const selectFile = (selectedFile) => {
    if (!selectedFile) {
      return;
    }

    if (!isValidFile(selectedFile)) {
      setError(
        "Please upload a PDF, PNG, JPG, or JPEG file."
      );
      return;
    }

    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }

    const newPreviewUrl =
      URL.createObjectURL(
        selectedFile
      );

    setFile(selectedFile);
    setPreviewUrl(newPreviewUrl);

    clearResults();
  };

  const handleFileChange = (event) => {
    const selectedFile =
      event.target.files[0];

    selectFile(selectedFile);

    event.target.value = "";
  };

  const handleDragEnter = (event) => {
    event.preventDefault();
    event.stopPropagation();

    setIsDragging(true);
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    event.stopPropagation();

    setIsDragging(true);
  };

  const handleDragLeave = (event) => {
    event.preventDefault();
    event.stopPropagation();

    setIsDragging(false);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    event.stopPropagation();

    setIsDragging(false);

    const droppedFile =
      event.dataTransfer.files[0];

    selectFile(droppedFile);
  };

  const handleClearFile = () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }

    setFile(null);
    setPreviewUrl("");

    setSummary("");
    setKeyPoints([]);
    setExtractedText("");
    setSuggestions([]);

    setError("");
    setDownloaded(false);
    setCopiedSection("");
  };

  const handleSummarize = async () => {
    if (!file) {
      setError(
        "Please select a PDF or image first."
      );
      return;
    }

    setLoading(true);
    setError("");

    setDownloaded(false);
    setCopiedSection("");

    setSummary("");
    setKeyPoints([]);
    setExtractedText("");
    setSuggestions([]);

    try {
      const formData =
        new FormData();

      formData.append(
        "file",
        file
      );

      formData.append(
        "length",
        summaryLength
      );

      formData.append(
        "summary_length",
        summaryLength
      );

      const response =
        await fetch(
          "http://127.0.0.1:8000/api/summarize/",
          {
            method: "POST",
            body: formData,
          }
        );

      let data;

      try {
        data =
          await response.json();
      } catch {
        throw new Error(
          "The backend returned an invalid response."
        );
      }

      console.log(
        "Backend response:",
        data
      );

      if (!response.ok) {
        throw new Error(
          data.error ||
          data.detail ||
          "Failed to generate summary."
        );
      }

      setSummary(
        data.summary || ""
      );

      setKeyPoints(
        Array.isArray(
          data.key_points
        )
          ? data.key_points
          : []
      );

      setExtractedText(
        data.extracted_text ||
        data.extracted_data ||
        data.text ||
        ""
      );

      setSuggestions(
        Array.isArray(
          data.suggestions
        )
          ? data.suggestions
          : []
      );

    } catch (err) {
      console.error(
        "Summarization error:",
        err
      );

      setError(
        err.message ||
        "Something went wrong while processing the document."
      );

    } finally {
      setLoading(false);
    }
  };

  const cleanKeyPoint = (value) => {
    let text =
      String(value).trim();

    text = text.replace(
      /\*\*\s*\d+\s*\*\*/g,
      ""
    );

    text = text.replace(
      /\*\*/g,
      ""
    );

    text = text.replace(
      /^\s*\d+\s*[\.\)\:\-]?\s*/,
      ""
    );

    text = text.replace(
      /^\s*[•●▪◦‣\-\*]\s*/,
      ""
    );

    return text.trim();
  };

  const cleanSuggestion = (
    value
  ) => {
    let text =
      String(value).trim();

    text = text.replace(
      /\*\*/g,
      ""
    );

    text = text.replace(
      /^\s*\d+\s*[\.\)\:\-]?\s*/,
      ""
    );

    text = text.replace(
      /^\s*[•●▪◦‣\-\*]\s*/,
      ""
    );

    return text.trim();
  };

  const formatKeyPoints = () => {
    return keyPoints
      .map(
        (point, index) =>
          `${index + 1}. ${cleanKeyPoint(
            point
          )}`
      )
      .join("\n");
  };

  const formatSuggestions = () => {
    return suggestions
      .map(
        (suggestion, index) =>
          `${index + 1}. ${cleanSuggestion(
            suggestion
          )}`
      )
      .join("\n");
  };

  const copyToClipboard = async (
    text,
    section
  ) => {
    if (!text) {
      return;
    }

    try {
      await navigator.clipboard.writeText(
        text
      );

      setCopiedSection(
        section
      );

      setTimeout(() => {
        setCopiedSection("");
      }, 2000);

    } catch (err) {
      console.error(
        "Copy failed:",
        err
      );

      setError(
        "Unable to copy this content."
      );
    }
  };

  const handleCopySummary = () => {
    copyToClipboard(
      summary,
      "summary"
    );
  };

  const handleCopyKeyPoints = () => {
    copyToClipboard(
      formatKeyPoints(),
      "keypoints"
    );
  };

  const handleCopyExtractedText =
    () => {
      copyToClipboard(
        extractedText,
        "extracted"
      );
    };

  const handleCopySuggestions = () => {
    copyToClipboard(
      formatSuggestions(),
      "suggestions"
    );
  };

  const hasResults =
    Boolean(summary) ||
    keyPoints.length > 0 ||
    Boolean(extractedText) ||
    suggestions.length > 0;

  const handleDownload = () => {
    if (!hasResults) {
      return;
    }

    const documentName =
      file
        ? file.name
        : "document";

    const baseName =
      documentName.replace(
        /\.[^/.]+$/,
        ""
      );

    const content = `
DOCUMENT SUMMARY ASSISTANT
==========================

Document:
${documentName}

Summary Length:
${summaryLength}

----------------------------------------
SUMMARY
----------------------------------------

${summary || "No summary available."}

----------------------------------------
KEY POINTS
----------------------------------------

${
  keyPoints.length > 0
    ? formatKeyPoints()
    : "No key points available."
}

----------------------------------------
EXTRACTED TEXT
----------------------------------------

${
  extractedText ||
  "No extracted text available."
}

----------------------------------------
SUGGESTIONS
----------------------------------------

${
  suggestions.length > 0
    ? formatSuggestions()
    : "No suggestions available."
}

----------------------------------------
Generated by Document Summary Assistant
`;

    const blob =
      new Blob(
        [content],
        {
          type:
            "text/plain;charset=utf-8",
        }
      );

    const url =
      URL.createObjectURL(
        blob
      );

    const link =
      document.createElement(
        "a"
      );

    link.href = url;

    link.download =
      `${baseName}_summary.txt`;

    document.body.appendChild(
      link
    );

    link.click();

    document.body.removeChild(
      link
    );

    URL.revokeObjectURL(
      url
    );

    setDownloaded(true);
  };

  return (
    <div className="app">
      <div className="container">

        <header className="header">

          <div className="logo-icon">
            📚
          </div>

          <h1>
            Document Summary Assistant
          </h1>

          <p>
            Upload any document and get a smart
            summary, key points, extracted text,
            and suggestions.
          </p>

        </header>

        <UploadBox
          file={file}
          previewUrl={previewUrl}
          isDragging={isDragging}
          loading={loading}
          onFileChange={
            handleFileChange
          }
          onDragEnter={
            handleDragEnter
          }
          onDragOver={
            handleDragOver
          }
          onDragLeave={
            handleDragLeave
          }
          onDrop={handleDrop}
          onClearFile={
            handleClearFile
          }
        />

        <section className="length-section">

          <h2>
            Summary Length
          </h2>

          <div className="length-buttons">

            <button
              type="button"
              className={
                summaryLength ===
                "short"
                  ? "active"
                  : ""
              }
              onClick={() =>
                setSummaryLength(
                  "short"
                )
              }
              disabled={loading}
            >
              Short
            </button>

            <button
              type="button"
              className={
                summaryLength ===
                "medium"
                  ? "active"
                  : ""
              }
              onClick={() =>
                setSummaryLength(
                  "medium"
                )
              }
              disabled={loading}
            >
              Medium
            </button>

            <button
              type="button"
              className={
                summaryLength ===
                "long"
                  ? "active"
                  : ""
              }
              onClick={() =>
                setSummaryLength(
                  "long"
                )
              }
              disabled={loading}
            >
              Long
            </button>

          </div>

        </section>

        {error && (
          <div className="error-box">

            <span>
              ⚠️
            </span>

            <span>
              {error}
            </span>

          </div>
        )}

        <button
          type="button"
          className="summarize-button"
          onClick={
            handleSummarize
          }
          disabled={loading}
        >
          {loading ? (
            <>
              <span className="spinner"></span>
              Processing Document...
            </>
          ) : (
            "✨ Summarize Document"
          )}
        </button>

        {hasResults && (
          <button
            type="button"
            className="download-button"
            onClick={
              handleDownload
            }
          >
            ⬇️ Download Results
          </button>
        )}

        {downloaded && (
          <div className="download-success">
            ✅ Results downloaded successfully.
          </div>
        )}

        {hasResults && (
          <section className="results">

            <div className="results-header">

              <h2>
                Document Results
              </h2>

              {file && (
                <p>
                  Results for{" "}
                  <strong>
                    {file.name}
                  </strong>
                </p>
              )}

            </div>

            <SummaryResult
              summary={summary}
              copiedSection={
                copiedSection
              }
              onCopy={
                handleCopySummary
              }
            />

            <KeyPoints
              keyPoints={
                keyPoints
              }
              copiedSection={
                copiedSection
              }
              onCopy={
                handleCopyKeyPoints
              }
              cleanKeyPoint={
                cleanKeyPoint
              }
            />

            <ExtractedText
              extractedText={
                extractedText
              }
              copiedSection={
                copiedSection
              }
              onCopy={
                handleCopyExtractedText
              }
            />

            <Suggestions
              suggestions={
                suggestions
              }
              copiedSection={
                copiedSection
              }
              onCopy={
                handleCopySuggestions
              }
              cleanSuggestion={
                cleanSuggestion
              }
            />

          </section>
        )}

      </div>
    </div>
  );
}

export default App;