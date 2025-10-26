from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg, Max, Min
from django.utils import timezone

from .models import BookReview, Book, User
from .serializers import (
    BookReviewSerializer,
    BookReviewSimpleSerializer,
    BookListSerializer
)

# =============================================================================
# BOOK REVIEWS VIEWS
# =============================================================================

@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def book_reviews_list(request, book_id):
    """
    GET: Get all reviews for a book
    POST: Create a new review for a book (requires authentication)
    """
    book = get_object_or_404(Book, id=book_id)
    
    if request.method == 'GET':
        # Get all reviews for this book
        reviews = BookReview.objects.filter(book=book).select_related('user').order_by('-created_at')
        
        # Optional filtering
        rating_filter = request.GET.get('rating')
        if rating_filter:
            try:
                rating_filter = int(rating_filter)
                reviews = reviews.filter(rating=rating_filter)
            except ValueError:
                pass
        
        # Pagination
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        start = (page - 1) * page_size
        end = start + page_size
        
        total_reviews = reviews.count()
        paginated_reviews = reviews[start:end]
        
        serializer = BookReviewSerializer(paginated_reviews, many=True)
        
        # Calculate statistics
        stats = reviews.aggregate(
            average_rating=Avg('rating'),
            total_reviews=Count('id'),
            max_rating=Max('rating'),
            min_rating=Min('rating')
        )
        
        # Rating distribution
        rating_distribution = {}
        for i in range(1, 11):
            count = reviews.filter(rating=i).count()
            rating_distribution[str(i)] = count
        
        return Response({
            'status': 'success',
            'book': {
                'id': book.id,
                'title': book.title,
                'authors': book.author_names
            },
            'reviews': serializer.data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': total_reviews,
                'total_pages': (total_reviews + page_size - 1) // page_size
            },
            'statistics': {
                'average_rating': round(stats['average_rating'] or 0, 2),
                'total_reviews': stats['total_reviews'],
                'max_rating': stats['max_rating'] or 0,
                'min_rating': stats['min_rating'] or 0,
                'rating_distribution': rating_distribution
            }
        })
    
    elif request.method == 'POST':
        # Create new review
        if not request.user.is_authenticated:
            return Response({
                'status': 'error',
                'message': 'Authentication required to post a review'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Check if user already reviewed this book
        if BookReview.objects.filter(user=request.user, book=book).exists():
            return Response({
                'status': 'error',
                'message': 'You have already reviewed this book. You can edit your existing review.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create review
        data = request.data.copy()
        data['user_id'] = request.user.id
        data['book_id'] = book.id
        
        serializer = BookReviewSerializer(data=data)
        
        if serializer.is_valid():
            review = serializer.save()
            
            return Response({
                'status': 'success',
                'message': 'Review posted successfully!',
                'review': BookReviewSerializer(review).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'status': 'error',
            'message': 'Validation error',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def review_detail(request, review_id):
    """
    GET: Get review details
    PUT: Update review (only by owner)
    DELETE: Delete review (only by owner)
    """
    review = get_object_or_404(BookReview, id=review_id)
    
    if request.method == 'GET':
        serializer = BookReviewSerializer(review)
        return Response({
            'status': 'success',
            'review': serializer.data
        })
    
    elif request.method == 'PUT':
        # Check ownership
        if review.user != request.user:
            return Response({
                'status': 'error',
                'message': 'You can only edit your own reviews'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = BookReviewSerializer(review, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'message': 'Review updated successfully',
                'review': serializer.data
            })
        
        return Response({
            'status': 'error',
            'message': 'Validation error',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        # Check ownership
        if review.user != request.user:
            return Response({
                'status': 'error',
                'message': 'You can only delete your own reviews'
            }, status=status.HTTP_403_FORBIDDEN)
        
        review.delete()
        
        return Response({
            'status': 'success',
            'message': 'Review deleted successfully'
        })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_reviews_list(request):
    """
    Get all reviews by the current user
    """
    user = request.user
    
    # Get all user's reviews
    reviews = BookReview.objects.filter(user=user).select_related('book').order_by('-created_at')
    
    # Optional filtering
    rating_filter = request.GET.get('rating')
    if rating_filter:
        try:
            rating_filter = int(rating_filter)
            reviews = reviews.filter(rating=rating_filter)
        except ValueError:
            pass
    
    # Sorting
    sort_by = request.GET.get('sort_by', '-created_at')
    valid_sorts = ['-created_at', 'created_at', '-rating', 'rating', 'book__title']
    if sort_by in valid_sorts:
        reviews = reviews.order_by(sort_by)
    
    # Pagination
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    start = (page - 1) * page_size
    end = start + page_size
    
    total_reviews = reviews.count()
    paginated_reviews = reviews[start:end]
    
    serializer = BookReviewSerializer(paginated_reviews, many=True)
    
    # User statistics
    stats = reviews.aggregate(
        average_rating=Avg('rating'),
        total_reviews=Count('id'),
        highest_rating=Max('rating'),
        lowest_rating=Min('rating')
    )
    
    return Response({
        'status': 'success',
        'reviews': serializer.data,
        'pagination': {
            'page': page,
            'page_size': page_size,
            'total': total_reviews,
            'total_pages': (total_reviews + page_size - 1) // page_size
        },
        'user_statistics': {
            'total_reviews': stats['total_reviews'],
            'average_rating': round(stats['average_rating'] or 0, 2),
            'highest_rating': stats['highest_rating'] or 0,
            'lowest_rating': stats['lowest_rating'] or 0
        }
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def check_user_review(request, book_id):
    """
    Check if current user has reviewed a specific book
    """
    book = get_object_or_404(Book, id=book_id)
    
    try:
        review = BookReview.objects.get(user=request.user, book=book)
        serializer = BookReviewSerializer(review)
        
        return Response({
            'status': 'success',
            'has_reviewed': True,
            'review': serializer.data
        })
    except BookReview.DoesNotExist:
        return Response({
            'status': 'success',
            'has_reviewed': False,
            'review': None
        })

@api_view(['GET'])
def review_statistics(request):
    """
    Get global review statistics
    """
    try:
        # Overall statistics
        total_reviews = BookReview.objects.count()
        total_users_reviewed = BookReview.objects.values('user').distinct().count()
        total_books_reviewed = BookReview.objects.values('book').distinct().count()
        
        overall_stats = BookReview.objects.aggregate(
            average_rating=Avg('rating'),
            highest_rating=Max('rating'),
            lowest_rating=Min('rating')
        )
        
        # Rating distribution (1-10)
        rating_distribution = {}
        for i in range(1, 11):
            count = BookReview.objects.filter(rating=i).count()
            rating_distribution[str(i)] = count
        
        # Most reviewed books
        most_reviewed_books = Book.objects.annotate(
            review_count=Count('reviews')
        ).filter(review_count__gt=0).order_by('-review_count')[:10]
        
        most_reviewed_data = []
        for book in most_reviewed_books:
            most_reviewed_data.append({
                'id': book.id,
                'title': book.title,
                'authors': book.author_names,
                'review_count': book.review_count,
                'average_rating': book.average_rating
            })
        
        # Most active reviewers
        most_active_users = User.objects.annotate(
            review_count=Count('reviews')
        ).filter(review_count__gt=0).order_by('-review_count')[:10]
        
        most_active_data = []
        for user in most_active_users:
            user_reviews = user.reviews.aggregate(avg_rating=Avg('rating'))
            most_active_data.append({
                'id': user.id,
                'username': user.username,
                'review_count': user.review_count,
                'average_rating': round(user_reviews['avg_rating'] or 0, 2)
            })
        
        # Recent reviews
        recent_reviews = BookReview.objects.select_related('user', 'book').order_by('-created_at')[:5]
        recent_reviews_data = BookReviewSimpleSerializer(recent_reviews, many=True).data
        
        return Response({
            'status': 'success',
            'statistics': {
                'total_reviews': total_reviews,
                'total_users_reviewed': total_users_reviewed,
                'total_books_reviewed': total_books_reviewed,
                'overall_average_rating': round(overall_stats['average_rating'] or 0, 2),
                'highest_rating': overall_stats['highest_rating'] or 0,
                'lowest_rating': overall_stats['lowest_rating'] or 0,
                'rating_distribution': rating_distribution,
                'most_reviewed_books': most_reviewed_data,
                'most_active_reviewers': most_active_data,
                'recent_reviews': recent_reviews_data
            }
        })
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def highest_rated_books(request):
    """
    Get highest rated books (with minimum review count)
    """
    try:
        min_reviews = int(request.GET.get('min_reviews', 5))
        limit = int(request.GET.get('limit', 20))
        
        # Get books with at least min_reviews reviews, ordered by average rating
        books = Book.objects.annotate(
            review_count=Count('reviews'),
            avg_rating=Avg('reviews__rating')
        ).filter(
            review_count__gte=min_reviews
        ).order_by('-avg_rating', '-review_count')[:limit]
        
        books_data = []
        for book in books:
            books_data.append({
                'id': book.id,
                'title': book.title,
                'authors': book.author_names,
                'average_rating': round(book.avg_rating, 2),
                'review_count': book.review_count,
                'cover_image_url': book.cover_image_url
            })
        
        return Response({
            'status': 'success',
            'books': books_data,
            'parameters': {
                'min_reviews': min_reviews,
                'limit': limit
            }
        })
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)