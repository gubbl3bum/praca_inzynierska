import os
import sys
import django
import requests
import time
from urllib.parse import quote

# Setup Django 
sys.path.append('/backend')
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from ml_api.models import Book

class OpenLibraryFetcher:
    def __init__(self):
        self.base_url = "https://openlibrary.org"
        self.search_url = f"{self.base_url}/search.json"
        self.cover_url = "https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BookRecommendationSystem/1.0 (Educational Project)'
        })
    
    def search_book(self, title, author=None):
        """Szukaj książki w OpenLibrary API"""
        try:
            # Przygotuj query
            query = f'title:"{title}"'
            if author:
                query += f' author:"{author}"'
            
            params = {
                'q': query,
                'limit': 5,
                'fields': 'key,title,author_name,isbn,publish_year,cover_i'
            }
            
            response = self.session.get(self.search_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('docs'):
                return data['docs'][0]  # Zwróć pierwszy wynik
            
        except Exception as e:
            print(f"    ❌ Error searching for '{title}': {e}")
        
        return None
    
    def get_isbn_and_cover(self, book):
        """Pobierz ISBN i URL okładki dla książki"""
        try:
            # Przygotuj author string
            author_names = book.author_names
            first_author = author_names.split(',')[0].strip() if author_names else None
            
            print(f"🔍 Searching: {book.title} by {first_author}")
            
            # Szukaj w OpenLibrary
            result = self.search_book(book.title, first_author)
            
            if result:
                # Pobierz ISBN
                isbn = None
                if result.get('isbn'):
                    isbn = result['isbn'][0]  # Pierwszy ISBN z listy
                
                # Przygotuj URL okładki
                cover_url = None
                if isbn:
                    # Sprawdź czy okładka istnieje
                    cover_test_url = self.cover_url.format(isbn=isbn)
                    try:
                        cover_response = self.session.head(cover_test_url, timeout=5)
                        if cover_response.status_code == 200:
                            cover_url = cover_test_url
                    except:
                        pass
                
                return isbn, cover_url
            
        except Exception as e:
            print(f"    ❌ Error fetching data for '{book.title}': {e}")
        
        return None, None
    
    def update_book_with_isbn_cover(self, book):
        """Zaktualizuj książkę o ISBN i okładkę"""
        isbn, cover_url = self.get_isbn_and_cover(book)
        
        updated = False
        if isbn and not book.isbn:
            book.isbn = isbn
            updated = True
            print(f"    📚 ISBN: {isbn}")
        
        if cover_url and not book.cover_image_url:
            book.cover_image_url = cover_url
            updated = True
            print(f"    🖼️  Cover: {cover_url}")
        
        if updated:
            book.save()
            return True
        
        return False

def fetch_isbn_and_covers(batch_size=50, delay=1.0):  # Zmniejszone dla testów
    """Pobierz ISBN i okładki dla książek bez tych danych"""
    
    print("🌐 FETCHING ISBN AND COVERS FROM OPENLIBRARY")
    print("=" * 60)
    
    fetcher = OpenLibraryFetcher()
    
    # Znajdź książki bez ISBN lub okładek
    books_without_isbn = Book.objects.filter(isbn__isnull=True)[:batch_size]
    books_without_covers = Book.objects.filter(cover_image_url__isnull=True)[:batch_size]
    
    # Połącz i usuń duplikaty
    books_to_update = list(set(list(books_without_isbn) + list(books_without_covers)))
    
    print(f"📚 Found {len(books_to_update)} books to update")
    print(f"⏱️  Using {delay}s delay between requests")
    
    stats = {
        'processed': 0,
        'updated': 0,
        'isbn_found': 0,
        'covers_found': 0,
        'errors': 0
    }
    
    for i, book in enumerate(books_to_update, 1):
        try:
            print(f"\n📖 [{i}/{len(books_to_update)}] {book.title[:50]}...")
            
            # Sprawdź czy książka już ma dane
            if book.isbn and book.cover_image_url:
                print("    ✅ Already has ISBN and cover")
                continue
            
            # Pobierz dane
            isbn_before = book.isbn
            cover_before = book.cover_image_url
            
            updated = fetcher.update_book_with_isbn_cover(book)
            
            stats['processed'] += 1
            
            if updated:
                stats['updated'] += 1
                if book.isbn and not isbn_before:
                    stats['isbn_found'] += 1
                if book.cover_image_url and not cover_before:
                    stats['covers_found'] += 1
                print("    ✅ Updated!")
            else:
                print("    📭 No data found")
            
            # Opóźnienie między requestami
            if i < len(books_to_update):
                time.sleep(delay)
            
        except Exception as e:
            print(f"    ❌ Error: {e}")
            stats['errors'] += 1
            continue
    
    # Podsumowanie
    print("\n" + "=" * 60)
    print("🌐 OPENLIBRARY FETCH SUMMARY:")
    print(f"📚 Books processed: {stats['processed']}")
    print(f"✅ Books updated: {stats['updated']}")
    print(f"📖 ISBNs found: {stats['isbn_found']}")
    print(f"🖼️  Covers found: {stats['covers_found']}")
    print(f"❌ Errors: {stats['errors']}")
    
    return True

if __name__ == "__main__":
    # 🚨 TESTOWY LIMIT - USUŃ DLA PEŁNEGO POBIERANIA
    fetch_isbn_and_covers(batch_size=50, delay=1.0)  # 🔴 Zmień na większy batch_size