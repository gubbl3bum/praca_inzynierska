#!/bin/bash

# Czekaj na dostęp do bazy danych
echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "PostgreSQL started"

# Wykonaj migracje
python manage.py migrate

# Uruchom serwer deweloperski
python manage.py runserver 0.0.0.0:8000