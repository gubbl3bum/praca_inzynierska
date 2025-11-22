from django.core.management.base import BaseCommand
from django.db.models import Count, Avg
from ml_api.models import Book, User, BookReview, BookSimilarity


class Command(BaseCommand):
    help = 'Display system statistics'

    def handle(self, *args, **options):
        self.stdout.write('=' * 60)
        self.stdout.write(self.style.SUCCESS('WOLFREAD SYSTEM STATISTICS'))
        self.stdout.write('=' * 60)
        
        # Books
        total_books = Book.objects.count()
        books_with_covers = Book.objects.filter(
            cover_image_url__isnull=False
        ).count()
        
        self.stdout.write(f'\nBOOKS:')
        self.stdout.write(f'   Total: {total_books}')
        self.stdout.write(f'   With covers: {books_with_covers} ({books_with_covers/total_books*100:.1f}%)')
        
        # Users
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        staff_users = User.objects.filter(is_staff=True).count()
        
        self.stdout.write(f'\nUSERS:')
        self.stdout.write(f'   Total: {total_users}')
        self.stdout.write(f'   Active: {active_users}')
        self.stdout.write(f'   Staff: {staff_users}')
        
        # Reviews
        total_reviews = BookReview.objects.count()
        avg_rating = BookReview.objects.aggregate(
            avg=Avg('rating')
        )['avg'] or 0
        
        self.stdout.write(f'\nREVIEWS:')
        self.stdout.write(f'   Total: {total_reviews}')
        self.stdout.write(f'   Average rating: {avg_rating:.2f}/10')
        
        # Similarities
        book_sims = BookSimilarity.objects.count()
        
        self.stdout.write(f'\nSIMILARITIES:')
        self.stdout.write(f'   Book similarities: {book_sims}')
        
        self.stdout.write('\n' + '=' * 60)