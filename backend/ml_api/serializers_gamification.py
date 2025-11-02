from rest_framework import serializers
from .models import Badge, UserBadge, UserStatistics, Achievement, Leaderboard


class BadgeSerializer(serializers.ModelSerializer):
    """Badge details serializer"""
    rarity_color = serializers.ReadOnlyField(source='get_rarity_color')
    
    class Meta:
        model = Badge
        fields = [
            'id', 'name', 'slug', 'description', 'icon',
            'category', 'rarity', 'rarity_color',
            'requirement_type', 'requirement_value',
            'points', 'is_hidden', 'order'
        ]


class UserBadgeSerializer(serializers.ModelSerializer):
    """User badge with progress"""
    badge = BadgeSerializer(read_only=True)
    progress_percentage = serializers.ReadOnlyField()
    remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = UserBadge
        fields = [
            'id', 'badge', 'progress', 'completed',
            'progress_percentage', 'remaining',
            'earned_at', 'is_showcased'
        ]
    
    def get_remaining(self, obj):
        """Calculate remaining progress"""
        if obj.completed:
            return 0
        return max(0, obj.badge.requirement_value - obj.progress)


class UserStatisticsSerializer(serializers.ModelSerializer):
    """User statistics serializer"""
    
    class Meta:
        model = UserStatistics
        fields = [
            'total_reviews', 'reviews_with_text', 'average_review_length',
            'perfect_ratings', 'harsh_ratings',
            'books_read', 'books_reading', 'books_to_read',
            'favorite_books', 'custom_lists_created',
            'unique_categories_read', 'categories_explored',
            'current_reading_streak', 'longest_reading_streak',
            'total_badges_earned', 'total_points',
            'last_activity_date', 'updated_at'
        ]


class AchievementSerializer(serializers.ModelSerializer):
    """Achievement serializer"""
    achievement_type_display = serializers.CharField(
        source='get_achievement_type_display',
        read_only=True
    )
    
    class Meta:
        model = Achievement
        fields = [
            'id', 'achievement_type', 'achievement_type_display',
            'description', 'achieved_at', 'metadata'
        ]


class LeaderboardSerializer(serializers.ModelSerializer):
    """Leaderboard entry serializer"""
    username = serializers.CharField(source='user.username', read_only=True)
    user_avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = Leaderboard
        fields = [
            'rank', 'username', 'user_avatar', 'score',
            'period', 'category', 'updated_at'
        ]
    
    def get_user_avatar(self, obj):
        """Get user avatar initial"""
        return obj.user.first_name[:1] if obj.user.first_name else obj.user.username[:1]


class UserProfileGamificationSerializer(serializers.Serializer):
    """Complete user gamification profile"""
    statistics = UserStatisticsSerializer(read_only=True)
    showcased_badges = UserBadgeSerializer(many=True, read_only=True)
    next_badges = serializers.ListField(read_only=True)
    recent_achievements = AchievementSerializer(many=True, read_only=True)
    rank_info = serializers.DictField(read_only=True)
    
    class Meta:
        fields = [
            'statistics', 'showcased_badges', 'next_badges',
            'recent_achievements', 'rank_info'
        ]