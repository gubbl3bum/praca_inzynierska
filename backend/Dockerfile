FROM python:3.9

WORKDIR /app

# Zainstaluj wymagane narzędzia systemowe
RUN apt-get update && apt-get install -y netcat-openbsd && apt-get clean

# Zainstaluj zależności Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# NLTK data - pobierz raz przy budowaniu obrazu
RUN python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('wordnet', quiet=True); nltk.download('omw-1.4', quiet=True)"

# Skopiuj kod aplikacji
COPY . .

# Udostępnij port
EXPOSE 8000

# Uruchom skrypt startowy
CMD ["python", "startup.py"]