from django.urls import path
from . import admin_views

app_name = 'admin'

urlpatterns = [
    # Dashboard & Analytics
    path('dashboard/', admin_views.admin_dashboard, name='dashboard'),
    path('analytics/', admin_views.admin_analytics, name='analytics'),
    
    # Books Management
    path('books/', admin_views.admin_books_list, name='books_list'),
    path('books/<int:book_id>/', admin_views.admin_book_detail, name='book_detail'),
    
    # Users Management
    path('users/', admin_views.admin_users_list, name='users_list'),
    path('users/<int:user_id>/', admin_views.admin_user_detail, name='user_detail'),
    
    # Authors Management
    path('authors/', admin_views.admin_authors_list, name='authors_list'),
    path('authors/<int:author_id>/', admin_views.admin_author_detail, name='author_detail'),
    
    # Categories Management
    path('categories/', admin_views.admin_categories_list, name='categories_list'),
    path('categories/<int:category_id>/', admin_views.admin_category_detail, name='category_detail'),
    
    # Reviews Management
    path('reviews/', admin_views.admin_reviews_list, name='reviews_list'),
    path('reviews/<int:review_id>/delete/', admin_views.admin_review_delete, name='review_delete'),
    
    # Bulk Actions
    path('bulk/delete-books/', admin_views.admin_bulk_delete_books, name='bulk_delete_books'),
    path('bulk/update-books/', admin_views.admin_bulk_update_books, name='bulk_update_books'),
    
    # System Actions
    path('system/recalculate-similarities/', admin_views.admin_recalculate_similarities, name='recalculate_similarities'),
    path('system/recalculate-user-similarities/', admin_views.admin_recalculate_user_similarities, name='recalculate_user_similarities'),
    path('system/check-badges/', admin_views.admin_check_all_badges, name='check_badges'),
    path('system/cleanup/', admin_views.admin_cleanup_data, name='cleanup_data'),
    
    # Export
    path('export/', admin_views.admin_export_data, name='export_data'),

    # Badges Management
    path('badges/', admin_views.admin_badges_list, name='badges_list'),
    path('badges/<int:badge_id>/', admin_views.admin_badge_detail, name='badge_detail'),
    path('badges/<int:badge_id>/toggle-active/', admin_views.admin_badge_toggle_active, name='badge_toggle_active'),
    path('badges/<int:badge_id>/award/', admin_views.admin_badge_award_manually, name='badge_award_manually'),
    path('badges/<int:badge_id>/revoke/', admin_views.admin_badge_revoke, name='badge_revoke'),
    path('badges/categories/', admin_views.admin_badge_categories, name='badge_categories'),
    path('badges/rarities/', admin_views.admin_badge_rarities, name='badge_rarities'),
    path('badges/leaderboard/', admin_views.admin_badge_leaderboard, name='badge_leaderboard'),
    path('bulk/update-badges/', admin_views.admin_badge_bulk_update, name='bulk_update_badges'),
]