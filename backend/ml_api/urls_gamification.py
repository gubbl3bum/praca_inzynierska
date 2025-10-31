from django.urls import path
from . import views_gamification

app_name = 'gamification'

urlpatterns = [
    # Badges
    path('badges/', views_gamification.badges_list, name='badges_list'),
    path('badges/my/', views_gamification.user_badges, name='user_badges'),
    path('badges/check/', views_gamification.check_badges, name='check_badges'),
    path('badges/<int:badge_id>/showcase/', views_gamification.toggle_showcase_badge, name='toggle_showcase'),
    path('badges/next/', views_gamification.next_badges, name='next_badges'),
    path('badges/categories/', views_gamification.badge_categories, name='badge_categories'),
    
    # Statistics
    path('statistics/', views_gamification.user_statistics, name='user_statistics'),
    path('profile/', views_gamification.gamification_profile, name='gamification_profile'),
    
    # Achievements
    path('achievements/', views_gamification.user_achievements, name='user_achievements'),
    
    # Leaderboard
    path('leaderboard/', views_gamification.leaderboard, name='leaderboard'),
    path('leaderboard/my-rank/', views_gamification.user_rank, name='user_rank'),
]