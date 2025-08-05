FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
# Install Python dependencies including portalocker for cross-platform file locking
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh","-c","[ -f .env ] || echo '.env file not found; environment variables may be missing'; uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
