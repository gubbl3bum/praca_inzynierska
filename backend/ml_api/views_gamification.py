from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count

from .models import Badge, UserBadge, UserStatistics, Achievement, Leaderboard
from .serializers_gamification import (
    BadgeSerializer, UserBadgeSerializer, UserStatisticsSerializer,
    AchievementSerializer, LeaderboardSerializer, UserProfileGamificationSerializer
)
from .services.badge_service import BadgeService, AchievementService


# =============================================================================
# BADGES VIEWS
# =============================================================================

@api_view(['GET'])
def badges_list(request):
    """
    Get all available badges
    
    Query params:
    - category: Filter by category
    - rarity: Filter by rarity
    - include_hidden: Include hidden badges (default: false)
    """
    badges = Badge.objects.filter(is_active=True)
    
    # Filters
    category = request.GET.get('category')
    if category:
        badges = badges.filter(category=category)
    
    rarity = request.GET.get('rarity')
    if rarity:
        badges = badges.filter(rarity=rarity)
    
    include_hidden = request.GET.get('include_hidden', 'false').lower() == 'true'
    if not include_hidden:
        badges = badges.filter(is_hidden=False)
    
    # Group by category
    group_by_category = request.GET.get('group_by_category', 'false').lower() == 'true'
    
    if group_by_category:
        result = {}
        for category_choice in Badge.CATEGORY_CHOICES:
            category_key = category_choice[0]
            category_badges = badges.filter(category=category_key)
            if category_badges.exists():
                result[category_key] = {
                    'name': category_choice[1],
                    'badges': BadgeSerializer(category_badges, many=True).data
                }
        
        return Response({
            'status': 'success',
            'categories': result
        })
    else:
        serializer = BadgeSerializer(badges, many=True)
        return Response({
            'status': 'success',
            'badges': serializer.data,
            'count': badges.count()
        })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_badges(request):
    """
    Get current user's badges with progress
    
    Query params:
    - completed: Filter by completion status (true/false)
    - category: Filter by category
    """
    user = request.user
    
    # Get or create user statistics
    BadgeService.initialize_user_statistics(user)
    
    # Get badges
    badges = UserBadge.objects.filter(user=user).select_related('badge')
    
    # Filters
    completed = request.GET.get('completed')
    if completed is not None:
        badges = badges.filter(completed=completed.lower() == 'true')
    
    category = request.GET.get('category')
    if category:
        badges = badges.filter(badge__category=category)
    
    serializer = UserBadgeSerializer(badges, many=True)
    
    return Response({
        'status': 'success',
        'badges': serializer.data,
        'count': badges.count()
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def check_badges(request):
    """
    Manually trigger badge check for current user
    Returns newly earned badges that haven't been notified yet
    """
    user = request.user
    
    pending_notifications = UserBadge.objects.filter(
        user=user,
        completed=True,
        notification_sent=False
    ).select_related('badge')
    
    badges_to_notify = []
    for user_badge in pending_notifications:
        badges_to_notify.append(user_badge.badge)
        user_badge.notification_sent = True
        user_badge.save()
    
    newly_earned = BadgeService.check_and_award_badges(user)
    
    all_new_badges = badges_to_notify + newly_earned
    
    if all_new_badges:
        serializer = BadgeSerializer(all_new_badges, many=True)
        return Response({
            'status': 'success',
            'message': f'Congratulations! You earned {len(all_new_badges)} new badge(s)!',
            'new_badges': serializer.data
        })
    else:
        return Response({
            'status': 'success',
            'message': 'No new badges earned',
            'new_badges': []
        })

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def toggle_showcase_badge(request, badge_id):
    """Toggle badge showcase status"""
    user = request.user
    
    success = BadgeService.toggle_showcase_badge(user, badge_id)
    
    if success:
        user_badge = UserBadge.objects.get(user=user, badge_id=badge_id)
        return Response({
            'status': 'success',
            'is_showcased': user_badge.is_showcased
        })
    else:
        return Response({
            'status': 'error',
            'message': 'Badge not found or not completed'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def next_badges(request):
    """Get badges user is close to earning"""
    user = request.user
    limit = int(request.GET.get('limit', 5))
    
    next_badges_data = BadgeService.get_next_badges(user, limit)
    
    return Response({
        'status': 'success',
        'next_badges': next_badges_data
    })


# =============================================================================
# STATISTICS VIEWS
# =============================================================================

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_statistics(request):
    """Get current user's statistics"""
    user = request.user
    
    # Update and get statistics
    stats = BadgeService.update_user_statistics(user)
    
    serializer = UserStatisticsSerializer(stats)
    
    return Response({
        'status': 'success',
        'statistics': serializer.data
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def gamification_profile(request):
    """
    Get complete gamification profile for current user
    Includes: statistics, showcased badges, next badges, recent achievements
    """
    user = request.user
    
    # Update statistics
    stats = BadgeService.update_user_statistics(user)
    
    # Get showcased badges
    showcased = BadgeService.get_showcased_badges(user, limit=5)
    
    # Get next badges
    next_badges = BadgeService.get_next_badges(user, limit=5)
    
    # Get recent achievements
    achievements = AchievementService.get_user_achievements(user)[:5]
    
    # Get rank info
    rank_info = {}
    try:
        leaderboard_entry = Leaderboard.objects.filter(
            user=user,
            period='all_time',
            category='points'
        ).first()
        if leaderboard_entry:
            rank_info = {
                'rank': leaderboard_entry.rank,
                'total_points': stats.total_points,
                'period': 'all_time'
            }
    except:
        pass
    
    return Response({
        'status': 'success',
        'profile': {
            'statistics': UserStatisticsSerializer(stats).data,
            'showcased_badges': UserBadgeSerializer(showcased, many=True).data,
            'next_badges': next_badges,
            'recent_achievements': AchievementSerializer(achievements, many=True).data,
            'rank_info': rank_info
        }
    })


# =============================================================================
# ACHIEVEMENTS VIEWS
# =============================================================================

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_achievements(request):
    """Get all user achievements"""
    user = request.user
    
    achievements = AchievementService.get_user_achievements(user)
    serializer = AchievementSerializer(achievements, many=True)
    
    return Response({
        'status': 'success',
        'achievements': serializer.data,
        'count': achievements.count()
    })


# =============================================================================
# LEADERBOARD VIEWS
# =============================================================================

@api_view(['GET'])
def leaderboard(request):
    """
    Get leaderboard
    
    Query params:
    - period: all_time, yearly, monthly, weekly (default: all_time)
    - category: points, badges, reviews, books_read (default: points)
    - limit: Number of entries (default: 100)
    """
    period = request.GET.get('period', 'all_time')
    category = request.GET.get('category', 'points')
    limit = int(request.GET.get('limit', 100))
    
    leaderboard = Leaderboard.objects.filter(
        period=period,
        category=category
    ).select_related('user').order_by('rank')[:limit]
    
    serializer = LeaderboardSerializer(leaderboard, many=True)
    
    # Get current user rank if authenticated
    user_rank = None
    if request.user.is_authenticated:
        try:
            user_entry = Leaderboard.objects.get(
                user=request.user,
                period=period,
                category=category
            )
            user_rank = {
                'rank': user_entry.rank,
                'score': user_entry.score
            }
        except Leaderboard.DoesNotExist:
            pass
    
    return Response({
        'status': 'success',
        'leaderboard': serializer.data,
        'period': period,
        'category': category,
        'user_rank': user_rank,
        'total_entries': leaderboard.count()
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_rank(request):
    """Get current user's rank across all leaderboards"""
    user = request.user
    
    ranks = Leaderboard.objects.filter(user=user)
    
    result = {}
    for entry in ranks:
        if entry.period not in result:
            result[entry.period] = {}
        result[entry.period][entry.category] = {
            'rank': entry.rank,
            'score': entry.score,
            'updated_at': entry.updated_at
        }
    
    return Response({
        'status': 'success',
        'ranks': result
    })


# =============================================================================
# BADGE CATEGORIES
# =============================================================================

@api_view(['GET'])
def badge_categories(request):
    """Get all badge categories with counts"""
    categories = []
    
    for category_choice in Badge.CATEGORY_CHOICES:
        category_key = category_choice[0]
        category_name = category_choice[1]
        
        count = Badge.objects.filter(
            category=category_key,
            is_active=True
        ).count()
        
        categories.append({
            'key': category_key,
            'name': category_name,
            'badge_count': count
        })
    
    return Response({
        'status': 'success',
        'categories': categories
    })