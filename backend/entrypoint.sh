#!/bin/bash

# Czekaj na dostęp do bazy danych
echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "PostgreSQL started"

# Stwórz migracje jeśli nie istnieją
echo "Creating migrations..."
python manage.py makemigrations ml_api

# Wykonaj migracje
echo "Applying migrations..."
python manage.py migrate

# Załaduj przykładowe dane (tylko jeśli baza jest pusta)
echo "Loading sample data..."
python manage.py load_sample_books

# Uruchom serwer deweloperski
echo "Starting Django development server..."
python manage.py runserver 0.0.0.0:8000