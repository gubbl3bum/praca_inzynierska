from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from ml_api import views_lists
import json

from ml_api.views import book_recommendations, similarity_stats, recalculate_similarities

def api_root(request):
    return JsonResponse({
        'message': 'WolfRead API',
        'version': '1.0',
        'endpoints': {
            'admin': '/admin/',
            'books': '/api/books/',
            'categories': '/api/categories/',
            'auth': '/api/auth/',
            'lists': '/api/lists/',
            'status': '/api/status/',
        }
    })

def health_check(request):
    """Simple health check endpoint"""
    return JsonResponse({
        'status': 'ok',
        'message': 'Book Recommendation System API'
    })

@api_view(['GET'])
def featured_books(request):
    """Featured books for the home page"""
    try:
        from ml_api.models import Book
        
        # Top rated books (first 4)
        top_rated = Book.objects.annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ).filter(review_count__gte=1).order_by('-avg_rating')[:4]
        
        # Recent books (first 4)
        recent = Book.objects.order_by('-created_at')[:4]
        
        # Popular books (most reviews, first 4)  
        popular = Book.objects.annotate(
            review_count=Count('reviews')
        ).order_by('-review_count')[:4]
        
        def book_to_dict(book):
            return {
                'id': book.id,
                'title': book.title,
                'authors': book.author_names,
                'price': str(book.price) if book.price else None,
                'publish_year': book.publish_year,
                'average_rating': float(book.average_rating) if book.average_rating else 0,
                'ratings_count': book.ratings_count,
                'description': (book.description[:200] + '...') if book.description and len(book.description) > 200 else book.description,
                'cover_image_url': book.cover_image_url,
                'isbn': book.isbn,
                'categories': [cat.name for cat in book.categories.all()],
            }
        
        return Response({
            'status': 'success',
            'top_rated': [book_to_dict(book) for book in top_rated],
            'recent': [book_to_dict(book) for book in recent], 
            'popular': [book_to_dict(book) for book in popular]
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e),
            'top_rated': [],
            'recent': [],
            'popular': []
        }, status=500)

