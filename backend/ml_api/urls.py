from django.urls import path
from . import views

urlpatterns = [
    # Istniejące endpointy ML
    path('predict/', views.prediction, name='prediction'),
    path('history/', views.prediction_history, name='prediction_history'),
    
    # Nowe endpointy dla książek
    path('books/', views.BookListView.as_view(), name='book-list'),
    path('books/<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),
    path('books/featured/', views.featured_books, name='featured-books'),
    path('books/categories/', views.book_categories, name='book-categories'),
]