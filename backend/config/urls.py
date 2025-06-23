# backend/config/urls.py - CLEAN EMERGENCY VERSION
from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

def health_check(request):
    """Simple health check endpoint"""
    return JsonResponse({
        'status': 'ok',
        'message': 'Book Recommendation System API'
    })

@api_view(['GET'])
def featured_books(request):
    """Polecane książki - działające emergency endpoint"""
    try:
        from ml_api.models import Book
        
        # Pobierz pierwsze 12 książek jako featured
        books = Book.objects.all()[:12]
        
        book_data = []
        for book in books:
            book_data.append({
                'id': book.id,
                'title': book.title,
                'authors': book.author_names if hasattr(book, 'author_names') else 'Unknown',
                'price': str(book.price) if book.price else None,
                'publish_year': book.publish_year,
                'average_rating': book.average_rating if hasattr(book, 'average_rating') else 0,
                'ratings_count': book.ratings_count if hasattr(book, 'ratings_count') else 0,
                'description': (book.description[:200] + '...') if book.description and len(book.description) > 200 else book.description,
                'cover_image_url': book.cover_image_url,
                'isbn': book.isbn,
            })
        
        return Response({
            'status': 'success',
            'count': len(book_data),
            'books': book_data
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=500)

@api_view(['GET'])
def book_list(request):
    """Lista książek z paginacją"""
    try:
        from ml_api.models import Book
        
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))
        
        start = (page - 1) * limit
        end = start + limit
        
        books = Book.objects.all()[start:end]
        total_count = Book.objects.count()
        
        book_data = []
        for book in books:
            book_data.append({
                'id': book.id,
                'title': book.title,
                'authors': book.author_names if hasattr(book, 'author_names') else 'Unknown',
                'price': str(book.price) if book.price else None,
                'publish_year': book.publish_year,
                'average_rating': book.average_rating if hasattr(book, 'average_rating') else 0,
                'ratings_count': book.ratings_count if hasattr(book, 'ratings_count') else 0,
                'description': (book.description[:200] + '...') if book.description and len(book.description) > 200 else book.description,
            })
        
        return Response({
            'status': 'success',
            'count': len(book_data),
            'total': total_count,
            'page': page,
            'limit': limit,
            'has_next': end < total_count,
            'books': book_data
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=500)

@api_view(['GET'])
def top_books(request):
    """Top 200 książek"""
    try:
        from ml_api.models import Book
        
        # Książki posortowane według roku publikacji (najnowsze = top)
        books = Book.objects.filter(publish_year__isnull=False).order_by('-publish_year')[:200]
        
        book_data = []
        for book in books:
            book_data.append({
                'id': book.id,
                'title': book.title,
                'authors': book.author_names if hasattr(book, 'author_names') else 'Unknown',
                'price': str(book.price) if book.price else None,
                'publish_year': book.publish_year,
                'average_rating': book.average_rating if hasattr(book, 'average_rating') else 0,
                'ratings_count': book.ratings_count if hasattr(book, 'ratings_count') else 0,
            })
        
        return Response({
            'status': 'success',
            'count': len(book_data),
            'books': book_data
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=500)

@api_view(['GET'])
def categories_list(request):
    """Lista kategorii"""
    try:
        from ml_api.models import Category
        
        categories = Category.objects.all()[:50]  # Pierwsze 50 kategorii
        
        category_data = []
        for cat in categories:
            category_data.append({
                'id': cat.id,
                'name': cat.name,
            })
        
        return Response({
            'status': 'success',
            'count': len(category_data),
            'categories': category_data
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=500)

def api_status(request):
    """API status endpoint"""
    try:
        from ml_api.models import Book, Author, Category, User, BookReview
        
        stats = {
            'status': 'ok',
            'books_count': Book.objects.count(),
            'authors_count': Author.objects.count(),
            'categories_count': Category.objects.count(),
            'users_count': User.objects.count(),
            'reviews_count': BookReview.objects.count(),
        }
        return JsonResponse(stats)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', health_check, name='health_check'),
    path('api/status/', api_status, name='api_status'),
    path('api/health/', health_check, name='api_health'),
    
    # WORKING ENDPOINTS - bezpośrednio w głównym urls.py
    path('api/books/featured/', featured_books, name='featured_books'),
    path('api/books/top/', top_books, name='top_books'), 
    path('api/books/', book_list, name='book_list'),
    path('api/categories/', categories_list, name='categories_list'),
    

]