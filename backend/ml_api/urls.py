from django.urls import path
from . import views

urlpatterns = [
    # ML API endpoints
    path('predict/', views.prediction, name='prediction'),
    path('history/', views.prediction_history, name='prediction_history'),
    path('status/', views.api_status, name='api_status'),
    
    # Books API endpoints
    path('books/', views.books_list, name='books_list'),
    path('books/featured/', views.books_featured, name='books_featured'),
    path('books/search/', views.books_search, name='books_search'),
    path('books/<int:book_id>/', views.book_detail, name='book_detail'),
    path('books/top-rated/', views.books_top_rated, name='books_top_rated'), 
    
    # Stats endpoints (nowe)
    path('users/stats/', views.users_stats, name='users_stats'),
    path('ratings/stats/', views.ratings_stats, name='ratings_stats'),
]