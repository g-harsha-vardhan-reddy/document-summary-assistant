import os
import uuid

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .extraction import extract_pdf_text
from .ocr import extract_image_text, extract_scanned_pdf_text
from .summarizer import generate_summary
from .key_points import generate_key_points
from .suggestions import generate_suggestions


ALLOWED_EXTENSIONS = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@api_view(["POST"])
def summarize(request):

    uploaded_file = request.FILES.get("file")

    summary_length = request.data.get(
        "summary_length",
        "medium"
    ).lower()

    # -----------------------------------------
    # FILE VALIDATION
    # -----------------------------------------

    if not uploaded_file:
        return Response(
            {
                "error": "No file was uploaded."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if uploaded_file.size > MAX_FILE_SIZE:
        return Response(
            {
                "error": "File size must not exceed 10 MB."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # -----------------------------------------
    # SUMMARY LENGTH VALIDATION
    # -----------------------------------------

    if summary_length not in {
        "short",
        "medium",
        "long"
    }:
        return Response(
            {
                "error": (
                    "summary_length must be "
                    "short, medium, or long."
                )
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # -----------------------------------------
    # FILE TYPE VALIDATION
    # -----------------------------------------

    extension = os.path.splitext(
        uploaded_file.name
    )[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        return Response(
            {
                "error": (
                    "Unsupported file type. "
                    "Use PDF, PNG, JPG, or JPEG."
                )
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # -----------------------------------------
    # CREATE TEMP DIRECTORY
    # -----------------------------------------

    os.makedirs(
        "temp",
        exist_ok=True
    )

    safe_filename = f"{uuid.uuid4()}{extension}"

    file_path = os.path.join(
        "temp",
        safe_filename
    )

    try:

        # -----------------------------------------
        # SAVE UPLOADED FILE
        # -----------------------------------------

        with open(
            file_path,
            "wb+"
        ) as destination:

            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        # -----------------------------------------
        # TEXT EXTRACTION
        # -----------------------------------------

        if extension == ".pdf":

            extracted_text = extract_pdf_text(
                file_path
            )

            # Scanned PDF fallback
            if not extracted_text:

                extracted_text = (
                    extract_scanned_pdf_text(
                        file_path
                    )
                )

        else:

            extracted_text = extract_image_text(
                file_path
            )

        # -----------------------------------------
        # EMPTY TEXT VALIDATION
        # -----------------------------------------

        if not extracted_text:

            return Response(
                {
                    "error": (
                        "No readable text was found "
                        "in the document."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # -----------------------------------------
        # SUMMARY GENERATION
        # -----------------------------------------

        summary = generate_summary(
            extracted_text,
            summary_length
        )

        # -----------------------------------------
        # KEY POINTS
        # -----------------------------------------

        key_points = generate_key_points(
            extracted_text,
            count=5
        )

        # -----------------------------------------
        # IMPROVEMENT SUGGESTIONS
        # -----------------------------------------

        suggestions = generate_suggestions(
            extracted_text
        )

        # -----------------------------------------
        # API RESPONSE
        # -----------------------------------------

        return Response(
            {
                "filename": uploaded_file.name,
                "summary_length": summary_length,
                "text": extracted_text,
                "summary": summary,
                "key_points": key_points,
                "suggestions": suggestions,
            },
            status=status.HTTP_200_OK,
        )

    # -----------------------------------------
    # ERROR HANDLING
    # -----------------------------------------

    except Exception as e:

        return Response(
            {
                "error": (
                    f"Document processing failed: {str(e)}"
                )
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # -----------------------------------------
    # CLEANUP
    # -----------------------------------------

    finally:

        if os.path.exists(file_path):
            os.remove(file_path)