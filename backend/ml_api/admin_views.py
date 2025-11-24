from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Count, Avg, Q, Sum
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404

from .models import (
    Book, Author, Publisher, Category, User, BookReview,
    BookSimilarity, UserSimilarity, BookList, ReadingProgress,
    Badge, UserBadge, UserStatistics
)
from .serializers import (
    BookSerializer, AuthorSerializer, PublisherSerializer,
    CategorySerializer, UserProfileSerializer, BookReviewSerializer
)
from .services.similarity_service import get_similarity_service
from .services.user_similarity_service import get_user_similarity_service
from .services.badge_service import BadgeService


# =============================================================================
# PERMISSIONS
# =============================================================================

class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff


# =============================================================================
# DASHBOARD & STATISTICS
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_dashboard(request):
    """
    Main admin dashboard with key statistics
    """
    try:
        # Time ranges
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        last_30d = now - timedelta(days=30)
        
        # Basic counts
        total_books = Book.objects.count()
        total_users = User.objects.count()
        total_reviews = BookReview.objects.count()
        total_authors = Author.objects.count()
        total_categories = Category.objects.count()
        
        # Recent activity
        new_users_24h = User.objects.filter(created_at__gte=last_24h).count()
        new_reviews_24h = BookReview.objects.filter(created_at__gte=last_24h).count()
        new_books_24h = Book.objects.filter(created_at__gte=last_24h).count()
        
        # Review statistics
        review_stats = BookReview.objects.aggregate(
            avg_rating=Avg('rating'),
            total_reviews=Count('id')
        )
        
        # User engagement
        active_users_7d = User.objects.filter(
            Q(reviews__created_at__gte=last_7d) |
            Q(reading_progress__updated_at__gte=last_7d)
        ).distinct().count()
        
        # Top rated books
        top_books = Book.objects.annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ).filter(review_count__gte=5).order_by('-avg_rating')[:5]
        
        top_books_data = [{
            'id': book.id,
            'title': book.title,
            'authors': book.author_names,
            'avg_rating': round(book.avg_rating, 2),
            'review_count': book.review_count
        } for book in top_books]
        
        # Most active users
        top_users = User.objects.annotate(
            review_count=Count('reviews')
        ).order_by('-review_count')[:5]
        
        top_users_data = [{
            'id': user.id,
            'username': user.username,
            'review_count': user.review_count
        } for user in top_users]
        
        # Similarity stats
        similarity_stats = {
            'book_similarities': BookSimilarity.objects.count(),
            'user_similarities': UserSimilarity.objects.count(),
            'avg_book_similarity': BookSimilarity.objects.aggregate(
                avg=Avg('cosine_similarity')
            )['avg'] or 0
        }
        
        # Gamification stats
        gamification_stats = {
            'total_badges': Badge.objects.count(),
            'active_badges': Badge.objects.filter(is_active=True).count(),
            'hidden_badges': Badge.objects.filter(is_hidden=True).count(),
            'badges_earned': UserBadge.objects.filter(completed=True).count(),
            'avg_user_points': UserStatistics.objects.aggregate(
                avg=Avg('total_points')
            )['avg'] or 0,
            'total_points_awarded': UserStatistics.objects.aggregate(
                total=Sum('total_points')
            )['total'] or 0,
        }
        
        return Response({
            'status': 'success',
            'dashboard': {
                'overview': {
                    'total_books': total_books,
                    'total_users': total_users,
                    'total_reviews': total_reviews,
                    'total_authors': total_authors,
                    'total_categories': total_categories,
                },
                'recent_activity': {
                    'new_users_24h': new_users_24h,
                    'new_reviews_24h': new_reviews_24h,
                    'new_books_24h': new_books_24h,
                    'active_users_7d': active_users_7d,
                },
                'review_statistics': {
                    'average_rating': round(review_stats['avg_rating'] or 0, 2),
                    'total_reviews': review_stats['total_reviews'],
                },
                'top_content': {
                    'top_books': top_books_data,
                    'top_users': top_users_data,
                },
                'similarity_stats': similarity_stats,
                'gamification_stats': gamification_stats,
            }
        })
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_analytics(request):
    """
    Detailed analytics with charts data
    """
    try:
        period = request.GET.get('period', '30')  # days
        days = int(period)
        start_date = timezone.now() - timedelta(days=days)
        
        # Daily new users
        daily_users = []
        for i in range(days):
            day = start_date + timedelta(days=i)
            next_day = day + timedelta(days=1)
            count = User.objects.filter(
                created_at__gte=day,
                created_at__lt=next_day
            ).count()
            daily_users.append({
                'date': day.strftime('%Y-%m-%d'),
                'count': count
            })
        
        # Daily reviews
        daily_reviews = []
        for i in range(days):
            day = start_date + timedelta(days=i)
            next_day = day + timedelta(days=1)
            count = BookReview.objects.filter(
                created_at__gte=day,
                created_at__lt=next_day
            ).count()
            daily_reviews.append({
                'date': day.strftime('%Y-%m-%d'),
                'count': count
            })
        
        # Rating distribution
        rating_distribution = []
        for rating in range(1, 11):
            count = BookReview.objects.filter(rating=rating).count()
            rating_distribution.append({
                'rating': rating,
                'count': count
            })
        
        # Category popularity
        category_stats = Category.objects.annotate(
            book_count=Count('books')
        ).order_by('-book_count')[:10]
        
        category_data = [{
            'name': cat.name,
            'book_count': cat.book_count
        } for cat in category_stats]
        
        # Author productivity
        author_stats = Author.objects.annotate(
            book_count=Count('books')
        ).filter(book_count__gte=3).order_by('-book_count')[:10]
        
        author_data = [{
            'name': author.full_name,
            'book_count': author.book_count
        } for author in author_stats]
        
        return Response({
            'status': 'success',
            'analytics': {
                'period_days': days,
                'daily_users': daily_users,
                'daily_reviews': daily_reviews,
                'rating_distribution': rating_distribution,
                'top_categories': category_data,
                'top_authors': author_data,
            }
        })
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =============================================================================
# BOOKS MANAGEMENT
# =============================================================================

