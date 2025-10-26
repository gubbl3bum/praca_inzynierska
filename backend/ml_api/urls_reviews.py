from django.urls import path
from . import views_reviews

app_name = 'reviews'

urlpatterns = [
    # Book reviews
    path('book/<int:book_id>/', views_reviews.book_reviews_list, name='book_reviews_list'),
    path('<int:review_id>/', views_reviews.review_detail, name='review_detail'),
    
    # User reviews
    path('my-reviews/', views_reviews.user_reviews_list, name='user_reviews_list'),
    path('check/<int:book_id>/', views_reviews.check_user_review, name='check_user_review'),
    
    # Statistics
    path('statistics/', views_reviews.review_statistics, name='review_statistics'),
    path('highest-rated/', views_reviews.highest_rated_books, name='highest_rated_books'),
]