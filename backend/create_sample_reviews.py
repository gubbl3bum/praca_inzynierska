"""
Create sample reviews for users to generate user similarity data
Run once after importing books and users
"""
import os
import sys
import django
import random

sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from ml_api.models import User, Book, BookReview


def create_sample_reviews():
    """Create random reviews for users"""
    
    print("⭐ Creating sample reviews for users...")
    
    # Get all users
    users = list(User.objects.all())
    
    if not users:
        print("❌ No users found!")
        return
    
    # Get all books
    books = list(Book.objects.all())
    
    if not books:
        print("❌ No books found!")
        return
    
    print(f"👥 Found {len(users)} users")
    print(f"📚 Found {len(books)} books")
    
    created_count = 0
    
    for user in users:
        # Each user reviews 5-15 random books
        num_reviews = random.randint(5, min(15, len(books)))
        selected_books = random.sample(books, num_reviews)
        
        for book in selected_books:
            # Skip if already reviewed
            if BookReview.objects.filter(user=user, book=book).exists():
                continue
            
            # Random rating (weighted towards higher ratings)
            # 1-3: 10%, 4-6: 20%, 7-8: 40%, 9-10: 30%
            rand = random.random()
            if rand < 0.10:
                rating = random.randint(1, 3)
            elif rand < 0.30:
                rating = random.randint(4, 6)
            elif rand < 0.70:
                rating = random.randint(7, 8)
            else:
                rating = random.randint(9, 10)
            
            # Generate simple review text (optional)
            review_texts = [
                "Great book! Really enjoyed it.",
                "Interesting read, would recommend.",
                "Not bad, but could be better.",
                "Loved every page of this book!",
                "Decent book, nothing special.",
                "Amazing story and characters!",
                "Well written and engaging.",
                "A bit slow but worth reading.",
                None,  # Some reviews without text
            ]
            
            review_text = random.choice(review_texts)
            
            # Create review
            BookReview.objects.create(
                user=user,
                book=book,
                rating=rating,
                review_text=review_text
            )
            created_count += 1
        
        print(f"Created {num_reviews} reviews for {user.username}")
    
    print(f"\n🎉 Total reviews created: {created_count}")
    
    # Print statistics
    print("\n📊 Review Statistics:")
    print(f"   Total users with reviews: {User.objects.filter(reviews__isnull=False).distinct().count()}")
    print(f"   Total reviews: {BookReview.objects.count()}")
    print(f"   Average reviews per user: {BookReview.objects.count() / len(users):.1f}")


if __name__ == "__main__":
    create_sample_reviews()