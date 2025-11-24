import os
import sys
import django
import random
from collections import defaultdict

sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from ml_api.models import (
    User, UserPreferences, UserPreferenceProfile, 
    BookReview, Book, Category, Author, Publisher
)
from django.db import transaction
from faker import Faker

fake = Faker()

def generate_unique_username(base_pattern, user_type):
    """
    Generate unique username with retry logic
    
    Args:
        base_pattern: Base pattern like 'reader'
        user_type: Type like 'heavy', 'specialist', etc.
    
    Returns:
        Unique username
    """
    max_attempts = 100
    
    for attempt in range(max_attempts):
        # Use larger range for better uniqueness
        random_num = random.randint(10000, 999999)
        username = f"{base_pattern}_{user_type}_{random_num}"
        
        # Check if username exists
        if not User.objects.filter(username=username).exists():
            return username
    
    # Fallback: use timestamp if all attempts failed
    import time
    timestamp = int(time.time() * 1000)
    username = f"{base_pattern}_{user_type}_{timestamp}"
    
    # If even this exists (very unlikely), add random suffix
    while User.objects.filter(username=username).exists():
        username = f"{base_pattern}_{user_type}_{timestamp}_{random.randint(1, 999)}"
    
    return username

class UserProfileGenerator:
    
    def __init__(self):
        self.books = list(Book.objects.all())
        self.categories = list(Category.objects.all())
        self.authors = list(Author.objects.all())
        self.publishers = list(Publisher.objects.all())
        
        print(f"Loaded {len(self.books)} books")
        print(f"Loaded {len(self.categories)} categories")
        print(f"Loaded {len(self.authors)} authors")
        print(f"Loaded {len(self.publishers)} publishers")
        
        # Group books by category for easier selection
        self.books_by_category = defaultdict(list)
        for book in self.books:
            for category in book.categories.all():
                self.books_by_category[category.id].append(book)
        
        # Group books by author
        self.books_by_author = defaultdict(list)
        for book in self.books:
            for author in book.authors.all():
                self.books_by_author[author.id].append(book)
    
    def create_heavy_reader(self, username_base):
        """
        Heavy reader: 40-60 reviews, diverse genres, thoughtful ratings
        """
        # ✅ POPRAWKA: Generate unique username
        username = generate_unique_username(username_base, 'heavy')
        email = f"{username}@example.com"
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password='testpassword123',
            first_name=fake.first_name(),
            last_name=fake.last_name()
        )
        
        # Preferences: 5-8 categories, varied
        preferred_cats = random.sample(self.categories, k=min(random.randint(5, 8), len(self.categories)))
        cat_weights = {str(cat.id): round(random.uniform(0.6, 1.0), 2) for cat in preferred_cats}
        
        preferred_authors = random.sample(self.authors, k=min(random.randint(3, 6), len(self.authors)))
        author_ids = [a.id for a in preferred_authors]
        
        preferred_publishers = random.sample(self.publishers, k=min(random.randint(2, 4), len(self.publishers)))
        pub_ids = [p.id for p in preferred_publishers]
        
        UserPreferenceProfile.objects.create(
            user=user,
            preferred_categories=cat_weights,
            preferred_authors=author_ids,
            preferred_publishers=pub_ids,
            min_rating_threshold=5.0,
            preferred_year_range={'min': 1980, 'max': 2024},
            completed=True
        )
        
        # Reviews: 40-60 books, normal distribution of ratings (5-9 mostly)
        num_reviews = random.randint(40, 60)
        reviewed_books = random.sample(self.books, k=min(num_reviews, len(self.books)))
        
        for book in reviewed_books:
            # Normal distribution around 7-8
            rating = int(random.gauss(7.5, 1.5))
            rating = max(1, min(10, rating))  # Clamp to 1-10
            
            # 60% chance of review text
            review_text = None
            if random.random() < 0.6:
                review_text = fake.paragraph(nb_sentences=random.randint(2, 5))
            
            BookReview.objects.create(
                user=user,
                book=book,
                rating=rating,
                review_text=review_text
            )
        
        print(f"Created heavy reader: {username} ({num_reviews} reviews)")
        return user
    
    def create_genre_specialist(self, username_base):
        """
        Genre specialist: 30-45 reviews, focused on 1-2 categories
        """
        # ✅ POPRAWKA: Generate unique username
        username = generate_unique_username(username_base, 'specialist')
        email = f"{username}@example.com"
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password='testpassword123',
            first_name=fake.first_name(),
            last_name=fake.last_name()
        )
        
        # Preferences: 1-2 dominant categories
        specialist_categories = random.sample(self.categories, k=min(2, len(self.categories)))
        cat_weights = {str(cat.id): 1.0 for cat in specialist_categories}
        
        # Add a few more with lower weights
        other_cats = random.sample(
            [c for c in self.categories if c not in specialist_categories],
            k=min(2, len(self.categories) - len(specialist_categories))
        )
        for cat in other_cats:
            cat_weights[str(cat.id)] = round(random.uniform(0.3, 0.5), 2)
        
        UserPreferenceProfile.objects.create(
            user=user,
            preferred_categories=cat_weights,
            preferred_authors=[],
            preferred_publishers=[],
            min_rating_threshold=6.0,
            preferred_year_range={'min': 2000, 'max': 2024},
            completed=True
        )
        
        # Reviews: mostly from specialist categories
        num_reviews = random.randint(30, 45)
        
        # 80% from specialist categories, 20% from others
        specialist_count = int(num_reviews * 0.8)
        other_count = num_reviews - specialist_count
        
        reviewed_books = []
        
        # Get books from specialist categories
        specialist_books = []
        for cat in specialist_categories:
            specialist_books.extend(self.books_by_category[cat.id])
        
        if specialist_books:
            reviewed_books.extend(
                random.sample(specialist_books, k=min(specialist_count, len(specialist_books)))
            )
        
        # Add some other books
        other_books = [b for b in self.books if b not in reviewed_books]
        if other_books and other_count > 0:
            reviewed_books.extend(
                random.sample(other_books, k=min(other_count, len(other_books)))
            )
        
        # Create reviews with higher ratings (they love their genre)
        for book in reviewed_books:
            rating = int(random.gauss(8.0, 1.2))
            rating = max(5, min(10, rating))  # Skewed positive
            
            review_text = None
            if random.random() < 0.5:
                review_text = fake.paragraph(nb_sentences=random.randint(2, 4))
            
            BookReview.objects.create(
                user=user,
                book=book,
                rating=rating,
                review_text=review_text
            )
        
        print(f"Created genre specialist: {username} ({len(reviewed_books)} reviews, focus: {[c.name for c in specialist_categories]})")
        return user
    
    def create_critical_reader(self, username_base):
        """
        Critical reader: 25-40 reviews, wider rating distribution, detailed reviews
        """
        # ✅ POPRAWKA: Generate unique username
        username = generate_unique_username(username_base, 'critic')
        email = f"{username}@example.com"
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password='testpassword123',
            first_name=fake.first_name(),
            last_name=fake.last_name()
        )
        
        # Preferences: varied categories, no strong preference
        preferred_cats = random.sample(self.categories, k=min(random.randint(4, 6), len(self.categories)))
        cat_weights = {str(cat.id): round(random.uniform(0.5, 0.8), 2) for cat in preferred_cats}
        
        UserPreferenceProfile.objects.create(
            user=user,
            preferred_categories=cat_weights,
            preferred_authors=[],
            preferred_publishers=[],
            min_rating_threshold=0.0,  # No threshold, reads everything
            preferred_year_range={'min': 1950, 'max': 2024},
            completed=True
        )
        
        # Reviews: wide rating distribution, more detailed
        num_reviews = random.randint(25, 40)
        reviewed_books = random.sample(self.books, k=min(num_reviews, len(self.books)))
        
        for book in reviewed_books:
            # Uniform distribution 3-9 (more critical)
            rating = random.randint(3, 9)
            
            # 80% chance of review text (critics write more)
            review_text = None
            if random.random() < 0.8:
                review_text = fake.paragraph(nb_sentences=random.randint(3, 6))
            
            BookReview.objects.create(
                user=user,
                book=book,
                rating=rating,
                review_text=review_text
            )
        
        print(f"Created critical reader: {username} ({num_reviews} reviews)")
        return user
    
    def create_enthusiast(self, username_base):
        """
        Enthusiast: 20-35 reviews, mostly high ratings, positive reviews
        """
        # ✅ POPRAWKA: Generate unique username
        username = generate_unique_username(username_base, 'enthusiast')
        email = f"{username}@example.com"
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password='testpassword123',
            first_name=fake.first_name(),
            last_name=fake.last_name()
        )
        
        # Preferences: varied but positive
        preferred_cats = random.sample(self.categories, k=min(random.randint(3, 5), len(self.categories)))
        cat_weights = {str(cat.id): round(random.uniform(0.7, 1.0), 2) for cat in preferred_cats}
        
        UserPreferenceProfile.objects.create(
            user=user,
            preferred_categories=cat_weights,
            preferred_authors=[],
            preferred_publishers=[],
            min_rating_threshold=7.0,
            preferred_year_range={'min': 2000, 'max': 2024},
            completed=True
        )
        
        # Reviews: high ratings (7-10)
        num_reviews = random.randint(20, 35)
        reviewed_books = random.sample(self.books, k=min(num_reviews, len(self.books)))
        
        for book in reviewed_books:
            # Skewed towards high ratings
            rating = int(random.gauss(8.5, 1.0))
            rating = max(7, min(10, rating))
            
            review_text = None
            if random.random() < 0.4:
                review_text = fake.paragraph(nb_sentences=random.randint(1, 3))
            
            BookReview.objects.create(
                user=user,
                book=book,
                rating=rating,
                review_text=review_text
            )
        
        print(f"Created enthusiast: {username} ({num_reviews} reviews)")
        return user
    
    def create_casual_reader(self, username_base):
        """
        Casual reader: 10-20 reviews, moderate ratings
        """
        # ✅ POPRAWKA: Generate unique username
        username = generate_unique_username(username_base, 'casual')
        email = f"{username}@example.com"
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password='testpassword123',
            first_name=fake.first_name(),
            last_name=fake.last_name()
        )
        
        # Preferences: minimal
        preferred_cats = random.sample(self.categories, k=min(random.randint(2, 3), len(self.categories)))
        cat_weights = {str(cat.id): round(random.uniform(0.5, 0.7), 2) for cat in preferred_cats}
        
        UserPreferenceProfile.objects.create(
            user=user,
            preferred_categories=cat_weights,
            preferred_authors=[],
            preferred_publishers=[],
            min_rating_threshold=5.0,
            preferred_year_range={'min': 1990, 'max': 2024},
            completed=True
        )
        
        # Reviews: fewer, moderate ratings
        num_reviews = random.randint(10, 20)
        reviewed_books = random.sample(self.books, k=min(num_reviews, len(self.books)))
        
        for book in reviewed_books:
            rating = random.randint(5, 9)
            
            review_text = None
            if random.random() < 0.3:
                review_text = fake.sentence()
            
            BookReview.objects.create(
                user=user,
                book=book,
                rating=rating,
                review_text=review_text
            )
        
        print(f"Created casual reader: {username} ({num_reviews} reviews)")
        return user