@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def admin_books_list(request):
    """
    GET: List all books with advanced filters
    POST: Create new book
    """
    if request.method == 'GET':
        # Get all books
        books = Book.objects.all().select_related('publisher').prefetch_related('authors', 'categories')
        
        # Filters
        search = request.GET.get('search', '').strip()
        if search:
            books = books.filter(
                Q(title__icontains=search) |
                Q(isbn__icontains=search) |
                Q(description__icontains=search)
            )
        
        category_id = request.GET.get('category')
        if category_id:
            books = books.filter(categories__id=category_id)
        
        author_id = request.GET.get('author')
        if author_id:
            books = books.filter(authors__id=author_id)
        
        publisher_id = request.GET.get('publisher')
        if publisher_id:
            books = books.filter(publisher_id=publisher_id)
        
        year_from = request.GET.get('year_from')
        if year_from:
            books = books.filter(publish_year__gte=int(year_from))
        
        year_to = request.GET.get('year_to')
        if year_to:
            books = books.filter(publish_year__lte=int(year_to))
        
        has_cover = request.GET.get('has_cover')
        if has_cover == 'true':
            books = books.filter(cover_image_url__isnull=False)
        elif has_cover == 'false':
            books = books.filter(cover_image_url__isnull=True)
        
        # Sorting
        sort_by = request.GET.get('sort_by', '-created_at')
        valid_sorts = [
            'title', '-title', 'publish_year', '-publish_year',
            'created_at', '-created_at', 'updated_at', '-updated_at'
        ]
        if sort_by in valid_sorts:
            books = books.order_by(sort_by)
        
        # Pagination
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 50))
        
        paginator = Paginator(books, page_size)
        page_obj = paginator.get_page(page)
        
        serializer = BookSerializer(page_obj, many=True)
        
        return Response({
            'status': 'success',
            'books': serializer.data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': paginator.count,
                'total_pages': paginator.num_pages,
            }
        })
    
    elif request.method == 'POST':
        from .serializers import BookCreateUpdateSerializer
        serializer = BookCreateUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            book = serializer.save()
            return Response({
                'status': 'success',
                'message': 'Book created successfully',
                'book': BookSerializer(book).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'status': 'error',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdminUser])
