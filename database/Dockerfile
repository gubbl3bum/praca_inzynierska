FROM python:3.9-slim

WORKDIR /app

# Zainstaluj wymagane pakiety systemowe
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Zainstaluj pakiety Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Skopiuj skrypty
COPY . .

# Nadaj uprawnienia wykonywania
RUN chmod +x download_data.sh
RUN chmod +x data_import.py
RUN chmod +x entrypoint.sh

# Domyślnie uruchamiaj import
CMD ["python", "data_import.py"]