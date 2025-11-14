"""
Initialize user preferences for existing users
Run once to set up random preferences for testing
"""
import os
import sys
import django
import random

sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from ml_api.models import User, UserPreferenceProfile, Category, Author, Publisher


def initialize_random_preferences():
    """Create random preference profiles for existing users"""
    
    print("🎲 Initializing random user preferences...")
    
    # Get all data
    categories = list(Category.objects.all())
    authors = list(Author.objects.all()[:100])  # Top 100 authors
    publishers = list(Publisher.objects.all()[:50])  # Top 50 publishers
    
    if not categories:
        print("No categories found. Import books first!")
        return
    
    users = User.objects.all()
    created = 0
    
    for user in users:
        # Skip if already has profile
        if hasattr(user, 'preference_profile') and user.preference_profile.completed:
            continue
        
        # Random category preferences (3-7 categories)
        num_cats = random.randint(3, min(7, len(categories)))
        selected_cats = random.sample(categories, num_cats)
        
        cat_prefs = {}
        for cat in selected_cats:
            weight = round(random.uniform(0.3, 1.0), 2)
            cat_prefs[str(cat.id)] = weight
        
        # Random authors (0-5)
        num_authors = random.randint(0, min(5, len(authors)))
        selected_authors = random.sample(authors, num_authors) if authors else []
        author_ids = [a.id for a in selected_authors]
        
        # Random publishers (0-3)
        num_pubs = random.randint(0, min(3, len(publishers)))
        selected_pubs = random.sample(publishers, num_pubs) if publishers else []
        pub_ids = [p.id for p in selected_pubs]
        
        # Create profile
        UserPreferenceProfile.objects.update_or_create(
            user=user,
            defaults={
                'preferred_categories': cat_prefs,
                'preferred_authors': author_ids,
                'preferred_publishers': pub_ids,
                'min_rating_threshold': random.choice([0.0, 5.0, 6.0, 7.0]),
                'preferred_year_range': {
                    'min': random.choice([1950, 1980, 1990, 2000, 2010]),
                    'max': 2024
                },
                'completed': True
            }
        )
        created += 1
        print(f"Created preferences for {user.username}")
    
    print(f"\n✨ Created {created} preference profiles!")


if __name__ == "__main__":
    initialize_random_preferences()