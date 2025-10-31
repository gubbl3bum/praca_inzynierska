from django.db.models import Count, Q, Avg
from django.db.models.functions import Length 
from django.utils import timezone
from datetime import datetime, timedelta
from ..models import (
    Badge, UserBadge, UserStatistics, Achievement,
    BookReview, ReadingProgress, BookList
)


class BadgeService:
    """
    Service for checking and awarding badges to users
    """
    
    @staticmethod
    def initialize_user_statistics(user):
        """Create or get user statistics"""
        stats, created = UserStatistics.objects.get_or_create(user=user)
        if created:
            BadgeService.update_user_statistics(user)
        return stats
    
    @staticmethod
    def update_user_statistics(user):
        """Update all user statistics"""
        stats = UserStatistics.objects.get_or_create(user=user)[0]
        
        # Reviews statistics
        reviews = BookReview.objects.filter(user=user)
        stats.total_reviews = reviews.count()
        stats.reviews_with_text = reviews.exclude(review_text__isnull=True).exclude(review_text='').count()
        
        review_lengths = [len(r.review_text or '') for r in reviews]
        stats.average_review_length = sum(review_lengths) // len(review_lengths) if review_lengths else 0
        
        stats.perfect_ratings = reviews.filter(rating=10).count()
        stats.harsh_ratings = reviews.filter(rating__lte=3).count()
        
        # Reading statistics
        progress = ReadingProgress.objects.filter(user=user)
        stats.books_read = progress.filter(status='finished').count()
        stats.books_reading = progress.filter(status='reading').count()
        
        # Collection statistics
        lists = BookList.objects.filter(user=user)
        stats.favorite_books = lists.filter(list_type='favorites').first()
        stats.favorite_books = stats.favorite_books.items.count() if stats.favorite_books else 0
        stats.custom_lists_created = lists.filter(list_type='custom').count()
        
        # Discovery statistics
        read_books = progress.filter(status='finished').values_list('book_id', flat=True)
        from ..models import Book
        categories = Book.objects.filter(id__in=read_books).values_list('categories__id', flat=True).distinct()
        stats.unique_categories_read = len(set(categories))
        stats.categories_explored = list(set(categories))
        
        # Badges
        stats.total_badges_earned = UserBadge.objects.filter(user=user, completed=True).count()
        stats.total_points = sum(
            ub.badge.points for ub in UserBadge.objects.filter(user=user, completed=True).select_related('badge')
        )
        
        stats.save()
        return stats
    
    @staticmethod
    def check_and_award_badges(user, trigger_type=None):
        """
        Check all badges and award new ones
        
        Args:
            user: User object
            trigger_type: Optional specific trigger (e.g., 'review_created', 'book_finished')
        
        Returns:
            List of newly earned badges
        """
        stats = BadgeService.update_user_statistics(user)
        newly_earned = []
        
        # Get all active badges
        badges = Badge.objects.filter(is_active=True)
        
        # POPRAWIONE: Lepsze filtrowanie po trigger_type
        # Mapowanie triggerów na typy wymagań
        trigger_mapping = {
            'review_created': ['review_count', 'review_perfect_count', 'review_harsh_count', 'review_detailed_count'],
            'books_read': ['books_read', 'books_in_month', 'books_in_year', 'night_reading', 'early_reading', 'weekend_books'],
            'favorite_count': ['favorite_count'],
            'custom_list': ['custom_list_count'],
            'custom_list_count': ['custom_list_count'],
            'categories_explored': ['categories_explored', 'non_top100_read']
        }
        
        if trigger_type and trigger_type in trigger_mapping:
            badges = badges.filter(requirement_type__in=trigger_mapping[trigger_type])
        
        for badge in badges:
            # Check if user already has this badge
            user_badge, created = UserBadge.objects.get_or_create(
                user=user,
                badge=badge,
                defaults={'progress': 0}
            )
            
            if user_badge.completed:
                continue  # Already earned
            
            # Check badge requirements
            current_progress = BadgeService._get_badge_progress(user, badge, stats)
            user_badge.progress = current_progress
            
            # Check if badge is earned
            if current_progress >= badge.requirement_value:
                user_badge.completed = True
                user_badge.earned_at = timezone.now()
                newly_earned.append(badge)
                
                # Update user stats
                stats.total_badges_earned += 1
                stats.total_points += badge.points
                stats.save()
            
            user_badge.save()
        
        return newly_earned
    
    @staticmethod
    def _get_badge_progress(user, badge, stats):
        """
        Calculate current progress for a specific badge
        
        Returns:
            Current progress value
        """
        req_type = badge.requirement_type
        
        # Reviews category
        if req_type == 'review_count':
            return stats.total_reviews
        elif req_type == 'review_perfect_count':
            return stats.perfect_ratings
        elif req_type == 'review_harsh_count':
            return stats.harsh_ratings
        elif req_type == 'review_detailed_count':
            # POPRAWIONE: Używamy zaimportowanego Length
            return BookReview.objects.filter(user=user).annotate(
                text_length=Length('review_text')
            ).filter(text_length__gte=500).count()
        
        # Reading category
        elif req_type == 'books_read':
            return stats.books_read
        elif req_type == 'reading_streak':
            return stats.current_reading_streak
        elif req_type == 'books_in_month':
            one_month_ago = timezone.now() - timedelta(days=30)
            return ReadingProgress.objects.filter(
                user=user,
                status='finished',
                finished_at__gte=one_month_ago
            ).count()
        elif req_type == 'books_in_year':
            one_year_ago = timezone.now() - timedelta(days=365)
            return ReadingProgress.objects.filter(
                user=user,
                status='finished',
                finished_at__gte=one_year_ago
            ).count()
        
        # Collections category
        elif req_type == 'favorite_count':
            return stats.favorite_books
        elif req_type == 'custom_list_count':
            return stats.custom_lists_created
        
        # Discovery category
        elif req_type == 'categories_explored':
            return stats.unique_categories_read
        elif req_type == 'non_top100_read':
            # Books outside top 100 by rating
            from ..models import Book
            # POPRAWIONE: Używamy aggregate zamiast property
            from django.db.models import Avg, Count
            top_100_ids = Book.objects.annotate(
                avg_rating=Avg('reviews__rating'),
                review_count=Count('reviews')
            ).filter(review_count__gt=0).order_by('-avg_rating')[:100].values_list('id', flat=True)
            
            return ReadingProgress.objects.filter(
                user=user,
                status='finished'
            ).exclude(book_id__in=top_100_ids).count()
        
        # Time-based category
        elif req_type == 'weekend_books':
            return ReadingProgress.objects.filter(
                user=user,
                status='finished'
            ).extra(
                where=["EXTRACT(DOW FROM finished_at) IN (0, 6)"]
            ).count()
        
        # Special conditions
        elif req_type == 'night_reading':
            return ReadingProgress.objects.filter(
                user=user,
                status='finished'
            ).extra(
                where=["EXTRACT(HOUR FROM finished_at) >= 22 OR EXTRACT(HOUR FROM finished_at) <= 6"]
            ).count()
        elif req_type == 'early_reading':
            return ReadingProgress.objects.filter(
                user=user,
                status='finished'
            ).extra(
                where=["EXTRACT(HOUR FROM finished_at) >= 5 AND EXTRACT(HOUR FROM finished_at) <= 9"]
            ).count()
        
        return 0
    
    @staticmethod
    def get_user_badges(user, completed_only=False):
        """Get all badges for user with progress"""
        query = UserBadge.objects.filter(user=user).select_related('badge')
        
        if completed_only:
            query = query.filter(completed=True)
        
        return query.order_by('-completed', '-earned_at')
    
    @staticmethod
    def get_showcased_badges(user, limit=5):
        """Get user's showcased badges for profile display"""
        return UserBadge.objects.filter(
            user=user,
            completed=True,
            is_showcased=True
        ).select_related('badge').order_by('-earned_at')[:limit]
    
    @staticmethod
    def toggle_showcase_badge(user, badge_id):
        """
        Toggle badge showcase status
        Max 5 badges can be showcased at once
        """
        try:
            user_badge = UserBadge.objects.get(
                user=user,
                badge_id=badge_id,
                completed=True
            )
            
            if user_badge.is_showcased:
                # Remove from showcase
                user_badge.is_showcased = False
            else:
                # Check limit
                showcased_count = UserBadge.objects.filter(
                    user=user,
                    is_showcased=True
                ).count()
                
                if showcased_count >= 5:
                    return False  # Max limit reached
                
                user_badge.is_showcased = True
            
            user_badge.save()
            return True
        except UserBadge.DoesNotExist:
            return False
    
    @staticmethod
    def get_next_badges(user, limit=5):
        """
        Get badges user is close to earning
        Returns badges ordered by completion percentage (descending)
        """
        stats = BadgeService.update_user_statistics(user)
        
        # Get all incomplete badges with progress
        incomplete_badges = UserBadge.objects.filter(
            user=user,
            completed=False
        ).select_related('badge')
        
        # Calculate progress for each
        badge_progress = []
        for user_badge in incomplete_badges:
            if user_badge.badge.requirement_value > 0:
                progress_pct = (user_badge.progress / user_badge.badge.requirement_value) * 100
                badge_progress.append({
                    'badge': user_badge.badge,
                    'progress': user_badge.progress,
                    'required': user_badge.badge.requirement_value,
                    'progress_percentage': round(progress_pct, 1),
                    'remaining': user_badge.badge.requirement_value - user_badge.progress
                })
        
        # Sort by progress percentage (highest first)
        badge_progress.sort(key=lambda x: x['progress_percentage'], reverse=True)
        
        return badge_progress[:limit]


