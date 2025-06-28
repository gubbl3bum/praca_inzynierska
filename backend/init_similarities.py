"""
Skrypt do inicjalizacji podobieństw książek
backend/init_similarities.py
"""

import os
import sys
import django
import time
from django.db import transaction, models

# Setup Django 
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from ml_api.models import Book, BookSimilarity, BookVector
from ml_api.services.similarity_service import BookSimilarityService

def check_prerequisites():
    """Sprawdź czy system jest gotowy"""
    print("🔍 Checking prerequisites...")
    
    # Sprawdź liczbę książek
    book_count = Book.objects.count()
    print(f"📚 Books in database: {book_count}")
    
    if book_count == 0:
        print("❌ No books found! Please import books first.")
        return False
    
    if book_count < 10:
        print("⚠️  Very few books - similarities might not be meaningful")
    
    # Sprawdź czy są już podobieństwa
    similarity_count = BookSimilarity.objects.count()
    print(f"🔗 Existing similarities: {similarity_count}")
    
    if similarity_count > 0:
        response = input("❓ Similarities already exist. Recalculate? (y/N): ")
        if response.lower() != 'y':
            print("✅ Keeping existing similarities")
            return False
    
    return True

def calculate_sample_similarities(sample_size=50):
    """Wylicz podobieństwa dla próbki książek"""
    print(f"🧪 Calculating similarities for {sample_size} sample books...")
    
    service = BookSimilarityService()
    
    # Weź najbardziej popularne książki (z recenzjami)
    sample_books = Book.objects.annotate(
        review_count=models.Count('reviews')
    ).order_by('-review_count', '-created_at')[:sample_size]
    
    print(f"📊 Selected {len(sample_books)} books for similarity calculation")
    
    total_similarities = 0
    processed = 0
    
    start_time = time.time()
    
    for book in sample_books:
        try:
            print(f"[{processed + 1}/{len(sample_books)}] Processing: {book.title[:50]}")
            
            similarities_count = service.calculate_similarities_for_book(book, batch_size=20)
            total_similarities += similarities_count
            processed += 1
            
            # Progress indicator
            if processed % 10 == 0:
                elapsed = time.time() - start_time
                avg_time = elapsed / processed
                remaining_time = avg_time * (len(sample_books) - processed)
                print(f"   📈 Progress: {processed}/{len(sample_books)} books | ETA: {remaining_time/60:.1f} min")
            
        except Exception as e:
            print(f"   ❌ Error processing {book.title}: {e}")
            continue
    
    elapsed_time = time.time() - start_time
    
    print(f"\n✅ Sample calculation completed!")
    print(f"📊 Books processed: {processed}/{len(sample_books)}")
    print(f"🔗 Total similarities created: {total_similarities}")
    print(f"⏱️  Time taken: {elapsed_time/60:.2f} minutes")
    print(f"📈 Average similarities per book: {total_similarities/processed if processed > 0 else 0:.1f}")
    
    return total_similarities

def calculate_all_similarities():
    """Wylicz podobieństwa dla wszystkich książek"""
    print("🚀 Starting FULL similarity calculation...")
    print("⚠️  This will take a LONG time for large datasets!")
    
    response = input("❓ Are you sure you want to calculate similarities for ALL books? (y/N): ")
    if response.lower() != 'y':
        print("❌ Cancelled")
        return 0
    
    service = BookSimilarityService()
    return service.calculate_all_similarities()

def show_similarity_examples():
    """Pokaż przykłady wyliczonych podobieństw"""
    print("\n📋 SIMILARITY EXAMPLES")
    print("=" * 60)
    
    # Top 10 najwyższych podobieństw
    top_similarities = BookSimilarity.objects.order_by('-cosine_similarity')[:10]
    
    if not top_similarities:
        print("❌ No similarities calculated yet")
        return
    
    print("🏆 TOP 10 HIGHEST SIMILARITIES:")
    for i, sim in enumerate(top_similarities, 1):
        print(f"   {i:2d}. {sim.book1.title[:30]:30} ↔ {sim.book2.title[:30]:30}")
        print(f"       Similarity: {sim.cosine_similarity:.4f}")
        print(f"       Categories: {sim.category_similarity:.3f} | "
              f"Keywords: {sim.keyword_similarity:.3f} | "
              f"Authors: {sim.author_similarity:.3f}")
        print()
    
    # Przykład rekomendacji dla losowej książki
    random_book = Book.objects.filter(
        similarities_as_book1__isnull=False
    ).first()
    
    if random_book:
        print(f"📚 RECOMMENDATIONS FOR: {random_book.title}")
        service = BookSimilarityService()
        recommendations = service.get_similar_books(random_book, limit=5)
        
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec['book'].title} (similarity: {rec['similarity']:.3f})")