def generate_rich_users(
    num_heavy=15,
    num_specialists=20,
    num_critics=15,
    num_enthusiasts=20,
    num_casual=30
):
    """
    Generate a mix of different user types
    
    Default: 100 users total with realistic distribution
    """
    
    print("=" * 70)
    print("GENERATING RICH USER PROFILES FOR COLLABORATIVE FILTERING")
    print("=" * 70)
    
    # Check if books exist
    if Book.objects.count() == 0:
        print("❌ No books in database! Import books first.")
        return False
    
    generator = UserProfileGenerator()
    
    stats = {
        'heavy_readers': 0,
        'genre_specialists': 0,
        'critical_readers': 0,
        'enthusiasts': 0,
        'casual_readers': 0,
        'total_reviews': 0
    }
    
    username_base = "reader"
    
    # Generate heavy readers
    print(f"\n📚 Creating {num_heavy} heavy readers...")
    for i in range(num_heavy):
        try:
            generator.create_heavy_reader(username_base)
            stats['heavy_readers'] += 1
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
    
    # Generate genre specialists
    print(f"\n🎯 Creating {num_specialists} genre specialists...")
    for i in range(num_specialists):
        try:
            generator.create_genre_specialist(username_base)
            stats['genre_specialists'] += 1
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
    
    # Generate critical readers
    print(f"\n🎭 Creating {num_critics} critical readers...")
    for i in range(num_critics):
        try:
            generator.create_critical_reader(username_base)
            stats['critical_readers'] += 1
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
    
    # Generate enthusiasts
    print(f"\n⭐ Creating {num_enthusiasts} enthusiasts...")
    for i in range(num_enthusiasts):
        try:
            generator.create_enthusiast(username_base)
            stats['enthusiasts'] += 1
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
    
    # Generate casual readers
    print(f"\n📖 Creating {num_casual} casual readers...")
    for i in range(num_casual):
        try:
            generator.create_casual_reader(username_base)
            stats['casual_readers'] += 1
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
    
    # Calculate total reviews
    stats['total_reviews'] = BookReview.objects.count()
    
    # Print summary
    print("\n" + "=" * 70)
    print("✅ USER GENERATION SUMMARY")
    print("=" * 70)
    print(f"    Total users created: {sum([stats[k] for k in stats if k != 'total_reviews'])}")
    print(f"    Heavy readers: {stats['heavy_readers']} (40-60 reviews each)")
    print(f"    Genre specialists: {stats['genre_specialists']} (30-45 reviews each)")
    print(f"    Critical readers: {stats['critical_readers']} (25-40 reviews each)")
    print(f"    Enthusiasts: {stats['enthusiasts']} (20-35 reviews each)")
    print(f"    Casual readers: {stats['casual_readers']} (10-20 reviews each)")
    print(f"\n📊 Total reviews in database: {stats['total_reviews']}")
    print(f"📈 Average reviews per user: {stats['total_reviews'] / max(1, sum([stats[k] for k in stats if k != 'total_reviews'])):.1f}")
    
    print("\n🎉 Rich user generation completed!")
    
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate rich user profiles')
    parser.add_argument('--heavy', type=int, default=15, help='Number of heavy readers')
    parser.add_argument('--specialists', type=int, default=20, help='Number of genre specialists')
    parser.add_argument('--critics', type=int, default=15, help='Number of critical readers')
    parser.add_argument('--enthusiasts', type=int, default=20, help='Number of enthusiasts')
    parser.add_argument('--casual', type=int, default=30, help='Number of casual readers')
    
    args = parser.parse_args()
    
    success = generate_rich_users(
        num_heavy=args.heavy,
        num_specialists=args.specialists,
        num_critics=args.critics,
        num_enthusiasts=args.enthusiasts,
        num_casual=args.casual
    )
    
    sys.exit(0 if success else 1)