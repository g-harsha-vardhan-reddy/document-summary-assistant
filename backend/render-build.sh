
#!/usr/bin/env bash

set -o errexit

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Installing Tesseract OCR..."
apt-get update
apt-get install -y tesseract-ocr

echo "Collecting Django static files..."
python manage.py collectstatic --noinput

echo "Build completed successfully."
