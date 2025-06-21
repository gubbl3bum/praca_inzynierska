FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    netcat-openbsd \
    postgresql-client \
    curl \
    unzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY data_import.py .
COPY download_data.sh .
RUN chmod +x download_data.sh

RUN mkdir -p /data

ENV PYTHONPATH=/app
ENV DJANGO_SETTINGS_MODULE=config.settings

CMD ["python", "data_import.py"]