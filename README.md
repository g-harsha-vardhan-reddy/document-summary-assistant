# Document Summary Assistant

A full-stack web application that allows users to upload PDF or image documents and automatically generate intelligent summaries.

The application extracts text directly from selectable-text PDFs and uses OCR for scanned PDFs and image documents. It then generates summaries, key points, extracted text, and suggestions through a simple React-based interface.

---

## Features

- Upload PDF documents
- Upload PNG, JPG, and JPEG images
- Drag-and-drop document upload
- PDF and image preview
- Direct text extraction from selectable PDFs
- OCR processing for scanned PDFs and images
- Short, medium, and long summaries
- Key point extraction
- Extracted text display
- Improvement suggestions
- Copy summary, key points, extracted text, and suggestions
- Download generated results as a text file
- Remove and replace uploaded documents
- Responsive frontend
- Django REST API backend

---

## System Architecture

```text
                    USER
                      |
                      v
              React Frontend
                      |
          +-----------+-----------+
          |                       |
          v                       v
    Upload PDF/Image       Document Preview
          |
          v
       Django REST API
          |
          v
   Document Processing
          |
      +---+---+
      |       |
      v       v
  PDF Text   OCR
 Extraction  (Images /
              Scanned PDF)
      |       |
      +---+---+
          |
          v
     Extracted Text
          |
          v
   Summary Generation
          |
      +---+----------------+
      |        |           |
      v        v           v
   Summary  Key Points  Suggestions
      |        |           |
      +--------+-----------+
               |
               v
          React Frontend
               |
       +-------+-------+
       |               |
       v               v
    Display         Download/
                    Copy Results



document-summary-assistant/
│
├── backend/
│   │
│   ├── config/
│   ├── documents/
│   │   ├── summarizer.py
│   │   ├── key_points.py
│   │   ├── ...
│   │
│   ├── manage.py
│   └── ...
│
├── frontend/
│   │
│   ├── public/
│   │
│   ├── src/
│   │   ├── assets/
│   │   │
│   │   ├── components/
│   │   │   ├── UploadBox.jsx
│   │   │   ├── SummaryResult.jsx
│   │   │   ├── KeyPoints.jsx
│   │   │   ├── ExtractedText.jsx
│   │   │   └── Suggestions.jsx
│   │   │
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   │
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── .gitignore
└── README.md