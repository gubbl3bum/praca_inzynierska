FROM python:3.9

WORKDIR /app

RUN apt-get update && apt-get install -y netcat-openbsd && apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pobierz dane NLTK (jeśli potrzebne)
RUN python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('wordnet', quiet=True)" || true

COPY . .

EXPOSE 8000

# Poprawiona ścieżka do pliku importu
CMD ["sh", "-c", "while ! nc -z db 5432; do sleep 1; done && python manage.py makemigrations ml_api --noinput && python manage.py migrate --noinput && python database/normalized_data_import.py && python manage.py runserver 0.0.0.0:8000"]