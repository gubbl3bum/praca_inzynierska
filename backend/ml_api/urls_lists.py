from django.urls import path
from . import views_lists

app_name = 'lists'

urlpatterns = [
    # Book Lists
    path('', views_lists.user_book_lists, name='user_book_lists'),
    path('initialize/', views_lists.initialize_default_lists, name='initialize_default_lists'),
    path('<int:list_id>/', views_lists.book_list_detail, name='book_list_detail'),
    path('<int:list_id>/add/', views_lists.add_to_list, name='add_to_list'),
    path('<int:list_id>/items/<int:item_id>/', views_lists.list_item_detail, name='list_item_detail'),
    
    # Reading Progress
    path('progress/', views_lists.reading_progress_list, name='reading_progress_list'),
    path('progress/<int:progress_id>/', views_lists.reading_progress_detail, name='reading_progress_detail'),
    path('progress/book/<int:book_id>/', views_lists.update_reading_progress_percentage, name='update_progress'),
    
    # Quick Actions
    path('quick/favorites/<int:book_id>/', views_lists.quick_add_to_favorites, name='quick_add_to_favorites'),
    path('quick/reading/<int:book_id>/', views_lists.quick_add_to_reading, name='quick_add_to_reading'),
    path('quick/check/<int:book_id>/', views_lists.check_book_in_lists, name='check_book_in_lists'),
]