def admin_book_detail(request, book_id):
    """
    GET: Get book details
    PUT: Update book
    DELETE: Delete book
    """
    book = get_object_or_404(Book, id=book_id)
    
    if request.method == 'GET':
        serializer = BookSerializer(book)
        
        # Additional stats
        stats = {
            'total_reviews': book.reviews.count(),
            'average_rating': book.average_rating,
            'in_lists': BookList.objects.filter(items__book=book).count(),
            'reading_now': ReadingProgress.objects.filter(
                book=book, status='reading'
            ).count(),
        }
        
        return Response({
            'status': 'success',
            'book': serializer.data,
            'stats': stats
        })
    
    elif request.method == 'PUT':
        from .serializers import BookCreateUpdateSerializer
        serializer = BookCreateUpdateSerializer(book, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'message': 'Book updated successfully',
                'book': BookSerializer(book).data
            })
        
        return Response({
            'status': 'error',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        title = book.title
        book.delete()
        
        return Response({
            'status': 'success',
            'message': f'Book "{title}" deleted successfully'
        })


# =============================================================================
# USERS MANAGEMENT
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_users_list(request):
    """
    List all users with filters
    """
    users = User.objects.all()
    
    # Filters
    search = request.GET.get('search', '').strip()
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    is_staff = request.GET.get('is_staff')
    if is_staff == 'true':
        users = users.filter(is_staff=True)
    elif is_staff == 'false':
        users = users.filter(is_staff=False)
    
    is_active = request.GET.get('is_active')
    if is_active == 'true':
        users = users.filter(is_active=True)
    elif is_active == 'false':
        users = users.filter(is_active=False)
    
    # Sorting
    sort_by = request.GET.get('sort_by', '-created_at')
    users = users.order_by(sort_by)
    
    # Pagination
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 50))
    
    paginator = Paginator(users, page_size)
    page_obj = paginator.get_page(page)
    
    # Add stats to each user
    users_data = []
    for user in page_obj:
        user_data = UserProfileSerializer(user).data
        user_data['stats'] = {
            'total_reviews': user.reviews.count(),
            'total_lists': user.book_lists.count(),
            'books_read': ReadingProgress.objects.filter(
                user=user, status='finished'
            ).count(),
        }
        users_data.append(user_data)
    
    return Response({
        'status': 'success',
        'users': users_data,
        'pagination': {
            'page': page,
            'page_size': page_size,
            'total': paginator.count,
            'total_pages': paginator.num_pages,
        }
    })


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdminUser])
def admin_user_detail(request, user_id):
    """
    GET: Get user details
    PUT: Update user (change staff status, active status, etc.)
    DELETE: Delete user
    """
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'GET':
        user_data = UserProfileSerializer(user).data
        
        # Additional stats
        stats = {
            'total_reviews': user.reviews.count(),
            'avg_rating_given': user.reviews.aggregate(
                avg=Avg('rating')
            )['avg'] or 0,
            'total_lists': user.book_lists.count(),
            'books_read': ReadingProgress.objects.filter(
                user=user, status='finished'
            ).count(),
            'badges_earned': UserBadge.objects.filter(
                user=user, completed=True
            ).count(),
        }
        
        # Recent activity
        recent_reviews = BookReviewSerializer(
            user.reviews.order_by('-created_at')[:5],
            many=True
        ).data
        
        return Response({
            'status': 'success',
            'user': user_data,
            'stats': stats,
            'recent_reviews': recent_reviews
        })
    
    elif request.method == 'PUT':
        # Allow updating specific fields
        allowed_fields = ['is_staff', 'is_active', 'first_name', 'last_name']
        
        for field in allowed_fields:
            if field in request.data:
                setattr(user, field, request.data[field])
        
        user.save()
        
        return Response({
            'status': 'success',
            'message': 'User updated successfully',
            'user': UserProfileSerializer(user).data
        })
    
    elif request.method == 'DELETE':
        # Prevent deleting yourself
        if user.id == request.user.id:
            return Response({
                'status': 'error',
                'message': 'Cannot delete your own account'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        username = user.username
        user.delete()
        
        return Response({
            'status': 'success',
            'message': f'User "{username}" deleted successfully'
        })


# =============================================================================
# AUTHORS MANAGEMENT
# =============================================================================

@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def admin_authors_list(request):
    """
    GET: List all authors
    POST: Create new author
    """
    if request.method == 'GET':
        authors = Author.objects.all().annotate(
            book_count=Count('books')
        )
        
        # Search
        search = request.GET.get('search', '').strip()
        if search:
            authors = authors.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        # Sorting
        sort_by = request.GET.get('sort_by', 'last_name')
        authors = authors.order_by(sort_by)
        
        # Pagination
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 50))
        
        paginator = Paginator(authors, page_size)
        page_obj = paginator.get_page(page)
        
        serializer = AuthorSerializer(page_obj, many=True)
        
        return Response({
            'status': 'success',
            'authors': serializer.data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': paginator.count,
                'total_pages': paginator.num_pages,
            }
        })
    
    elif request.method == 'POST':
        serializer = AuthorSerializer(data=request.data)
        
        if serializer.is_valid():
            author = serializer.save()
            return Response({
                'status': 'success',
                'message': 'Author created successfully',
                'author': AuthorSerializer(author).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'status': 'error',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdminUser])
