from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.db.models import Count, Avg, Q, Sum
from django.utils import timezone
from datetime import timedelta

from .models import (
    Book, Author, Publisher, Category, User, BookReview,
    BookSimilarity, UserSimilarity, UserPreferenceProfile,
    Badge, UserBadge, UserStatistics
)
from .services.similarity_service import get_similarity_service
from .services.user_similarity_service import get_user_similarity_service
from .services.badge_service import BadgeService


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_dashboard_stats(request):
    """
    Complete dashboard statistics for admin panel
    """
    try:
        # Basic counts
        total_books = Book.objects.count()
        total_users = User.objects.count()
        total_reviews = BookReview.objects.count()
        total_authors = Author.objects.count()
        total_publishers = Publisher.objects.count()
        total_categories = Category.objects.count()
        
        # Similarity stats
        book_similarities = BookSimilarity.objects.count()
        user_similarities = UserSimilarity.objects.count()
        
        # User engagement
        users_with_reviews = User.objects.annotate(
            review_count=Count('reviews')
        ).filter(review_count__gt=0).count()
        
        users_with_preferences = UserPreferenceProfile.objects.filter(
            completed=True
        ).count()
        
        # Review stats
        avg_rating = BookReview.objects.aggregate(avg=Avg('rating'))['avg'] or 0
        reviews_with_text = BookReview.objects.exclude(
            Q(review_text__isnull=True) | Q(review_text='')
        ).count()
        
        # Recent activity (last 7 days)
        week_ago = timezone.now() - timedelta(days=7)
        new_users_week = User.objects.filter(created_at__gte=week_ago).count()
        new_reviews_week = BookReview.objects.filter(created_at__gte=week_ago).count()
        
        # Gamification stats
        total_badges = Badge.objects.count()
        badges_earned = UserBadge.objects.filter(completed=True).count()
        total_points = UserStatistics.objects.aggregate(
            total=Sum('total_points')
        )['total'] or 0
        
        # Top books by reviews
        top_books = Book.objects.annotate(
            review_count=Count('reviews')
        ).order_by('-review_count')[:5].values(
            'id', 'title', 'review_count'
        )
        
        # Top users by activity
        top_users = User.objects.annotate(
            review_count=Count('reviews')
        ).order_by('-review_count')[:5].values(
            'id', 'username', 'email', 'review_count'
        )
        
        return Response({
            'status': 'success',
            'stats': {
                'content': {
                    'total_books': total_books,
                    'total_authors': total_authors,
                    'total_publishers': total_publishers,
                    'total_categories': total_categories,
                },
                'users': {
                    'total_users': total_users,
                    'users_with_reviews': users_with_reviews,
                    'users_with_preferences': users_with_preferences,
                    'new_users_week': new_users_week,
                },
                'reviews': {
                    'total_reviews': total_reviews,
                    'reviews_with_text': reviews_with_text,
                    'average_rating': round(avg_rating, 2),
                    'new_reviews_week': new_reviews_week,
                },
                'recommendations': {
                    'book_similarities': book_similarities,
                    'user_similarities': user_similarities,
                    'coverage_books': round((book_similarities / (total_books * (total_books - 1) / 2) * 100), 2) if total_books > 1 else 0,
                },
                'gamification': {
                    'total_badges': total_badges,
                    'badges_earned': badges_earned,
                    'total_points': total_points,
                },
                'top_books': list(top_books),
                'top_users': list(top_users),
            }
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def recalculate_book_similarities(request):
    """
    Trigger book similarity recalculation
    """
    try:
        book_id = request.data.get('book_id')
        batch_size = int(request.data.get('batch_size', 50))
        recalculate_all = request.data.get('recalculate_all', False) 
        
        service = get_similarity_service()
        
        if book_id:
            # Single book
            try:
                book = Book.objects.get(id=book_id)
                count = service.calculate_similarities_for_book(book, batch_size=batch_size)
                
                return Response({
                    'status': 'success',
                    'message': f'Recalculated similarities for {book.title}',
                    'similarities_created': count
                })
            except Book.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': 'Book not found'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            if recalculate_all:
                # All books
                print("Recalculating ALL book similarities...")
                total_count = service.calculate_all_similarities(batch_size=batch_size)
                
                return Response({
                    'status': 'success',
                    'message': f'Recalculated similarities for ALL books',
                    'total_similarities_created': total_count
                })
            else:
                # Just firsy 10 (safe mode)
                limit = int(request.data.get('limit', 10))
                books = Book.objects.all()[:limit]
                
                total_count = 0
                for book in books:
                    count = service.calculate_similarities_for_book(book, batch_size=batch_size)
                    total_count += count
                
                return Response({
                    'status': 'success',
                    'message': f'Recalculated similarities for {len(books)} books (limited mode)',
                    'total_similarities_created': total_count,
                    'note': 'Use recalculate_all=true to process all books'
                })
            
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def recalculate_user_similarities(request):
    """
    Trigger user similarity recalculation
    """
    try:
        user_id = request.data.get('user_id')
        batch_size = int(request.data.get('batch_size', 50))
        recalculate_all = request.data.get('recalculate_all', False)  
        
        service = get_user_similarity_service()
        
        if user_id:
            # Single user
            try:
                user = User.objects.get(id=user_id)
                count = service.calculate_similarities_for_user(user)
                
                return Response({
                    'status': 'success',
                    'message': f'Recalculated similarities for {user.username}',
                    'similarities_created': count
                })
            except User.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': 'User not found'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            if recalculate_all:
                print("Recalculating ALL user similarities...")
                total_count = service.calculate_all_similarities(batch_size=batch_size)
                
                return Response({
                    'status': 'success',
                    'message': f'Recalculated similarities for ALL users',
                    'total_similarities_created': total_count
                })
            else:
                # Just first 10 (safe mode)
                limit = int(request.data.get('limit', 10))
                users = User.objects.filter(
                    Q(reviews__isnull=False) | Q(preference_profile__isnull=False)
                ).distinct()[:limit]
                
                total_count = 0
                for user in users:
                    count = service.calculate_similarities_for_user(user)
                    total_count += count
                
                return Response({
                    'status': 'success',
                    'message': f'Recalculated similarities for {len(users)} users (limited mode)',
                    'total_similarities_created': total_count,
                    'note': 'Use recalculate_all=true to process all users'
                })
            
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['GET'])
@permission_classes([IsAdminUser])
def user_management_list(request):
    """
    List users with filtering and search
    """
    try:
        users = User.objects.all()
        
        # Search
        search = request.GET.get('search')
        if search:
            users = users.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        # Filter by activity
        has_reviews = request.GET.get('has_reviews')
        if has_reviews == 'true':
            users = users.annotate(review_count=Count('reviews')).filter(review_count__gt=0)
        
        # Annotate with stats
        users = users.annotate(
            review_count=Count('reviews'),
            avg_rating=Avg('reviews__rating')
        ).order_by('-date_joined')
        
        # Pagination
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        start = (page - 1) * page_size
        end = start + page_size
        
        total = users.count()
        paginated_users = users[start:end]
        
        user_data = []
        for user in paginated_users:
            user_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'is_active': user.is_active,
                'is_staff': user.is_staff,
                'date_joined': user.date_joined,
                'review_count': user.review_count,
                'avg_rating': round(user.avg_rating, 2) if user.avg_rating else None,
            })
        
        return Response({
            'status': 'success',
            'users': user_data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': total,
                'total_pages': (total + page_size - 1) // page_size
            }
        })
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def toggle_user_status(request, user_id):
    """
    Activate/deactivate user
    """
    try:
        user = User.objects.get(id=user_id)
        
        # Prevent self-deactivation
        if user.id == request.user.id:
            return Response({
                'status': 'error',
                'message': 'Cannot deactivate your own account'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user.is_active = not user.is_active
        user.save()
        
        return Response({
            'status': 'success',
            'message': f"User {'activated' if user.is_active else 'deactivated'}",
            'is_active': user.is_active
        })
        
    except User.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def update_user(request, user_id):
    """
    Update user details
    """
    try:
        user = User.objects.get(id=user_id)
        
        # Prevent editing yourself
        if user.id == request.user.id:
            return Response({
                'status': 'error',
                'message': 'Cannot edit your own account through admin panel'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update allowed fields
        if 'first_name' in request.data:
            user.first_name = request.data['first_name']
        if 'last_name' in request.data:
            user.last_name = request.data['last_name']
        if 'is_staff' in request.data:
            user.is_staff = request.data['is_staff']
        if 'is_active' in request.data:
            user.is_active = request.data['is_active']
        
        user.save()
        
        return Response({
            'status': 'success',
            'message': 'User updated successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_staff': user.is_staff,
                'is_active': user.is_active
            }
        })
        
    except User.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def system_health(request):
    """
    System health check
    """
    try:
        # Check database connectivity
        db_ok = True
        try:
            Book.objects.count()
        except:
            db_ok = False
        
        # Check similarity coverage
        total_books = Book.objects.count()
        total_similarities = BookSimilarity.objects.count()
        max_possible = (total_books * (total_books - 1)) / 2 if total_books > 1 else 0
        similarity_coverage = (total_similarities / max_possible * 100) if max_possible > 0 else 0
        
        # Check user engagement
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        users_with_reviews = User.objects.annotate(
            review_count=Count('reviews')
        ).filter(review_count__gt=0).count()
        
        engagement_rate = (users_with_reviews / total_users * 100) if total_users > 0 else 0
        
        # Overall health
        health_status = 'healthy'
        issues = []
        
        if not db_ok:
            health_status = 'critical'
            issues.append('Database connection failed')
        
        if similarity_coverage < 10:
            health_status = 'warning' if health_status == 'healthy' else health_status
            issues.append('Low similarity coverage')
        
        if engagement_rate < 20:
            health_status = 'warning' if health_status == 'healthy' else health_status
            issues.append('Low user engagement')
        
        return Response({
            'status': 'success',
            'health': {
                'overall_status': health_status,
                'database_ok': db_ok,
                'similarity_coverage': round(similarity_coverage, 2),
                'active_users_percentage': round((active_users / total_users * 100), 2) if total_users > 0 else 0,
                'user_engagement_rate': round(engagement_rate, 2),
                'issues': issues
            }
        })
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e),
            'health': {
                'overall_status': 'critical',
                'issues': [str(e)]
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# =============================================================================
# BOOKS MANAGEMENT
# =============================================================================

@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def books_management(request):
    """
    GET: List books with filtering
    POST: Create new book
    """
    if request.method == 'GET':
        books = Book.objects.all()
        
        # Search
        search = request.GET.get('search')
        if search:
            books = books.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
        
        # Filter by category
        category = request.GET.get('category')
        if category:
            books = books.filter(categories__name__icontains=category)
        
        # Annotate
        books = books.annotate(
            review_count=Count('reviews'),
            avg_rating=Avg('reviews__rating')
        ).distinct().order_by('-created_at')
        
        # Pagination
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        start = (page - 1) * page_size
        end = start + page_size
        
        total = books.count()
        paginated_books = books[start:end]
        
        book_data = []
        for book in paginated_books:
            book_data.append({
                'id': book.id,
                'title': book.title,
                'authors': book.author_names,
                'description': book.description[:100] + '...' if book.description and len(book.description) > 100 else book.description,
                'price': str(book.price) if book.price else None,
                'publish_year': book.publish_year,
                'review_count': book.review_count,
                'avg_rating': round(book.avg_rating, 2) if book.avg_rating else None,
                'created_at': book.created_at,
            })
        
        return Response({
            'status': 'success',
            'books': book_data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': total,
                'total_pages': (total + page_size - 1) // page_size
            }
        })
    
    elif request.method == 'POST':
        # Create new book (simplified)
        try:
            title = request.data.get('title')
            if not title:
                return Response({
                    'status': 'error',
                    'message': 'Title is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            book = Book.objects.create(
                title=title,
                description=request.data.get('description', ''),
                price=request.data.get('price'),
                publish_year=request.data.get('publish_year'),
            )
            
            return Response({
                'status': 'success',
                'message': 'Book created successfully',
                'book': {
                    'id': book.id,
                    'title': book.title
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdminUser])
def book_detail(request, book_id):
    """
    GET: Get book details
    PUT: Update book
    DELETE: Delete book
    """
    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Book not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        return Response({
            'status': 'success',
            'book': {
                'id': book.id,
                'title': book.title,
                'description': book.description,
                'price': str(book.price) if book.price else None,
                'publish_year': book.publish_year,
                'isbn': book.isbn,
                'authors': book.author_names,
                'review_count': book.reviews.count(),
                'avg_rating': book.average_rating,
            }
        })
    
    elif request.method == 'PUT':
        try:
            if 'title' in request.data:
                book.title = request.data['title']
            if 'description' in request.data:
                book.description = request.data['description']
            if 'price' in request.data:
                book.price = request.data['price']
            if 'publish_year' in request.data:
                book.publish_year = request.data['publish_year']
            
            book.save()
            
            return Response({
                'status': 'success',
                'message': 'Book updated successfully',
                'book': {
                    'id': book.id,
                    'title': book.title
                }
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    elif request.method == 'DELETE':
        try:
            book.delete()
            return Response({
                'status': 'success',
                'message': 'Book deleted successfully'
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =============================================================================
# REVIEWS MANAGEMENT
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAdminUser])
def reviews_management(request):
    """
    List all reviews with filtering
    """
    reviews = BookReview.objects.select_related('user', 'book').all()
    
    # Search by user or book
    search = request.GET.get('search')
    if search:
        reviews = reviews.filter(
            Q(user__username__icontains=search) |
            Q(book__title__icontains=search) |
            Q(review_text__icontains=search)
        )
    
    # Filter by rating
    rating = request.GET.get('rating')
    if rating:
        reviews = reviews.filter(rating=int(rating))
    
    reviews = reviews.order_by('-created_at')
    
    # Pagination
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    start = (page - 1) * page_size
    end = start + page_size
    
    total = reviews.count()
    paginated_reviews = reviews[start:end]
    
    review_data = []
    for review in paginated_reviews:
        review_data.append({
            'id': review.id,
            'user': review.user.username,
            'user_id': review.user.id,
            'book': review.book.title,
            'book_id': review.book.id,
            'rating': review.rating,
            'review_text': review.review_text[:100] + '...' if review.review_text and len(review.review_text) > 100 else review.review_text,
            'created_at': review.created_at,
        })
    
    return Response({
        'status': 'success',
        'reviews': review_data,
        'pagination': {
            'page': page,
            'page_size': page_size,
            'total': total,
            'total_pages': (total + page_size - 1) // page_size
        }
    })


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_review(request, review_id):
    """
    Delete a review
    """
    try:
        review = BookReview.objects.get(id=review_id)
        review.delete()
        
        return Response({
            'status': 'success',
            'message': 'Review deleted successfully'
        })
    except BookReview.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Review not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def update_review(request, review_id):
    """
    Update review
    """
    try:
        review = BookReview.objects.get(id=review_id)
        
        if 'rating' in request.data:
            rating = int(request.data['rating'])
            if not (1 <= rating <= 10):
                return Response({
                    'status': 'error',
                    'message': 'Rating must be between 1 and 10'
                }, status=status.HTTP_400_BAD_REQUEST)
            review.rating = rating
        
        if 'review_text' in request.data:
            review.review_text = request.data['review_text']
        
        review.save()
        
        return Response({
            'status': 'success',
            'message': 'Review updated successfully'
        })
        
    except BookReview.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Review not found'
        }, status=status.HTTP_404_NOT_FOUND)
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
def badges_management(request):
    """
    GET: List all badges
    POST: Create new badge
    """
    if request.method == 'GET':
        badges = Badge.objects.all().order_by('category', 'order')
        
        badge_data = []
        for badge in badges:
            badge_data.append({
                'id': badge.id,
                'name': badge.name,
                'slug': badge.slug,
                'icon': badge.icon,
                'description': badge.description,
                'category': badge.category,
                'rarity': badge.rarity,
                'requirement_type': badge.requirement_type,
                'requirement_value': badge.requirement_value,
                'points': badge.points,
                'is_active': badge.is_active,
                'is_hidden': badge.is_hidden,
                'users_earned': UserBadge.objects.filter(badge=badge, completed=True).count()
            })
        
        return Response({
            'status': 'success',
            'badges': badge_data,
            'total': len(badge_data)
        })
    
    elif request.method == 'POST':
        try:
            badge = Badge.objects.create(
                name=request.data['name'],
                slug=request.data['slug'],
                description=request.data['description'],
                icon=request.data.get('icon', '🏆'),
                category=request.data['category'],
                rarity=request.data.get('rarity', 'common'),
                requirement_type=request.data['requirement_type'],
                requirement_value=request.data['requirement_value'],
                points=request.data.get('points', 10),
                is_active=request.data.get('is_active', True),
                is_hidden=request.data.get('is_hidden', False),
            )
            
            return Response({
                'status': 'success',
                'message': 'Badge created successfully',
                'badge': {
                    'id': badge.id,
                    'name': badge.name
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdminUser])
def badge_detail(request, badge_id):
    """
    GET: Get badge details
    PUT: Update badge
    DELETE: Delete badge
    """
    try:
        badge = Badge.objects.get(id=badge_id)
    except Badge.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Badge not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        return Response({
            'status': 'success',
            'badge': {
                'id': badge.id,
                'name': badge.name,
                'slug': badge.slug,
                'description': badge.description,
                'icon': badge.icon,
                'category': badge.category,
                'rarity': badge.rarity,
                'requirement_type': badge.requirement_type,
                'requirement_value': badge.requirement_value,
                'points': badge.points,
                'is_active': badge.is_active,
                'is_hidden': badge.is_hidden,
            }
        })
    
    elif request.method == 'PUT':
        try:
            for field in ['name', 'description', 'icon', 'category', 'rarity', 
                         'requirement_type', 'requirement_value', 'points', 
                         'is_active', 'is_hidden']:
                if field in request.data:
                    setattr(badge, field, request.data[field])
            
            badge.save()
            
            return Response({
                'status': 'success',
                'message': 'Badge updated successfully'
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    elif request.method == 'DELETE':
        try:
            badge.delete()
            return Response({
                'status': 'success',
                'message': 'Badge deleted successfully'
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =============================================================================
# CATEGORIES MANAGEMENT
# =============================================================================

@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def categories_management(request):
    """
    GET: List all categories
    POST: Create new category
    """
    if request.method == 'GET':
        categories = Category.objects.annotate(
            book_count=Count('books')
        ).order_by('name')
        
        category_data = []
        for cat in categories:
            category_data.append({
                'id': cat.id,
                'name': cat.name,
                'book_count': cat.book_count,
                'created_at': cat.created_at,
            })
        
        return Response({
            'status': 'success',
            'categories': category_data,
            'total': len(category_data)
        })
    
    elif request.method == 'POST':
        try:
            name = request.data.get('name')
            if not name:
                return Response({
                    'status': 'error',
                    'message': 'Name is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if Category.objects.filter(name=name).exists():
                return Response({
                    'status': 'error',
                    'message': 'Category already exists'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            category = Category.objects.create(name=name)
            
            return Response({
                'status': 'success',
                'message': 'Category created successfully',
                'category': {
                    'id': category.id,
                    'name': category.name
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT', 'DELETE'])
@permission_classes([IsAdminUser])
def category_detail(request, category_id):
    """
    PUT: Update category
    DELETE: Delete category
    """
    try:
        category = Category.objects.get(id=category_id)
    except Category.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Category not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'PUT':
        try:
            name = request.data.get('name')
            if name:
                category.name = name
                category.save()
            
            return Response({
                'status': 'success',
                'message': 'Category updated successfully'
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    elif request.method == 'DELETE':
        try:
            category.delete()
            return Response({
                'status': 'success',
                'message': 'Category deleted successfully'
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
# =============================================================================
# AUTHORS MANAGEMENT
# =============================================================================

@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def authors_management(request):
    """
    GET: List all authors
    POST: Create new author
    """
    if request.method == 'GET':
        authors = Author.objects.annotate(
            book_count=Count('books')
        ).order_by('last_name', 'first_name')
        
        # Search
        search = request.GET.get('search')
        if search:
            authors = authors.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        # Pagination
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        start = (page - 1) * page_size
        end = start + page_size
        
        total = authors.count()
        paginated_authors = authors[start:end]
        
        author_data = []
        for author in paginated_authors:
            author_data.append({
                'id': author.id,
                'first_name': author.first_name,
                'last_name': author.last_name,
                'full_name': author.full_name,
                'book_count': author.book_count,
                'created_at': author.created_at,
            })
        
        return Response({
            'status': 'success',
            'authors': author_data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': total,
                'total_pages': (total + page_size - 1) // page_size
            }
        })
    
    elif request.method == 'POST':
        try:
            first_name = request.data.get('first_name', '')
            last_name = request.data.get('last_name')
            
            if not last_name:
                return Response({
                    'status': 'error',
                    'message': 'Last name is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if author already exists
            if Author.objects.filter(first_name=first_name, last_name=last_name).exists():
                return Response({
                    'status': 'error',
                    'message': 'Author already exists'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            author = Author.objects.create(
                first_name=first_name,
                last_name=last_name
            )
            
            return Response({
                'status': 'success',
                'message': 'Author created successfully',
                'author': {
                    'id': author.id,
                    'full_name': author.full_name
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdminUser])
def author_detail(request, author_id):
    """
    GET: Get author details
    PUT: Update author
    DELETE: Delete author
    """
    try:
        author = Author.objects.get(id=author_id)
    except Author.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Author not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        # Get author's books
        books = author.books.all()[:10]
        book_list = [{'id': book.id, 'title': book.title} for book in books]
        
        return Response({
            'status': 'success',
            'author': {
                'id': author.id,
                'first_name': author.first_name,
                'last_name': author.last_name,
                'full_name': author.full_name,
                'book_count': author.books.count(),
                'books': book_list,
                'created_at': author.created_at,
            }
        })
    
    elif request.method == 'PUT':
        try:
            if 'first_name' in request.data:
                author.first_name = request.data['first_name']
            if 'last_name' in request.data:
                author.last_name = request.data['last_name']
            
            author.save()
            
            return Response({
                'status': 'success',
                'message': 'Author updated successfully',
                'author': {
                    'id': author.id,
                    'full_name': author.full_name
                }
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    elif request.method == 'DELETE':
        try:
            book_count = author.books.count()
            if book_count > 0:
                return Response({
                    'status': 'error',
                    'message': f'Cannot delete author with {book_count} books. Remove books first.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            author.delete()
            return Response({
                'status': 'success',
                'message': 'Author deleted successfully'
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =============================================================================
# PUBLISHERS MANAGEMENT
# =============================================================================

@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def publishers_management(request):
    """
    GET: List all publishers
    POST: Create new publisher
    """
    if request.method == 'GET':
        publishers = Publisher.objects.annotate(
            book_count=Count('books')
        ).order_by('name')
        
        # Search
        search = request.GET.get('search')
        if search:
            publishers = publishers.filter(name__icontains=search)
        
        # Pagination
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        start = (page - 1) * page_size
        end = start + page_size
        
        total = publishers.count()
        paginated_publishers = publishers[start:end]
        
        publisher_data = []
        for publisher in paginated_publishers:
            publisher_data.append({
                'id': publisher.id,
                'name': publisher.name,
                'book_count': publisher.book_count,
                'created_at': publisher.created_at,
            })
        
        return Response({
            'status': 'success',
            'publishers': publisher_data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': total,
                'total_pages': (total + page_size - 1) // page_size
            }
        })
    
    elif request.method == 'POST':
        try:
            name = request.data.get('name')
            
            if not name:
                return Response({
                    'status': 'error',
                    'message': 'Name is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if Publisher.objects.filter(name=name).exists():
                return Response({
                    'status': 'error',
                    'message': 'Publisher already exists'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            publisher = Publisher.objects.create(name=name)
            
            return Response({
                'status': 'success',
                'message': 'Publisher created successfully',
                'publisher': {
                    'id': publisher.id,
                    'name': publisher.name
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdminUser])
def publisher_detail(request, publisher_id):
    """
    GET: Get publisher details
    PUT: Update publisher
    DELETE: Delete publisher
    """
    try:
        publisher = Publisher.objects.get(id=publisher_id)
    except Publisher.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Publisher not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        # Get publisher's books
        books = publisher.books.all()[:10]
        book_list = [{'id': book.id, 'title': book.title} for book in books]
        
        return Response({
            'status': 'success',
            'publisher': {
                'id': publisher.id,
                'name': publisher.name,
                'book_count': publisher.books.count(),
                'books': book_list,
                'created_at': publisher.created_at,
            }
        })
    
    elif request.method == 'PUT':
        try:
            if 'name' in request.data:
                publisher.name = request.data['name']
                publisher.save()
            
            return Response({
                'status': 'success',
                'message': 'Publisher updated successfully',
                'publisher': {
                    'id': publisher.id,
                    'name': publisher.name
                }
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    elif request.method == 'DELETE':
        try:
            book_count = publisher.books.count()
            if book_count > 0:
                return Response({
                    'status': 'error',
                    'message': f'Cannot delete publisher with {book_count} books. Remove books first.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            publisher.delete()
            return Response({
                'status': 'success',
                'message': 'Publisher deleted successfully'
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)