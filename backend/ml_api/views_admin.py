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
            # All books (limited for safety)
            limit = int(request.data.get('limit', 10))
            books = Book.objects.all()[:limit]
            
            total_count = 0
            for book in books:
                count = service.calculate_similarities_for_book(book, batch_size=batch_size)
                total_count += count
            
            return Response({
                'status': 'success',
                'message': f'Recalculated similarities for {len(books)} books',
                'total_similarities_created': total_count
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
            # All users (limited for safety)
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
                'message': f'Recalculated similarities for {len(users)} users',
                'total_similarities_created': total_count
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