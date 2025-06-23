# backend/ml_api/urls.py
from django.urls import path
from . import views

app_name = 'ml_api'

urlpatterns = [
    # Lista wszystkich książek z filtrowaniem i paginacją
    path('books/', views.book_list, name='book_list'),
    
    # Polecane książki 
    path('books/featured/', views.featured_books, name='featured_books'),
    
    # Top książki 
    path('books/top/', views.top_books, name='top_books'),
    
    # Szczegóły książki
    path('books/<int:book_id>/', views.book_detail, name='book_detail'),
    
    # Lista kategorii
    path('categories/', views.categories_list, name='categories_list'),
    
    # Statystyki systemu
    path('stats/', views.stats, name='stats'),
]