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
]