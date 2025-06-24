from django.core.management.base import BaseCommand
from django.db import models
from ml_api.services.similarity_service import BookSimilarityService
from ml_api.models import Book, BookSimilarity

class Command(BaseCommand):
    help = 'Calculate book similarities using cosine similarity'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Calculate similarities for all books',
        )
        parser.add_argument(
            '--book',
            type=int,
            help='Calculate similarities for specific book ID',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=50,
            help='Batch size for processing (default: 50)',
        )
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Clean existing similarities before calculation',
        )
        parser.add_argument(
            '--stats',
            action='store_true',
            help='Show similarity statistics',
        )
    
    def handle(self, *args, **options):
        service = BookSimilarityService()
        
        if options['clean']:
            self.stdout.write("🧹 Cleaning existing similarities...")
            deleted_count = BookSimilarity.objects.all().delete()[0]
            self.stdout.write(
                self.style.SUCCESS(f"Deleted {deleted_count} similarity records")
            )
        
        if options['stats']:
            self.show_statistics()
            return
        
        if options['all']:
            self.stdout.write("🚀 Calculating similarities for ALL books...")
            total_similarities = service.calculate_all_similarities(
                batch_size=options['batch_size']
            )
            self.stdout.write(
                self.style.SUCCESS(f"✅ Created {total_similarities} similarity records")
            )
            
        elif options['book']:
            book_id = options['book']
            try:
                book = Book.objects.get(id=book_id)
                self.stdout.write(f"📊 Calculating similarities for: {book.title}")
                
                similarities_count = service.calculate_similarities_for_book(
                    book, batch_size=options['batch_size']
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Created {similarities_count} similarity records")
                )
                
            except Book.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"❌ Book with ID {book_id} not found")
                )
        else:
            self.stdout.write(
                self.style.WARNING("Please specify --all or --book ID or --stats")
            )
            
        # Pokaż statystyki na końcu
        if options['all'] or options['book']:
            self.show_statistics()
    
    def show_statistics(self):
        """Pokaż statystyki podobieństw"""
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write("📊 SIMILARITY STATISTICS")
        self.stdout.write("=" * 50)
        
        # Podstawowe statystyki
        total_books = Book.objects.count()
        total_similarities = BookSimilarity.objects.count()
        
        # Średnie podobieństwo
        avg_similarity = BookSimilarity.objects.aggregate(
            avg=models.Avg('cosine_similarity')
        )['avg'] or 0
        
        # Najwyższe podobieństwo
        max_similarity = BookSimilarity.objects.aggregate(
            max=models.Max('cosine_similarity')
        )['max'] or 0
        
        # Książki z największą liczbą podobieństw
        books_with_most_similarities = Book.objects.annotate(
            similarity_count=models.Count('similarities_as_book1') + models.Count('similarities_as_book2')
        ).order_by('-similarity_count')[:5]
        
        self.stdout.write(f"📚 Total books: {total_books}")
        self.stdout.write(f"🔗 Total similarities: {total_similarities}")
        self.stdout.write(f"📈 Average similarity: {avg_similarity:.4f}")
        self.stdout.write(f"🔝 Maximum similarity: {max_similarity:.4f}")
        
        if total_books > 0:
            coverage = (total_similarities / (total_books * (total_books - 1) / 2)) * 100
            self.stdout.write(f"📊 Similarity coverage: {coverage:.2f}%")
        
        self.stdout.write("\n🏆 TOP 5 BOOKS WITH MOST SIMILARITIES:")
        for i, book in enumerate(books_with_most_similarities, 1):
            similarity_count = (
                book.similarities_as_book1.count() + 
                book.similarities_as_book2.count()
            )
            self.stdout.write(f"   {i}. {book.title[:40]:40} ({similarity_count} similarities)")
        
        # Próbka najwyższych podobieństw
        top_similarities = BookSimilarity.objects.order_by('-cosine_similarity')[:5]
        self.stdout.write("\n⭐ TOP 5 HIGHEST SIMILARITIES:")
        for i, sim in enumerate(top_similarities, 1):
            self.stdout.write(
                f"   {i}. {sim.book1.title[:25]:25} ↔ {sim.book2.title[:25]:25} "
                f"({sim.cosine_similarity:.4f})"
            )