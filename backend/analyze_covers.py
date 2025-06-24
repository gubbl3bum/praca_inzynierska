"""
Skrypt do analizy dostępności okładek w bazie danych
"""

import os
import sys
import django
import requests
from collections import defaultdict

# Setup Django 
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from ml_api.models import Book

def analyze_covers():
    """Analiza dostępności okładek"""
    print("📊 ANALIZA OKŁADEK W BAZIE DANYCH")
    print("=" * 50)
    
    # Podstawowe statystyki
    total_books = Book.objects.count()
    books_with_covers = Book.objects.filter(cover_image_url__isnull=False).count()
    books_without_covers = total_books - books_with_covers
    
    print(f"📚 Całkowita liczba książek: {total_books}")
    print(f"🖼️  Książki z okładkami: {books_with_covers}")
    print(f"📭 Książki bez okładek: {books_without_covers}")
    
    if total_books > 0:
        coverage_percentage = (books_with_covers / total_books) * 100
        print(f"📈 Pokrycie okładkami: {coverage_percentage:.1f}%")
    
    print("\n" + "=" * 50)
    
    # Analiza autorów z największą liczbą książek bez okładek
    print("👤 AUTORZY Z NAJWIĘCEJ KSIĄŻKAMI BEZ OKŁADEK:")
    
    books_no_covers = Book.objects.filter(cover_image_url__isnull=True)
    author_stats = defaultdict(int)
    
    for book in books_no_covers:
        author = book.author_names or "Unknown Author"
        author_stats[author] += 1
    
    # Top 10 autorów
    top_authors = sorted(author_stats.items(), key=lambda x: x[1], reverse=True)[:10]
    
    for i, (author, count) in enumerate(top_authors, 1):
        print(f"   {i:2d}. {author[:30]:30} ({count} książek)")
    
    print("\n" + "=" * 50)
    
    # Analiza kategorii
    print("📂 KATEGORIE Z NAJWIĘKSZĄ LICZBĄ KSIĄŻEK BEZ OKŁADEK:")
    
    category_stats = defaultdict(int)
    
    for book in books_no_covers:
        categories = book.categories.all()
        if categories:
            for category in categories:
                category_stats[category.name] += 1
        else:
            category_stats["No Category"] += 1
    
    # Top 10 kategorii
    top_categories = sorted(category_stats.items(), key=lambda x: x[1], reverse=True)[:10]
    
    for i, (category, count) in enumerate(top_categories, 1):
        print(f"   {i:2d}. {category[:30]:30} ({count} książek)")
    
    print("\n" + "=" * 50)
    
    # Przykłady książek bez okładek
    print("📖 PRZYKŁADY KSIĄŻEK BEZ OKŁADEK:")
    
    sample_books = books_no_covers[:10]
    
    for i, book in enumerate(sample_books, 1):
        print(f"   {i:2d}. {book.title[:40]:40} - {book.author_names[:20]:20}")
    
    return {
        'total_books': total_books,
        'books_with_covers': books_with_covers,
        'books_without_covers': books_without_covers,
        'coverage_percentage': coverage_percentage if total_books > 0 else 0,
        'top_authors_no_covers': top_authors[:5],
        'top_categories_no_covers': top_categories[:5]
    }

def test_cover_urls():
    """Przetestuj czy istniejące URL-e okładek działają"""
    print("\n🔍 TESTOWANIE ISTNIEJĄCYCH URL-I OKŁADEK")
    print("=" * 50)
    
    books_with_covers = Book.objects.filter(cover_image_url__isnull=False)
    sample_books = books_with_covers
    
    working_urls = 0
    broken_urls = 0
    
    print(f"🧪 Testowanie {len(sample_books)} URL-i okładek...")
    
    for i, book in enumerate(sample_books, 1):
        try:
            response = requests.head(book.cover_image_url, timeout=5)
            if response.status_code == 200:
                status = "✅"
                working_urls += 1
            else:
                status = f"❌ ({response.status_code})"
                broken_urls += 1
        except:
            status = "❌ (timeout/error)"
            broken_urls += 1
        
        print(f"   {i:2d}. {status} {book.title[:30]:30} - {book.cover_image_url[:50]:50}")
    
    print(f"\n📊 Wyniki testu URL-i:")
    print(f"   ✅ Działające: {working_urls}")
    print(f"   ❌ Zepsute: {broken_urls}")
    
    if len(sample_books) > 0:
        url_success_rate = (working_urls / len(sample_books)) * 100
        print(f"   📈 Wskaźnik sukcesu: {url_success_rate:.1f}%")

def suggest_improvements():
    """Zasugeruj poprawki"""
    print("\n💡 SUGESTIE POPRAWY:")
    print("=" * 50)
    
    # Sprawdź książki z ISBN ale bez okładek
    books_with_isbn_no_cover = Book.objects.filter(
        isbn__isnull=False,
        cover_image_url__isnull=True
    ).count()
    
    print(f"📚 Książki z ISBN ale bez okładek: {books_with_isbn_no_cover}")
    print("   💡 Te książki mają największą szansę na znalezienie okładek")
    
    # Sprawdź książki bez ISBN i bez okładek
    books_no_isbn_no_cover = Book.objects.filter(
        isbn__isnull=True,
        cover_image_url__isnull=True
    ).count()
    
    print(f"📭 Książki bez ISBN i bez okładek: {books_no_isbn_no_cover}")
    print("   💡 Te książki wymagają wyszukiwania po tytule/autorze")
    
    print("\n🎯 REKOMENDACJE:")
    print("   1. Uruchom ulepszone pobieranie okładek:")
    print("      python fetch_isbn_covers.py")
    print("   2. Dla testowania pojedynczych książek:")
    print("      python fetch_isbn_covers.py --test 'Title of Book'")
    print("   3. Dla ograniczonej liczby książek:")
    print("      python fetch_isbn_covers.py --limit 50")

if __name__ == "__main__":
    stats = analyze_covers()
    test_cover_urls()
    suggest_improvements()
    
    print("\n" + "=" * 50)
    print("✅ Analiza zakończona!")
    
    if stats['coverage_percentage'] < 50:
        print("⚠️  Niska dostępność okładek - zalecane uruchomienie fetch_isbn_covers.py")
    elif stats['coverage_percentage'] < 80:
        print("📈 Średnia dostępność okładek - można poprawić")
    else:
        print("🎉 Wysoka dostępność okładek!")