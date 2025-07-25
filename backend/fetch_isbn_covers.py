import os
import sys
import django
import requests
import time
import re
from urllib.parse import quote

# Setup Django 
sys.path.append('/backend')
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from ml_api.models import Book

class ImprovedCoverFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BookRecommendationSystem/1.0 (Educational Project)'
        })
        
        # Różne sposoby na znalezienie okładek
        self.strategies = [
            self.strategy_open_library_search,
            self.strategy_open_library_direct_title,
            self.strategy_google_books,
            self.strategy_placeholder_generator
        ]
    
    def clean_title_for_search(self, title):
        """Oczyść tytuł do wyszukiwania"""
        if not title:
            return ""
        
        # Usuń znaki specjalne i normalizuj
        title = re.sub(r'[^\w\s]', ' ', title)
        title = re.sub(r'\s+', ' ', title).strip()
        
        # Usuń część po dwukropku (często podtytuły)
        if ':' in title:
            title = title.split(':')[0].strip()
        
        return title
    
    def clean_author_for_search(self, author):
        """Oczyść autora do wyszukiwania"""
        if not author:
            return ""
        
        # Weź tylko pierwszego autora
        if ',' in author:
            author = author.split(',')[0].strip()
        
        # Usuń "By " prefix
        if author.startswith("By "):
            author = author[3:].strip()
        
        return author
    
    def check_cover_exists(self, url):
        """Sprawdź czy okładka istnieje"""
        try:
            response = self.session.head(url, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def strategy_open_library_search(self, book):
        """Strategia 1: Wyszukiwanie w Open Library przez API"""
        try:
            clean_title = self.clean_title_for_search(book.title)
            clean_author = self.clean_author_for_search(book.author_names)
            
            if not clean_title:
                return None, None
            
            # Buduj query
            query_parts = [f'title:"{clean_title}"']
            if clean_author:
                query_parts.append(f'author:"{clean_author}"')
            
            query = ' AND '.join(query_parts)
            
            params = {
                'q': query,
                'limit': 5,
                'fields': 'key,title,author_name,isbn,cover_i,cover_edition_key'
            }
            
            response = self.session.get(
                "https://openlibrary.org/search.json", 
                params=params, 
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            for doc in data.get('docs', []):
                # Spróbuj ISBN
                if doc.get('isbn'):
                    for isbn in doc['isbn'][:3]:  # Sprawdź pierwsze 3 ISBN
                        cover_url = f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"
                        if self.check_cover_exists(cover_url):
                            return isbn, cover_url
                
                # Spróbuj cover_i (ID okładki)
                if doc.get('cover_i'):
                    cover_url = f"https://covers.openlibrary.org/b/id/{doc['cover_i']}-L.jpg"
                    if self.check_cover_exists(cover_url):
                        return doc.get('isbn', [None])[0], cover_url
            
        except Exception as e:
            print(f"      Strategy 1 failed: {e}")
        
        return None, None
    
    def strategy_open_library_direct_title(self, book):
        """Strategia 2: Bezpośrednie wyszukiwanie po tytule"""
        try:
            clean_title = self.clean_title_for_search(book.title)
            if not clean_title:
                return None, None
            
            # Próbuj różne warianty tytułu
            title_variants = [
                clean_title,
                clean_title.replace(' ', '+'),
                quote(clean_title)
            ]
            
            for variant in title_variants:
                params = {
                    'title': variant,
                    'limit': 3,
                    'fields': 'isbn,cover_i'
                }
                
                response = self.session.get(
                    "https://openlibrary.org/search.json",
                    params=params,
                    timeout=8
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for doc in data.get('docs', []):
                        if doc.get('isbn'):
                            isbn = doc['isbn'][0]
                            cover_url = f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"
                            if self.check_cover_exists(cover_url):
                                return isbn, cover_url
        
        except Exception as e:
            print(f"      Strategy 2 failed: {e}")
        
        return None, None
    
    def strategy_google_books(self, book):
        """Strategia 3: Google Books API (backup)"""
        try:
            clean_title = self.clean_title_for_search(book.title)
            clean_author = self.clean_author_for_search(book.author_names)
            
            if not clean_title:
                return None, None
            
            # Buduj query dla Google Books
            query_parts = [f'intitle:"{clean_title}"']
            if clean_author:
                query_parts.append(f'inauthor:"{clean_author}"')
            
            query = '+'.join(query_parts)
            
            params = {
                'q': query,
                'maxResults': 3,
                'fields': 'items(volumeInfo(imageLinks,industryIdentifiers))'
            }
            
            response = self.session.get(
                "https://www.googleapis.com/books/v1/volumes",
                params=params,
                timeout=8
            )
            response.raise_for_status()
            
            data = response.json()
            
            for item in data.get('items', []):
                volume_info = item.get('volumeInfo', {})
                
                # Pobierz okładkę
                image_links = volume_info.get('imageLinks', {})
                cover_url = (
                    image_links.get('large') or 
                    image_links.get('medium') or 
                    image_links.get('thumbnail')
                )
                
                if cover_url:
                    # Pobierz ISBN
                    isbn = None
                    for identifier in volume_info.get('industryIdentifiers', []):
                        if identifier.get('type') in ['ISBN_13', 'ISBN_10']:
                            isbn = identifier.get('identifier')
                            break
                    
                    return isbn, cover_url
        
        except Exception as e:
            print(f"      Strategy 3 failed: {e}")
        
        return None, None
    
    def strategy_placeholder_generator(self, book):
        """Strategia 4: Generuj placeholder okładkę (ostatnia opcja)"""
        try:
            # Możesz użyć serwisu do generowania placeholderów
            # Na przykład: https://via.placeholder.com/300x400/4A90E2/FFFFFF?text=Title
            
            title_short = book.title[:20] if book.title else "Book"
            title_encoded = quote(title_short)
            
            placeholder_url = f"https://via.placeholder.com/300x400/4A90E2/FFFFFF?text={title_encoded}"
            
            return None, placeholder_url
        
        except:
            pass
        
        return None, None
    
    def find_cover_for_book(self, book):
        """Znajdź okładkę używając wszystkich strategii"""
        print(f"📖 Searching cover for: {book.title}")
        
        for i, strategy in enumerate(self.strategies, 1):
            print(f"    🔍 Strategy {i}: {strategy.__name__}")
            
            try:
                isbn, cover_url = strategy(book)
                
                if cover_url:
                    print(f"    ✅ Found cover: {cover_url[:50]}...")
                    return isbn, cover_url
                else:
                    print(f"    ❌ No result")
            
            except Exception as e:
                print(f"    💥 Strategy {i} error: {e}")
                continue
            
            # Krótkie opóźnienie między strategiami
            time.sleep(0.5)
        
        print(f"    📭 No cover found for: {book.title}")
        return None, None
    
    def update_book_with_cover(self, book):
        """Zaktualizuj książkę z okładką"""
        # Pomiń jeśli już ma okładkę
        if book.cover_image_url:
            print(f"    ✅ Already has cover: {book.title}")
            return False
        
        isbn, cover_url = self.find_cover_for_book(book)
        
        updated = False
        
        if isbn and not book.isbn:
            book.isbn = isbn
            updated = True
            print(f"    📚 Added ISBN: {isbn}")
        
        if cover_url:
            book.cover_image_url = cover_url
            updated = True
            print(f"    🖼️  Added cover: {cover_url[:50]}...")
        
        if updated:
            try:
                book.save()
                return True
            except Exception as e:
                print(f"    ❌ Failed to save: {e}")
        
        return False

def fetch_covers_improved(batch_size=None, delay=1.5):
    """
    Pobierz okładki używając ulepszonych strategii
    
    Args:
        batch_size: Ile książek przetworzyć (None = wszystkie)
        delay: Opóźnienie między książkami w sekundach
    """
    
    print("🌐 IMPROVED COVER FETCHING")
    print("=" * 50)
    
    fetcher = ImprovedCoverFetcher()
    
    # Znajdź książki bez okładek
    books_without_covers = Book.objects.filter(cover_image_url__isnull=True)
    
    if batch_size:
        books_without_covers = books_without_covers[:batch_size]
        print(f"📚 Processing {len(books_without_covers)} books (limited to {batch_size})")
    else:
        print(f"📚 Processing {len(books_without_covers)} books (ALL without covers)")
    
    print(f"⏱️  Using {delay}s delay between books")
    print()
    
    stats = {
        'processed': 0,
        'updated': 0,
        'isbn_found': 0,
        'covers_found': 0,
        'errors': 0
    }
    
    for i, book in enumerate(books_without_covers, 1):
        try:
            print(f"[{i}/{len(books_without_covers)}] " + "="*40)
            
            isbn_before = book.isbn
            cover_before = book.cover_image_url
            
            updated = fetcher.update_book_with_cover(book)
            
            stats['processed'] += 1
            
            if updated:
                stats['updated'] += 1
                if book.isbn and not isbn_before:
                    stats['isbn_found'] += 1
                if book.cover_image_url and not cover_before:
                    stats['covers_found'] += 1
            
            print()
            
            # Opóźnienie między książkami
            if i < len(books_without_covers):
                time.sleep(delay)
        
        except Exception as e:
            print(f"💥 Error processing {book.title}: {e}")
            stats['errors'] += 1
            continue
    
    # Podsumowanie
    print("=" * 50)
    print("📊 IMPROVED FETCH SUMMARY:")
    print(f"📚 Books processed: {stats['processed']}")
    print(f"✅ Books updated: {stats['updated']}")
    print(f"📖 ISBNs found: {stats['isbn_found']}")
    print(f"🖼️  Covers found: {stats['covers_found']}")
    print(f"❌ Errors: {stats['errors']}")
    
    success_rate = (stats['covers_found'] / stats['processed'] * 100) if stats['processed'] > 0 else 0
    print(f"🎯 Success rate: {success_rate:.1f}%")
    
    return True

def test_single_book(book_title):
    """Test cover fetching dla pojedynczej książki"""
    try:
        book = Book.objects.filter(title__icontains=book_title).first()
        if not book:
            print(f"❌ Book not found: {book_title}")
            return
        
        print(f"🧪 Testing cover fetch for: {book.title}")
        print(f"    Author: {book.author_names}")
        print(f"    Current ISBN: {book.isbn}")
        print(f"    Current cover: {book.cover_image_url}")
        print()
        
        fetcher = ImprovedCoverFetcher()
        fetcher.update_book_with_cover(book)
        
    except Exception as e:
        print(f"💥 Test failed: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Improved book cover fetcher')
    parser.add_argument('--limit', type=int, help='Limit number of books to process')
    parser.add_argument('--delay', type=float, default=1.5, help='Delay between books (seconds)')
    parser.add_argument('--test', type=str, help='Test single book by title')
    
    args = parser.parse_args()
    
    if args.test:
        test_single_book(args.test)
    else:
        fetch_covers_improved(batch_size=args.limit, delay=args.delay)