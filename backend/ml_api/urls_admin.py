from django.urls import path
from . import views_admin

app_name = 'admin_api'

urlpatterns = [
    # Dashboard
    path('dashboard/stats/', views_admin.admin_dashboard_stats, name='dashboard_stats'),
    path('system/health/', views_admin.system_health, name='system_health'),
    
    # Similarity Management
    path('similarities/books/recalculate/', views_admin.recalculate_book_similarities, name='recalculate_book_similarities'),
    path('similarities/users/recalculate/', views_admin.recalculate_user_similarities, name='recalculate_user_similarities'),
    
    # User Management
    path('users/', views_admin.user_management_list, name='user_management_list'),
    path('users/<int:user_id>/toggle-status/', views_admin.toggle_user_status, name='toggle_user_status'),
    
    # Books Management
    path('books/', views_admin.books_management, name='books_management'),
    path('books/<int:book_id>/', views_admin.book_detail, name='book_detail'),
    
    # Reviews Management
    path('reviews/', views_admin.reviews_management, name='reviews_management'),
    path('reviews/<int:review_id>/', views_admin.delete_review, name='delete_review'),
    
    # Badges Management
    path('badges/', views_admin.badges_management, name='badges_management'),
    path('badges/<int:badge_id>/', views_admin.badge_detail, name='badge_detail'),
    
    # Categories Management
    path('categories/', views_admin.categories_management, name='categories_management'),
    path('categories/<int:category_id>/', views_admin.category_detail, name='category_detail'),
    
    # AUTHORS MANAGEMENT
    path('authors/', views_admin.authors_management, name='authors_management'),
    path('authors/<int:author_id>/', views_admin.author_detail, name='author_detail'),
    
    #  PUBLISHERS MANAGEMENT
    path('publishers/', views_admin.publishers_management, name='publishers_management'),
    path('publishers/<int:publisher_id>/', views_admin.publisher_detail, name='publisher_detail'),
]