def analyze_similarity_quality():
    """Analizuj jakość wyliczonych podobieństw"""
    print("\n🔬 SIMILARITY QUALITY ANALYSIS")
    print("=" * 60)
    
    from django.db.models import Avg, Max, Min, Count
    
    # Podstawowe statystyki
    stats = BookSimilarity.objects.aggregate(
        count=Count('id'),
        avg_similarity=Avg('cosine_similarity'),
        max_similarity=Max('cosine_similarity'),
        min_similarity=Min('cosine_similarity'),
        avg_category=Avg('category_similarity'),
        avg_keyword=Avg('keyword_similarity'),
        avg_author=Avg('author_similarity'),
        avg_description=Avg('description_similarity')
    )
    
    print(f"📊 Total similarities: {stats['count']}")
    print(f"📈 Average similarity: {stats['avg_similarity']:.4f}")
    print(f"🔝 Maximum similarity: {stats['max_similarity']:.4f}")
    print(f"🔻 Minimum similarity: {stats['min_similarity']:.4f}")
    print()
    print("📋 Component averages:")
    print(f"   Categories: {stats['avg_category']:.4f}")
    print(f"   Keywords:   {stats['avg_keyword']:.4f}")
    print(f"   Authors:    {stats['avg_author']:.4f}")
    print(f"   Description:{stats['avg_description']:.4f}")
    
    # Rozkład podobieństw
    print("\n📊 SIMILARITY DISTRIBUTION:")
    ranges = [
        (0.8, 1.0, "Very High (0.8-1.0)"),
        (0.6, 0.8, "High (0.6-0.8)"),
        (0.4, 0.6, "Medium (0.4-0.6)"),
        (0.2, 0.4, "Low (0.2-0.4)"),
        (0.0, 0.2, "Very Low (0.0-0.2)")
    ]
    
    for min_sim, max_sim, label in ranges:
        count = BookSimilarity.objects.filter(
            cosine_similarity__gte=min_sim,
            cosine_similarity__lt=max_sim
        ).count()
        percentage = (count / stats['count'] * 100) if stats['count'] > 0 else 0
        print(f"   {label:20} {count:6d} ({percentage:5.1f}%)")

def clean_similarities():
    """Wyczyść wszystkie podobieństwa"""
    print("🧹 CLEANING ALL SIMILARITIES")
    
    response = input("❓ Are you sure you want to delete ALL similarities? (y/N): ")
    if response.lower() != 'y':
        print("❌ Cancelled")
        return
    
    similarity_count = BookSimilarity.objects.count()
    vector_count = BookVector.objects.count()
    
    with transaction.atomic():
        BookSimilarity.objects.all().delete()
        BookVector.objects.all().delete()
    
    print(f"✅ Deleted {similarity_count} similarities and {vector_count} vectors")

def main():
    """Główna funkcja"""
    print("🚀 BOOK SIMILARITY INITIALIZATION")
    print("=" * 60)
    
    while True:
        print("\n📋 Available options:")
        print("   1. Check prerequisites")
        print("   2. Calculate sample similarities (recommended)")
        print("   3. Calculate ALL similarities (slow!)")
        print("   4. Show similarity examples")
        print("   5. Analyze similarity quality")
        print("   6. Clean all similarities")
        print("   7. Exit")
        
        choice = input("\n❓ Choose option (1-7): ").strip()
        
        try:
            if choice == '1':
                check_prerequisites()
            
            elif choice == '2':
                if check_prerequisites():
                    sample_size = input("📊 Sample size (default 50): ").strip()
                    sample_size = int(sample_size) if sample_size else 50
                    calculate_sample_similarities(sample_size)
                    show_similarity_examples()
            
            elif choice == '3':
                if check_prerequisites():
                    calculate_all_similarities()
                    show_similarity_examples()
            
            elif choice == '4':
                show_similarity_examples()
            
            elif choice == '5':
                analyze_similarity_quality()
            
            elif choice == '6':
                clean_similarities()
            
            elif choice == '7':
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid option")
        
        except KeyboardInterrupt:
            print("\n🛑 Interrupted by user")
            break
        except Exception as e:
            print(f"💥 Error: {e}")

if __name__ == "__main__":
    main()