class AchievementService:
    """
    Service for managing one-time achievements
    """
    
    @staticmethod
    def award_achievement(user, achievement_type, description, metadata=None):
        """
        Award an achievement to user (idempotent)
        """
        achievement, created = Achievement.objects.get_or_create(
            user=user,
            achievement_type=achievement_type,
            defaults={
                'description': description,
                'metadata': metadata or {}
            }
        )
        return achievement, created
    
    @staticmethod
    def get_user_achievements(user):
        """Get all user achievements"""
        return Achievement.objects.filter(user=user).order_by('-achieved_at')
    
    @staticmethod
    def has_achievement(user, achievement_type):
        """Check if user has specific achievement"""
        return Achievement.objects.filter(
            user=user,
            achievement_type=achievement_type
        ).exists()


# DODANE: Funkcja pomocnicza do inicjalizacji odznak
def initialize_badges():
    """
    Initialize all badges in the database
    Call this from management command or in ready() method
    """
    badges_data = [
        # === REVIEWS CATEGORY ===
        {
            'name': 'First Review',
            'slug': 'first-review',
            'description': 'Write your first book review',
            'icon': '✍️',
            'category': 'reviews',
            'rarity': 'common',
            'requirement_type': 'review_count',
            'requirement_value': 1,
            'points': 10,
            'order': 1
        },
        {
            'name': 'Review Enthusiast',
            'slug': 'review-enthusiast',
            'description': 'Write 10 book reviews',
            'icon': '📝',
            'category': 'reviews',
            'rarity': 'common',
            'requirement_type': 'review_count',
            'requirement_value': 10,
            'points': 50,
            'order': 2
        },
        {
            'name': 'Critic',
            'slug': 'critic',
            'description': 'Write 25 book reviews',
            'icon': '🎭',
            'category': 'reviews',
            'rarity': 'rare',
            'requirement_type': 'review_count',
            'requirement_value': 25,
            'points': 100,
            'order': 3
        },
        {
            'name': 'Master Reviewer',
            'slug': 'master-reviewer',
            'description': 'Write 50 book reviews',
            'icon': '👑',
            'category': 'reviews',
            'rarity': 'epic',
            'requirement_type': 'review_count',
            'requirement_value': 50,
            'points': 250,
            'order': 4
        },
        {
            'name': 'Perfect Score',
            'slug': 'perfect-score',
            'description': 'Give 10 perfect ratings (10/10)',
            'icon': '⭐',
            'category': 'reviews',
            'rarity': 'rare',
            'requirement_type': 'review_perfect_count',
            'requirement_value': 10,
            'points': 75,
            'order': 5
        },
        {
            'name': 'Harsh Critic',
            'slug': 'harsh-critic',
            'description': 'Give 5 low ratings (1-3/10)',
            'icon': '😤',
            'category': 'reviews',
            'rarity': 'rare',
            'requirement_type': 'review_harsh_count',
            'requirement_value': 5,
            'points': 50,
            'order': 6
        },
        
        # === READING CATEGORY ===
        {
            'name': 'Bookworm',
            'slug': 'bookworm',
            'description': 'Finish reading 10 books',
            'icon': '🐛',
            'category': 'reading',
            'rarity': 'common',
            'requirement_type': 'books_read',
            'requirement_value': 10,
            'points': 50,
            'order': 1
        },
        {
            'name': 'Library Builder',
            'slug': 'library-builder',
            'description': 'Finish reading 25 books',
            'icon': '📚',
            'category': 'reading',
            'rarity': 'rare',
            'requirement_type': 'books_read',
            'requirement_value': 25,
            'points': 100,
            'order': 2
        },
        {
            'name': 'Reading Champion',
            'slug': 'reading-champion',
            'description': 'Finish reading 50 books',
            'icon': '🏆',
            'category': 'reading',
            'rarity': 'epic',
            'requirement_type': 'books_read',
            'requirement_value': 50,
            'points': 250,
            'order': 3
        },
        {
            'name': 'Night Owl',
            'slug': 'night-owl',
            'description': 'Finish a book between 10 PM and 6 AM',
            'icon': '🌙',
            'category': 'reading',
            'rarity': 'rare',
            'requirement_type': 'night_reading',
            'requirement_value': 1,
            'points': 25,
            'order': 4
        },
        {
            'name': 'Early Bird',
            'slug': 'early-bird',
            'description': 'Finish a book between 5 AM and 9 AM',
            'icon': '☀️',
            'category': 'reading',
            'rarity': 'rare',
            'requirement_type': 'early_reading',
            'requirement_value': 1,
            'points': 25,
            'order': 5
        },
        
        # === COLLECTIONS CATEGORY ===
        {
            'name': 'Favorite Finder',
            'slug': 'favorite-finder',
            'description': 'Add 5 books to favorites',
            'icon': '❤️',
            'category': 'collections',
            'rarity': 'common',
            'requirement_type': 'favorite_count',
            'requirement_value': 5,
            'points': 25,
            'order': 1
        },
        {
            'name': 'Collection Master',
            'slug': 'collection-master',
            'description': 'Add 20 books to favorites',
            'icon': '💝',
            'category': 'collections',
            'rarity': 'rare',
            'requirement_type': 'favorite_count',
            'requirement_value': 20,
            'points': 75,
            'order': 2
        },
        {
            'name': 'List Creator',
            'slug': 'list-creator',
            'description': 'Create 3 custom lists',
            'icon': '📋',
            'category': 'collections',
            'rarity': 'common',
            'requirement_type': 'custom_list_count',
            'requirement_value': 3,
            'points': 30,
            'order': 3
        },
        {
            'name': 'Organized Reader',
            'slug': 'organized-reader',
            'description': 'Create 10 custom lists',
            'icon': '🎯',
            'category': 'collections',
            'rarity': 'rare',
            'requirement_type': 'custom_list_count',
            'requirement_value': 10,
            'points': 100,
            'order': 4
        },
        
        # === DISCOVERY CATEGORY ===
        {
            'name': 'Explorer',
            'slug': 'explorer',
            'description': 'Read books from 3 different categories',
            'icon': '🗺️',
            'category': 'discovery',
            'rarity': 'common',
            'requirement_type': 'categories_explored',
            'requirement_value': 3,
            'points': 30,
            'order': 1
        },
        {
            'name': 'Category Explorer',
            'slug': 'category-explorer',
            'description': 'Read books from 5 different categories',
            'icon': '🌍',
            'category': 'discovery',
            'rarity': 'rare',
            'requirement_type': 'categories_explored',
            'requirement_value': 5,
            'points': 75,
            'order': 2
        },
        {
            'name': 'Genre Master',
            'slug': 'genre-master',
            'description': 'Read books from 10 different categories',
            'icon': '🌌',
            'category': 'discovery',
            'rarity': 'epic',
            'requirement_type': 'categories_explored',
            'requirement_value': 10,
            'points': 150,
            'order': 3
        },
        {
            'name': 'Hidden Gem Finder',
            'slug': 'hidden-gem-finder',
            'description': 'Read a book outside the top 100',
            'icon': '🔍',
            'category': 'discovery',
            'rarity': 'rare',
            'requirement_type': 'non_top100_read',
            'requirement_value': 1,
            'points': 50,
            'order': 4
        },
        
        # === TIME CATEGORY ===
        {
            'name': 'Weekend Warrior',
            'slug': 'weekend-warrior',
            'description': 'Finish 3 books on weekends',
            'icon': '🎉',
            'category': 'time',
            'rarity': 'common',
            'requirement_type': 'weekend_books',
            'requirement_value': 3,
            'points': 40,
            'order': 1
        },
        {
            'name': 'Monthly Reader',
            'slug': 'monthly-reader',
            'description': 'Read at least 4 books in a month',
            'icon': '📅',
            'category': 'time',
            'rarity': 'rare',
            'requirement_type': 'books_in_month',
            'requirement_value': 4,
            'points': 75,
            'order': 2
        },
        {
            'name': 'Year of Reading',
            'slug': 'year-of-reading',
            'description': 'Read 52 books in a year',
            'icon': '🎊',
            'category': 'time',
            'rarity': 'legendary',
            'requirement_type': 'books_in_year',
            'requirement_value': 52,
            'points': 500,
            'order': 3
        },
        {
            'name': 'Reading Streak',
            'slug': 'reading-streak',
            'description': 'Read for 7 days in a row',
            'icon': '🏃',
            'category': 'time',
            'rarity': 'epic',
            'requirement_type': 'reading_streak',
            'requirement_value': 7,
            'points': 100,
            'order': 4
        },
        
        # === SOCIAL CATEGORY ===
        {
            'name': 'Quality Contributor',
            'slug': 'quality-contributor',
            'description': 'Write 10 detailed reviews (500+ words)',
            'icon': '🌟',
            'category': 'social',
            'rarity': 'epic',
            'requirement_type': 'review_detailed_count',
            'requirement_value': 10,
            'points': 200,
            'order': 1
        },
    ]
    
    created_count = 0
    for badge_data in badges_data:
        badge, created = Badge.objects.get_or_create(
            slug=badge_data['slug'],
            defaults=badge_data
        )
        if created:
            created_count += 1
    
    print(f"✅ Initialized {created_count} new badges ({len(badges_data)} total)")
    return created_count