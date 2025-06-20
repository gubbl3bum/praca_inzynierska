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
]