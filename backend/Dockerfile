FROM python:3.9

WORKDIR /app

# Zainstaluj netcat
RUN apt-get update && apt-get install -y netcat-openbsd && apt-get clean

# Skopiuj requirements i zainstaluj zależności
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Skopiuj kod aplikacji
COPY . .

EXPOSE 8000

# Uruchom bezpośrednio z wieloma komendami
CMD ["sh", "-c", "while ! nc -z db 5432; do sleep 1; done && python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]