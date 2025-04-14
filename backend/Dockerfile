FROM python:3.9

WORKDIR /app

# Zainstaluj netcat
RUN apt-get update && apt-get install -y netcat-openbsd && apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["./entrypoint.sh"]