FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# system deps (Pillow)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo \
    zlib1g \
 && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 10001 appuser

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY hse /app/hse

EXPOSE 8092

USER appuser

CMD ["uvicorn", "hse.main:app", "--host", "0.0.0.0", "--port", "8092"]
