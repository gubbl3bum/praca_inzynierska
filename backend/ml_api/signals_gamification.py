from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import BookReview, ReadingProgress, BookList, BookListItem
from .services.badge_service import BadgeService, AchievementService


@receiver(post_save, sender=BookReview)
def check_badges_after_review(sender, instance, created, **kwargs):
    """Check badges after creating/updating a review"""
    if created:
        # New review created
        BadgeService.check_and_award_badges(instance.user, trigger_type='review_created')
        
        # Award first review achievement
        if instance.user.reviews.count() == 1:
            AchievementService.award_achievement(
                user=instance.user,
                achievement_type='first_review',
                description='Wrote your first book review',
                metadata={'book_id': instance.book.id}
            )


@receiver(post_save, sender=ReadingProgress)
def check_badges_after_reading(sender, instance, created, **kwargs):
    """Check badges after updating reading progress"""
    if instance.status == 'finished':
        BadgeService.check_and_award_badges(instance.user, trigger_type='books_read')
        
        # Update reading streak
        stats = BadgeService.initialize_user_statistics(instance.user)
        stats.update_streak()
        
        # Award first book achievement
        if instance.user.reading_progress.filter(status='finished').count() == 1:
            AchievementService.award_achievement(
                user=instance.user,
                achievement_type='first_book_read',
                description='Finished your first book',
                metadata={'book_id': instance.book.id}
            )


@receiver(post_save, sender=BookListItem)
def check_badges_after_list_addition(sender, instance, created, **kwargs):
    """Check badges after adding book to list"""
    if created:
        print(f" Signal: Book added to list {instance.book_list.name}")
        # Check favorite badges
        if instance.book_list.list_type == 'favorites':
            print(f"Checking favorite badges for user {instance.book_list.user.username}")
            BadgeService.check_and_award_badges(instance.book_list.user, trigger_type='favorite_count')
        
        # Check collection badges
        BadgeService.check_and_award_badges(instance.book_list.user, trigger_type='custom_list')


@receiver(post_save, sender=BookList)
def check_badges_after_list_creation(sender, instance, created, **kwargs):
    """Check badges after creating a list"""
    if created and instance.list_type == 'custom':
        BadgeService.check_and_award_badges(instance.user, trigger_type='custom_list_count')
