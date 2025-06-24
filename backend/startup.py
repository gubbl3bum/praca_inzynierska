"""
Prosty skrypt startowy dla WolfRead
- Sprawdza czy baza ma dane
- Jeśli nie ma -> importuje książki z CSV
- Jeśli import się udał -> pobiera okładki
"""

import os
import sys
import subprocess
import time

def wait_for_database():
    """Poczekaj aż baza będzie dostępna"""
    print("🔄 Czekam na bazę danych...")
    
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            result = subprocess.run([
                'nc', '-z', 'db', '5432'
            ], capture_output=True)
            
            if result.returncode == 0:
                print("✅ Baza danych gotowa!")
                return True
                
        except:
            pass
            
        print(f"   Próba {attempt + 1}/{max_attempts}...")
        time.sleep(2)
    
    print("❌ Nie można połączyć z bazą danych!")
    return False

def run_migrations():
    """Uruchom migracje Django"""
    print("🔧 Uruchamiam migracje Django...")
    
    try:
        # Makemigrations
        subprocess.run([
            'python', 'manage.py', 'makemigrations', 'ml_api', '--noinput'
        ], check=False)
        
        # Migrate
        result = subprocess.run([
            'python', 'manage.py', 'migrate', '--noinput'
        ], check=True)
        
        print("✅ Migracje zakończone!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Błąd migracji: {e}")
        return False

def check_if_data_exists():
    """Sprawdź czy baza ma już dane"""
    print("🔍 Sprawdzam czy baza ma dane...")
    
    try:
        result = subprocess.run([
            'python', '-c', '''
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from ml_api.models import Book
count = Book.objects.count()
print(f"BOOKS_COUNT:{count}")
'''
        ], capture_output=True, text=True, check=True)
        
        # Wyciągnij liczbę książek z output
        for line in result.stdout.split('\n'):
            if line.startswith('BOOKS_COUNT:'):
                count = int(line.split(':')[1])
                print(f"📚 Znaleziono {count} książek w bazie")
                return count > 0
                
    except Exception as e:
        print(f"⚠️ Błąd sprawdzania danych: {e}")
        
    return False

def run_data_import():
    """Uruchom import danych"""
    print("📥 Uruchamiam import danych...")
    
    try:
        result = subprocess.run([
            'python', 'database/normalized_data_import.py'
        ], check=True)
        
        print("✅ Import danych zakończony!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Import danych nie powiódł się: {e}")
        return False

def fetch_book_covers():
    """Pobierz okładki książek"""
    print("🖼️ Pobieranie okładek książek...")
    
    try:
        # Uruchom bez limitu (usunięto --limit)
        result = subprocess.run([
            'python', 'fetch_isbn_covers.py'
        ], check=True)
        
        print("✅ Pobieranie okładek zakończone!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Pobieranie okładek nie powiodło się: {e}")
        return False
    except FileNotFoundError:
        print("⚠️ Skrypt pobierania okładek nie znaleziony - pomijam")
        return False

def start_django_server():
    """Uruchom serwer Django"""
    print("🌐 Uruchamiam serwer Django...")
    
    try:
        # Używamy exec żeby serwer przejął kontrolę nad procesem
        os.execvp('python', ['python', 'manage.py', 'runserver', '0.0.0.0:8000'])
    except Exception as e:
        print(f"❌ Nie można uruchomić serwera: {e}")
        sys.exit(1)

def main():
    """Główna funkcja"""
    print("🚀 WolfRead - Start!")
    print("=" * 40)
    
    # Krok 1: Poczekaj na bazę danych
    if not wait_for_database():
        sys.exit(1)
    
    # Krok 2: Uruchom migracje
    if not run_migrations():
        print("⚠️ Migracje nie powiodły się, ale kontynuuję...")
    
    # Krok 3: Sprawdź czy potrzebny import
    if check_if_data_exists():
        print("✅ Baza już ma dane - pomijam import")
    else:
        print("📭 Baza pusta - rozpoczynam import...")
        
        # Krok 4: Import danych
        if run_data_import():
            # Krok 5: Pobierz okładki (tylko jeśli import się udał)
            fetch_book_covers()
        else:
            print("⚠️ Import nie powiódł się, ale uruchamiam serwer...")
    
    # Krok 6: Uruchom serwer Django
    start_django_server()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Przerwano przez użytkownika")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Nieoczekiwany błąd: {e}")
        sys.exit(1)