@api_view(['GET'])
def book_list(request):
    """Book list with pagination and filtering"""
    try:
        from ml_api.models import Book
        
        # Parameters from the request
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        search = request.GET.get('search', '').strip()
        category = request.GET.get('category', '').strip()
        author = request.GET.get('author', '').strip()
        year_from = request.GET.get('year_from', '').strip()
        year_to = request.GET.get('year_to', '').strip()
        rating_min = request.GET.get('rating_min', '').strip()
        sort = request.GET.get('sort', '-created_at')
        
        # Building a query
        books = Book.objects.all()
        
        # Filtration
        if search:
            books = books.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search) |
                Q(bookauthor__author__first_name__icontains=search) |
                Q(bookauthor__author__last_name__icontains=search)
            )
        
        if category:
            books = books.filter(bookcategory__category__name__icontains=category)
            
        if author:
            books = books.filter(
                Q(bookauthor__author__first_name__icontains=author) |
                Q(bookauthor__author__last_name__icontains=author)
            )
            
        if year_from:
            try:
                books = books.filter(publish_year__gte=int(year_from))
            except ValueError:
                pass
                
        if year_to:
            try:
                books = books.filter(publish_year__lte=int(year_to))
            except ValueError:
                pass
                
        if rating_min:
            try:
                min_rating = float(rating_min)
                books = books.annotate(avg_rating=Avg('reviews__rating')).filter(avg_rating__gte=min_rating)
            except ValueError:
                pass
        
        # Remove duplicates
        books = books.distinct()
        
        # Sorting
        if sort == 'title':
            books = books.order_by('title')
        elif sort == '-title':
            books = books.order_by('-title')
        elif sort == 'author':
            books = books.order_by('bookauthor__author__last_name')
        elif sort == '-author':
            books = books.order_by('-bookauthor__author__last_name')
        elif sort == 'average_rating':
            books = books.annotate(avg_rating=Avg('reviews__rating')).order_by('avg_rating')
        elif sort == '-average_rating':
            books = books.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
        else:
            books = books.order_by(sort)
        
        # Pagination
        paginator = Paginator(books, page_size)
        page_obj = paginator.get_page(page)
        
        def book_to_dict(book):
            return {
                'id': book.id,
                'title': book.title,
                'authors': book.author_names,
                'price': str(book.price) if book.price else None,
                'publish_year': book.publish_year,
                'average_rating': float(book.average_rating) if book.average_rating else 0,
                'ratings_count': book.ratings_count,
                'description': (book.description[:200] + '...') if book.description and len(book.description) > 200 else book.description,
                'cover_image_url': book.cover_image_url,
                'isbn': book.isbn,
                'categories': [cat.name for cat in book.categories.all()],
            }
        
        return Response({
            'status': 'success',
            'results': [book_to_dict(book) for book in page_obj],
            'count': paginator.count,
            'num_pages': paginator.num_pages,
            'current_page': page,
            'page_size': page_size,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
            'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=500)

@api_view(['GET'])
def top_rated_books(request):
    """Top books with the best ratings"""
    try:
        from ml_api.models import Book
        
        # Parameters
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        filter_type = request.GET.get('filter', 'all')
        
        # Building a query - only books with ratings
        books = Book.objects.annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ).filter(review_count__gte=1)
        
        # Temporal filtering
        if filter_type == 'recent':
            books = books.filter(publish_year__gte=2019)  # Last 5 years
        elif filter_type == 'classic':
            books = books.filter(publish_year__lt=2000)
        
        # Sort by average rating
        books = books.order_by('-avg_rating', '-review_count')
        
        # Pagination
        paginator = Paginator(books, page_size)
        page_obj = paginator.get_page(page)
        
        def book_to_dict(book):
            return {
                'id': book.id,
                'title': book.title,
                'authors': book.author_names,
                'author': book.author_names.split(',')[0] if book.author_names else 'Unknown',
                'price': str(book.price) if book.price else None,
                'publish_year': book.publish_year,
                'publication_year': book.publish_year,  # alias
                'average_rating': float(book.avg_rating) if hasattr(book, 'avg_rating') and book.avg_rating else 0,
                'ratings_count': book.review_count if hasattr(book, 'review_count') else 0,
                'description': (book.description[:200] + '...') if book.description and len(book.description) > 200 else book.description,
                'cover_image_url': book.cover_image_url,
                'best_cover_medium': book.cover_image_url,
                'cover_url': book.cover_image_url,  # alias
                'image_url_m': book.cover_image_url,  # alias
                'isbn': book.isbn,
                'categories': [cat.name for cat in book.categories.all()],
                'publisher': book.publisher.name if book.publisher else None,
            }
        
        return Response({
            'status': 'success',
            'results': [book_to_dict(book) for book in page_obj],
            'count': paginator.count,
            'num_pages': paginator.num_pages,
            'current_page': page,
            'page_size': page_size,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
            'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=500)

@api_view(['GET'])
def book_detail(request, book_id):
    """Details of a single book"""
    try:
        from ml_api.models import Book
        
        book = Book.objects.get(id=book_id)
        
        book_data = {
            'id': book.id,
            'title': book.title,
            'authors': [{'name': author.full_name} for author in book.authors.all()],
            'author': book.author_names,
            'description': book.description,
            'keywords': book.keywords,
            'price': str(book.price) if book.price else None,
            'publish_year': book.publish_year,
            'publication_year': book.publish_year,
            'publish_month': book.publish_month,
            'average_rating': float(book.average_rating) if book.average_rating else 0,
            'ratings_count': book.ratings_count,
            'cover_image_url': book.cover_image_url,
            'best_cover_large': book.cover_image_url,
            'best_cover_medium': book.cover_image_url,
            'image_url_l': book.cover_image_url,
            'image_url_m': book.cover_image_url,
            'isbn': book.isbn,
            'categories': [cat.name for cat in book.categories.all()],
            'category_names': [cat.name for cat in book.categories.all()],
            'publisher': {'name': book.publisher.name} if book.publisher else None,
            'created_at': book.created_at,
            'updated_at': book.updated_at,
        }
        
        return Response({
            'status': 'success',
            **book_data
        })
    except Book.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Book not found'
        }, status=404)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=500)

@api_view(['GET'])
def categories_list(request):
    """List of categories"""
    try:
        from ml_api.models import Category
        
        categories = Category.objects.all()[:50]
        
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
    
    # API ENDPOINTS
    path('api/status/', api_status, name='api_status'),
    path('api/health/', health_check, name='api_health'),
    
    # BOOOKS API
    path('api/books/featured/', featured_books, name='featured_books'),
    path('api/books/top-rated/', top_rated_books, name='top_rated_books'),
    path('api/books/<int:book_id>/', book_detail, name='book_detail'),
    path('api/books/', book_list, name='book_list'),
    path('api/categories/', categories_list, name='categories_list'),
    
    # SIMILARITY ENDPOINTS
    path('api/books/<int:book_id>/recommendations/', book_recommendations, name='book_recommendations'),
    path('api/books/<int:book_id>/similar/', book_recommendations, name='similar_books'),
    path('api/similarities/stats/', similarity_stats, name='similarity_stats'),
    path('api/similarities/recalculate/', recalculate_similarities, name='recalculate_all_similarities'),
    path('api/similarities/recalculate/<int:book_id>/', recalculate_similarities, name='recalculate_book_similarities'),
    
    # AUTH ENDPOINTS 
    path('api/auth/', include('ml_api.urls_auth')),
    
    # JWT ENDPOINTS
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # BOOK LISTS API
    path('api/lists/', include('ml_api.urls_lists')),
]