def admin_author_detail(request, author_id):
    """
    GET: Get author details
    PUT: Update author
    DELETE: Delete author (if no books)
    """
    author = get_object_or_404(Author, id=author_id)
    
    if request.method == 'GET':
        serializer = AuthorSerializer(author)
        
        # Books by this author
        books = Book.objects.filter(authors=author)[:10]
        books_data = [{
            'id': book.id,
            'title': book.title,
            'publish_year': book.publish_year
        } for book in books]
        
        return Response({
            'status': 'success',
            'author': serializer.data,
            'books': books_data,
            'total_books': author.books.count()
        })
    
    elif request.method == 'PUT':
        serializer = AuthorSerializer(author, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'message': 'Author updated successfully',
                'author': serializer.data
            })
        
        return Response({
            'status': 'error',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if author.books.count() > 0:
            return Response({
                'status': 'error',
                'message': f'Cannot delete author with {author.books.count()} books'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        name = author.full_name
        author.delete()
        
        return Response({
            'status': 'success',
            'message': f'Author "{name}" deleted successfully'
        })


# =============================================================================
# CATEGORIES MANAGEMENT
# =============================================================================

@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def admin_categories_list(request):
    """
    GET: List all categories
    POST: Create new category
    """
    if request.method == 'GET':
        categories = Category.objects.all().annotate(
            book_count=Count('books')
        ).order_by('name')
        
        serializer = CategorySerializer(categories, many=True)
        
        return Response({
            'status': 'success',
            'categories': serializer.data,
            'count': categories.count()
        })
    
    elif request.method == 'POST':
        serializer = CategorySerializer(data=request.data)
        
        if serializer.is_valid():
            category = serializer.save()
            return Response({
                'status': 'success',
                'message': 'Category created successfully',
                'category': CategorySerializer(category).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'status': 'error',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdminUser])
def admin_category_detail(request, category_id):
    """
    GET: Get category details
    PUT: Update category
    DELETE: Delete category (if no books)
    """
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'GET':
        serializer = CategorySerializer(category)
        
        return Response({
            'status': 'success',
            'category': serializer.data
        })
    
    elif request.method == 'PUT':
        serializer = CategorySerializer(category, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'message': 'Category updated successfully',
                'category': serializer.data
            })
        
        return Response({
            'status': 'error',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if category.books.count() > 0:
            return Response({
                'status': 'error',
                'message': f'Cannot delete category with {category.books.count()} books'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        name = category.name
        category.delete()
        
        return Response({
            'status': 'success',
            'message': f'Category "{name}" deleted successfully'
        })


# =============================================================================
# REVIEWS MANAGEMENT
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_reviews_list(request):
    """
    List all reviews with filters
    """
    reviews = BookReview.objects.all().select_related('user', 'book')
    
    # Filters
    user_id = request.GET.get('user_id')
    if user_id:
        reviews = reviews.filter(user_id=user_id)
    
    book_id = request.GET.get('book_id')
    if book_id:
        reviews = reviews.filter(book_id=book_id)
    
    rating = request.GET.get('rating')
    if rating:
        reviews = reviews.filter(rating=int(rating))
    
    # Date range
    date_from = request.GET.get('date_from')
    if date_from:
        reviews = reviews.filter(created_at__gte=date_from)
    
    date_to = request.GET.get('date_to')
    if date_to:
        reviews = reviews.filter(created_at__lte=date_to)
    
    # Sorting
    sort_by = request.GET.get('sort_by', '-created_at')
    reviews = reviews.order_by(sort_by)
    
    # Pagination
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 50))
    
    paginator = Paginator(reviews, page_size)
    page_obj = paginator.get_page(page)
    
    serializer = BookReviewSerializer(page_obj, many=True)
    
    return Response({
        'status': 'success',
        'reviews': serializer.data,
        'pagination': {
            'page': page,
            'page_size': page_size,
            'total': paginator.count,
            'total_pages': paginator.num_pages,
        }
    })


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def admin_review_delete(request, review_id):
    """
    Delete a review
    """
    review = get_object_or_404(BookReview, id=review_id)
    
    user = review.user.username
    book = review.book.title
    
    review.delete()
    
    return Response({
        'status': 'success',
        'message': f'Review by {user} for "{book}" deleted successfully'
    })


# =============================================================================
# BULK ACTIONS
# =============================================================================

@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_bulk_delete_books(request):
    """
    Bulk delete books
    """
    book_ids = request.data.get('book_ids', [])
    
    if not book_ids:
        return Response({
            'status': 'error',
            'message': 'No book IDs provided'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    deleted_count = Book.objects.filter(id__in=book_ids).delete()[0]
    
    return Response({
        'status': 'success',
        'message': f'Deleted {deleted_count} books'
    })


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_bulk_update_books(request):
    """
    Bulk update books (e.g., change category, publisher)
    """
    book_ids = request.data.get('book_ids', [])
    updates = request.data.get('updates', {})
    
    if not book_ids or not updates:
        return Response({
            'status': 'error',
            'message': 'book_ids and updates required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    books = Book.objects.filter(id__in=book_ids)
    
    # Apply updates
    updated_count = 0
    for book in books:
        for field, value in updates.items():
            if hasattr(book, field):
                setattr(book, field, value)
                updated_count += 1
        book.save()
    
    return Response({
        'status': 'success',
        'message': f'Updated {len(book_ids)} books'
    })


# =============================================================================
# SYSTEM ACTIONS
# =============================================================================

@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_recalculate_similarities(request):
    """
    Trigger similarity recalculation
    """
    mode = request.data.get('mode', 'sample')  # 'sample' or 'all'
    limit = int(request.data.get('limit', 50))
    
    try:
        service = get_similarity_service()
        
        if mode == 'all':
            count = service.calculate_all_similarities()
        else:
            # Sample mode - calculate for limited books
            from .models import Book
            books = Book.objects.order_by('-created_at')[:limit]
            count = 0
            for book in books:
                c = service.calculate_similarities_for_book(book)
                count += c
        
        return Response({
            'status': 'success',
            'message': f'Similarity recalculation completed',
            'similarities_created': count
        })
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_recalculate_user_similarities(request):
    """
    Trigger user similarity recalculation
    """
    try:
        service = get_user_similarity_service()
        count = service.calculate_all_similarities()
        
        return Response({
            'status': 'success',
            'message': 'User similarity recalculation completed',
            'similarities_created': count
        })
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_check_all_badges(request):
    """
    Check and award badges for all users
    """
    try:
        users = User.objects.all()
        total_badges_awarded = 0
        
        for user in users:
            newly_earned = BadgeService.check_and_award_badges(user)
            total_badges_awarded += len(newly_earned)
        
        return Response({
            'status': 'success',
            'message': f'Badge check completed for {users.count()} users',
            'badges_awarded': total_badges_awarded
        })
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_cleanup_data(request):
    """
    Cleanup orphaned data
    """
    cleanup_type = request.data.get('type', 'all')
    
    results = {}
    
    try:
        if cleanup_type in ['all', 'similarities']:
            # Remove low similarity records
            deleted = BookSimilarity.objects.filter(
                cosine_similarity__lt=0.05
            ).delete()[0]
            results['low_similarities_deleted'] = deleted
        
        if cleanup_type in ['all', 'tokens']:
            # Remove expired tokens
            from .models import RefreshToken
            deleted = RefreshToken.objects.filter(
                expires_at__lt=timezone.now()
            ).delete()[0]
            results['expired_tokens_deleted'] = deleted
        
        return Response({
            'status': 'success',
            'message': 'Cleanup completed',
            'results': results
        })
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# =============================================================================
# BADGES MANAGEMENT
# =============================================================================

@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def admin_badges_list(request):
    """
    GET: List all badges
    POST: Create new badge
    """
    if request.method == 'GET':
        badges = Badge.objects.all()
        
        # Filters
        category = request.GET.get('category')
        if category:
            badges = badges.filter(category=category)
        
        rarity = request.GET.get('rarity')
        if rarity:
            badges = badges.filter(rarity=rarity)
        
        is_active = request.GET.get('is_active')
        if is_active == 'true':
            badges = badges.filter(is_active=True)
        elif is_active == 'false':
            badges = badges.filter(is_active=False)
        
        is_hidden = request.GET.get('is_hidden')
        if is_hidden == 'true':
            badges = badges.filter(is_hidden=True)
        elif is_hidden == 'false':
            badges = badges.filter(is_hidden=False)
        
        # Sorting
        sort_by = request.GET.get('sort_by', 'category')
        badges = badges.order_by(sort_by, 'order')
        
        # Add statistics
        badges_data = []
        for badge in badges:
            badge_dict = {
                'id': badge.id,
                'name': badge.name,
                'slug': badge.slug,
                'description': badge.description,
                'icon': badge.icon,
                'category': badge.category,
                'rarity': badge.rarity,
                'requirement_type': badge.requirement_type,
                'requirement_value': badge.requirement_value,
                'requirement_condition': badge.requirement_condition,
                'points': badge.points,
                'is_active': badge.is_active,
                'is_hidden': badge.is_hidden,
                'order': badge.order,
                'created_at': badge.created_at,
                'updated_at': badge.updated_at,
                # Stats
                'users_earned': UserBadge.objects.filter(
                    badge=badge, completed=True
                ).count(),
                'users_in_progress': UserBadge.objects.filter(
                    badge=badge, completed=False
                ).count(),
            }
            badges_data.append(badge_dict)
        
        return Response({
            'status': 'success',
            'badges': badges_data,
            'count': len(badges_data)
        })
    
    elif request.method == 'POST':
        from .serializers_gamification import BadgeSerializer
        serializer = BadgeSerializer(data=request.data)
        
        if serializer.is_valid():
            badge = serializer.save()
            return Response({
                'status': 'success',
                'message': 'Badge created successfully',
                'badge': BadgeSerializer(badge).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'status': 'error',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdminUser])
def admin_badge_detail(request, badge_id):
    """
    GET: Get badge details with statistics
    PUT: Update badge
    DELETE: Delete badge
    """
    badge = get_object_or_404(Badge, id=badge_id)
    
    if request.method == 'GET':
        from .serializers_gamification import BadgeSerializer
        badge_data = BadgeSerializer(badge).data
        
        # Detailed statistics
        users_earned = UserBadge.objects.filter(badge=badge, completed=True)
        users_in_progress = UserBadge.objects.filter(badge=badge, completed=False)
        
        stats = {
            'total_earned': users_earned.count(),
            'total_in_progress': users_in_progress.count(),
            'completion_rate': (users_earned.count() / UserBadge.objects.filter(badge=badge).count() * 100) 
                if UserBadge.objects.filter(badge=badge).count() > 0 else 0,
            'total_points_awarded': users_earned.count() * badge.points,
        }
        
        # Recent earners
        recent_earners = users_earned.select_related('user').order_by('-earned_at')[:10]
        recent_earners_data = [{
            'user_id': ub.user.id,
            'username': ub.user.username,
            'earned_at': ub.earned_at,
        } for ub in recent_earners]
        
        # Progress distribution
        if users_in_progress.exists():
            progress_ranges = {
                '0-25%': users_in_progress.filter(
                    progress__lt=badge.requirement_value * 0.25
                ).count(),
                '25-50%': users_in_progress.filter(
                    progress__gte=badge.requirement_value * 0.25,
                    progress__lt=badge.requirement_value * 0.50
                ).count(),
                '50-75%': users_in_progress.filter(
                    progress__gte=badge.requirement_value * 0.50,
                    progress__lt=badge.requirement_value * 0.75
                ).count(),
                '75-100%': users_in_progress.filter(
                    progress__gte=badge.requirement_value * 0.75
                ).count(),
            }
        else:
            progress_ranges = {}
        
        return Response({
            'status': 'success',
            'badge': badge_data,
            'stats': stats,
            'recent_earners': recent_earners_data,
            'progress_distribution': progress_ranges
        })
    
    elif request.method == 'PUT':
        from .serializers_gamification import BadgeSerializer
        serializer = BadgeSerializer(badge, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'message': 'Badge updated successfully',
                'badge': BadgeSerializer(badge).data
            })
        
        return Response({
            'status': 'error',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        # Check if any users have earned this badge
        users_with_badge = UserBadge.objects.filter(badge=badge, completed=True).count()
        
        if users_with_badge > 0:
            return Response({
                'status': 'error',
                'message': f'Cannot delete badge that {users_with_badge} users have earned. Deactivate it instead.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        name = badge.name
        badge.delete()
        
        return Response({
            'status': 'success',
            'message': f'Badge "{name}" deleted successfully'
        })


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_badge_toggle_active(request, badge_id):
    """
    Toggle badge active status
    """
    badge = get_object_or_404(Badge, id=badge_id)
    
    badge.is_active = not badge.is_active
    badge.save()
    
    return Response({
        'status': 'success',
        'message': f'Badge {"activated" if badge.is_active else "deactivated"}',
        'is_active': badge.is_active
    })


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_badge_award_manually(request, badge_id):
    """
    Manually award badge to specific users
    """
    badge = get_object_or_404(Badge, id=badge_id)
    user_ids = request.data.get('user_ids', [])
    
    if not user_ids:
        return Response({
            'status': 'error',
            'message': 'No user IDs provided'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    awarded_count = 0
    already_had_count = 0
    
    for user_id in user_ids:
        try:
            user = User.objects.get(id=user_id)
            user_badge, created = UserBadge.objects.get_or_create(
                user=user,
                badge=badge,
                defaults={
                    'progress': badge.requirement_value,
                    'completed': True,
                    'earned_at': timezone.now()
                }
            )
            
            if created:
                awarded_count += 1
                # Update user stats
                stats = UserStatistics.objects.get_or_create(user=user)[0]
                stats.total_badges_earned += 1
                stats.total_points += badge.points
                stats.save()
            else:
                if not user_badge.completed:
                    user_badge.completed = True
                    user_badge.progress = badge.requirement_value
                    user_badge.earned_at = timezone.now()
                    user_badge.save()
                    awarded_count += 1
                else:
                    already_had_count += 1
        except User.DoesNotExist:
            continue
    
    return Response({
        'status': 'success',
        'message': f'Badge awarded to {awarded_count} users',
        'awarded': awarded_count,
        'already_had': already_had_count
    })


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_badge_revoke(request, badge_id):
    """
    Revoke badge from specific users
    """
    badge = get_object_or_404(Badge, id=badge_id)
    user_ids = request.data.get('user_ids', [])
    
    if not user_ids:
        return Response({
            'status': 'error',
            'message': 'No user IDs provided'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    revoked_count = 0
    
    for user_id in user_ids:
        try:
            user_badge = UserBadge.objects.get(
                user_id=user_id,
                badge=badge,
                completed=True
            )
            
            # Update user stats
            user = user_badge.user
            stats = UserStatistics.objects.get_or_create(user=user)[0]
            stats.total_badges_earned = max(0, stats.total_badges_earned - 1)
            stats.total_points = max(0, stats.total_points - badge.points)
            stats.save()
            
            # Delete the badge
            user_badge.delete()
            revoked_count += 1
            
        except UserBadge.DoesNotExist:
            continue
    
    return Response({
        'status': 'success',
        'message': f'Badge revoked from {revoked_count} users',
        'revoked': revoked_count
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_badge_categories(request):
    """
    Get badge categories with statistics
    """
    categories_data = []
    
    for category_choice in Badge.CATEGORY_CHOICES:
        category_key = category_choice[0]
        category_name = category_choice[1]
        
        badges = Badge.objects.filter(category=category_key)
        active_badges = badges.filter(is_active=True)
        
        total_earned = UserBadge.objects.filter(
            badge__category=category_key,
            completed=True
        ).count()
        
        categories_data.append({
            'key': category_key,
            'name': category_name,
            'total_badges': badges.count(),
            'active_badges': active_badges.count(),
            'times_earned': total_earned,
        })
    
    return Response({
        'status': 'success',
        'categories': categories_data
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_badge_rarities(request):
    """
    Get badge rarities with statistics
    """
    rarities_data = []
    
    for rarity_choice in Badge.RARITY_CHOICES:
        rarity_key = rarity_choice[0]
        rarity_name = rarity_choice[1]
        
        badges = Badge.objects.filter(rarity=rarity_key)
        
        total_earned = UserBadge.objects.filter(
            badge__rarity=rarity_key,
            completed=True
        ).count()
        
        avg_points = badges.aggregate(avg=Avg('points'))['avg'] or 0
        
        rarities_data.append({
            'key': rarity_key,
            'name': rarity_name,
            'total_badges': badges.count(),
            'times_earned': total_earned,
            'avg_points': round(avg_points, 2)
        })
    
    return Response({
        'status': 'success',
        'rarities': rarities_data
    })


@api_view(['POST'])
@permission_classes([IsAdminUser])
def admin_badge_bulk_update(request):
    """
    Bulk update badges (activate/deactivate, change points, etc.)
    """
    badge_ids = request.data.get('badge_ids', [])
    updates = request.data.get('updates', {})
    
    if not badge_ids or not updates:
        return Response({
            'status': 'error',
            'message': 'badge_ids and updates required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    allowed_fields = ['is_active', 'is_hidden', 'points', 'order']
    
    badges = Badge.objects.filter(id__in=badge_ids)
    updated_count = 0
    
    for badge in badges:
        for field, value in updates.items():
            if field in allowed_fields and hasattr(badge, field):
                setattr(badge, field, value)
        badge.save()
        updated_count += 1
    
    return Response({
        'status': 'success',
        'message': f'Updated {updated_count} badges'
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_badge_leaderboard(request):
    """
    Get users with most badges earned
    """
    limit = int(request.GET.get('limit', 20))
    
    users = User.objects.annotate(
        badge_count=Count('earned_badges', filter=Q(earned_badges__completed=True))
    ).filter(badge_count__gt=0).order_by('-badge_count')[:limit]
    
    leaderboard_data = []
    for user in users:
        stats = UserStatistics.objects.get_or_create(user=user)[0]
        leaderboard_data.append({
            'user_id': user.id,
            'username': user.username,
            'badge_count': user.badge_count,
            'total_points': stats.total_points,
        })
    
    return Response({
        'status': 'success',
        'leaderboard': leaderboard_data
    })


# =============================================================================
# EXPORT DATA
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_export_data(request):
    """
    Export data to CSV
    """
    export_type = request.GET.get('type', 'books')
    
    try:
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{export_type}_export.csv"'
        
        writer = csv.writer(response)
        
        if export_type == 'books':
            writer.writerow(['ID', 'Title', 'Authors', 'ISBN', 'Year', 'Rating', 'Reviews'])
            books = Book.objects.all()[:1000]  # Limit for performance
            
            for book in books:
                writer.writerow([
                    book.id,
                    book.title,
                    book.author_names,
                    book.isbn or '',
                    book.publish_year or '',
                    book.average_rating,
                    book.ratings_count
                ])
        
        elif export_type == 'users':
            writer.writerow(['ID', 'Username', 'Email', 'Joined', 'Reviews', 'Active'])
            users = User.objects.all()[:1000]
            
            for user in users:
                writer.writerow([
                    user.id,
                    user.username,
                    user.email,
                    user.created_at.strftime('%Y-%m-%d'),
                    user.reviews.count(),
                    user.is_active
                ])
        
        return response
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)