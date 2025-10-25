from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from django.utils import timezone

from .models import BookList, BookListItem, ReadingProgress, Book
from .serializers import (
    BookListDetailSerializer,
    BookListSimpleSerializer,
    BookListCreateUpdateSerializer,
    BookListItemSerializer,
    ReadingProgressSerializer,
    AddToListSerializer
)

# =============================================================================
# BOOK LISTS VIEWS
# =============================================================================

@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def user_book_lists(request):
    """
    GET: Get all user's book lists
    POST: Create new book list
    """
    user = request.user
    
    if request.method == 'GET':
        # Get all user's lists
        lists = BookList.objects.filter(user=user).annotate(
            book_count=Count('items')
        ).order_by('-is_default', '-created_at')
        
        # Optional filter by type
        list_type = request.GET.get('type')
        if list_type:
            lists = lists.filter(list_type=list_type)
        
        serializer = BookListSimpleSerializer(lists, many=True)
        
        return Response({
            'status': 'success',
            'lists': serializer.data,
            'count': lists.count()
        })
    
    elif request.method == 'POST':
        # Create new list
        serializer = BookListCreateUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            # Check if list with this name already exists
            if BookList.objects.filter(
                user=user, 
                name=serializer.validated_data['name']
            ).exists():
                return Response({
                    'status': 'error',
                    'message': 'List with this name already exists'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            book_list = serializer.save(user=user)
            
            return Response({
                'status': 'success',
                'message': 'List created successfully',
                'list': BookListSimpleSerializer(book_list).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'status': 'error',
            'message': 'Validation error',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def book_list_detail(request, list_id):
    """
    GET: Get book list details with items
    PUT: Update book list
    DELETE: Delete book list
    """
    user = request.user
    book_list = get_object_or_404(BookList, id=list_id, user=user)
    
    if request.method == 'GET':
        serializer = BookListDetailSerializer(book_list)
        return Response({
            'status': 'success',
            'list': serializer.data
        })
    
    elif request.method == 'PUT':
        # Prevent updating default lists' core properties
        if book_list.is_default:
            # Only allow updating description and is_public
            allowed_fields = ['description', 'is_public']
            data = {k: v for k, v in request.data.items() if k in allowed_fields}
        else:
            data = request.data
        
        serializer = BookListCreateUpdateSerializer(
            book_list, 
            data=data, 
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'message': 'List updated successfully',
                'list': BookListSimpleSerializer(book_list).data
            })
        
        return Response({
            'status': 'error',
            'message': 'Validation error',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        # Prevent deleting default lists
        if book_list.is_default:
            return Response({
                'status': 'error',
                'message': 'Cannot delete default list'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        book_list.delete()
        
        return Response({
            'status': 'success',
            'message': 'List deleted successfully'
        })

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_to_list(request, list_id):
    """Add book to list"""
    user = request.user
    book_list = get_object_or_404(BookList, id=list_id, user=user)
    
    serializer = AddToListSerializer(data=request.data)
    
    if serializer.is_valid():
        book_id = serializer.validated_data['book_id']
        book = get_object_or_404(Book, id=book_id)
        
        # Check if book already in list
        if BookListItem.objects.filter(book_list=book_list, book=book).exists():
            return Response({
                'status': 'error',
                'message': 'Book already in this list'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Add to list
        item = BookListItem.objects.create(
            book_list=book_list,
            book=book,
            notes=serializer.validated_data.get('notes', ''),
            priority=serializer.validated_data.get('priority', 0)
        )
        
        return Response({
            'status': 'success',
            'message': 'Book added to list',
            'item': BookListItemSerializer(item).data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'status': 'error',
        'message': 'Validation error',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE', 'PUT'])
@permission_classes([permissions.IsAuthenticated])
def list_item_detail(request, list_id, item_id):
    """
    DELETE: Remove book from list
    PUT: Update list item (notes, priority)
    """
    user = request.user
    book_list = get_object_or_404(BookList, id=list_id, user=user)
    item = get_object_or_404(BookListItem, id=item_id, book_list=book_list)
    
    if request.method == 'DELETE':
        item.delete()
        return Response({
            'status': 'success',
            'message': 'Book removed from list'
        })
    
    elif request.method == 'PUT':
        # Update notes and/or priority
        if 'notes' in request.data:
            item.notes = request.data['notes']
        if 'priority' in request.data:
            item.priority = request.data['priority']
        
        item.save()
        
        return Response({
            'status': 'success',
            'message': 'Item updated',
            'item': BookListItemSerializer(item).data
        })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def initialize_default_lists(request):
    """Initialize default lists for user"""
    user = request.user
    lists = BookList.get_or_create_default_lists(user)
    
    return Response({
        'status': 'success',
        'message': 'Default lists initialized',
        'lists': BookListSimpleSerializer(lists, many=True).data
    })

# =============================================================================
# READING PROGRESS VIEWS
# =============================================================================

@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def reading_progress_list(request):
    """
    GET: Get all reading progress for user
    POST: Create/update reading progress
    """
    user = request.user
    
    if request.method == 'GET':
        # Filter by status
        status_filter = request.GET.get('status')
        
        progress = ReadingProgress.objects.filter(user=user)
        
        if status_filter:
            progress = progress.filter(status=status_filter)
        
        progress = progress.order_by('-updated_at')
        
        serializer = ReadingProgressSerializer(progress, many=True)
        
        return Response({
            'status': 'success',
            'progress': serializer.data,
            'count': progress.count()
        })
    
    elif request.method == 'POST':
        serializer = ReadingProgressSerializer(data=request.data)
        
        if serializer.is_valid():
            book_id = serializer.validated_data['book_id']
            book = get_object_or_404(Book, id=book_id)
            
            # Get or create progress
            progress, created = ReadingProgress.objects.get_or_create(
                user=user,
                book=book,
                defaults={
                    'status': serializer.validated_data.get('status', 'not_started'),
                    'progress_percentage': serializer.validated_data.get('progress_percentage', 0)
                }
            )
            
            if not created:
                # Update existing
                for field in ['status', 'progress_percentage', 'current_page', 'total_pages']:
                    if field in serializer.validated_data:
                        setattr(progress, field, serializer.validated_data[field])
                progress.save()
            
            return Response({
                'status': 'success',
                'message': 'Progress updated',
                'progress': ReadingProgressSerializer(progress).data
            }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        
        return Response({
            'status': 'error',
            'message': 'Validation error',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def reading_progress_detail(request, progress_id):
    """
    GET: Get reading progress details
    PUT: Update reading progress
    DELETE: Delete reading progress
    """
    user = request.user
    progress = get_object_or_404(ReadingProgress, id=progress_id, user=user)
    
    if request.method == 'GET':
        serializer = ReadingProgressSerializer(progress)
        return Response({
            'status': 'success',
            'progress': serializer.data
        })
    
    elif request.method == 'PUT':
        serializer = ReadingProgressSerializer(progress, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'message': 'Progress updated',
                'progress': serializer.data
            })
        
        return Response({
            'status': 'error',
            'message': 'Validation error',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        progress.delete()
        return Response({
            'status': 'success',
            'message': 'Progress deleted'
        })

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_reading_progress_percentage(request, book_id):
    """Quick update of reading progress percentage"""
    user = request.user
    book = get_object_or_404(Book, id=book_id)
    
    percentage = request.data.get('percentage')
    current_page = request.data.get('current_page')
    total_pages = request.data.get('total_pages')
    
    if percentage is None and (current_page is None or total_pages is None):
        return Response({
            'status': 'error',
            'message': 'Provide either percentage or current_page and total_pages'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Get or create progress
    progress, created = ReadingProgress.objects.get_or_create(
        user=user,
        book=book
    )
    
    # Update progress
    progress.update_progress(
        percentage=percentage,
        page=current_page,
        total=total_pages
    )
    
    return Response({
        'status': 'success',
        'message': 'Progress updated',
        'progress': ReadingProgressSerializer(progress).data
    })

# =============================================================================
# QUICK ACTION VIEWS
# =============================================================================

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def quick_add_to_favorites(request, book_id):
    """Quick add to favorites"""
    user = request.user
    book = get_object_or_404(Book, id=book_id)
    
    # Get or create favorites list
    favorites_list, _ = BookList.objects.get_or_create(
        user=user,
        list_type='favorites',
        defaults={'name': 'Favorites', 'is_default': True}
    )
    
    # Check if already in favorites
    if BookListItem.objects.filter(book_list=favorites_list, book=book).exists():
        return Response({
            'status': 'error',
            'message': 'Book already in favorites'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Add to favorites
    BookListItem.objects.create(
        book_list=favorites_list,
        book=book
    )
    
    return Response({
        'status': 'success',
        'message': 'Added to favorites'
    })

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def quick_add_to_reading(request, book_id):
    """Quick add to currently reading"""
    user = request.user
    book = get_object_or_404(Book, id=book_id)
    
    # Get or create reading list
    reading_list, _ = BookList.objects.get_or_create(
        user=user,
        list_type='reading',
        defaults={'name': 'Currently Reading', 'is_default': True}
    )
    
    # Check if already in reading
    if BookListItem.objects.filter(book_list=reading_list, book=book).exists():
        return Response({
            'status': 'error',
            'message': 'Book already in reading list'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Add to reading
    BookListItem.objects.create(
        book_list=reading_list,
        book=book
    )
    
    # Also create reading progress
    ReadingProgress.objects.get_or_create(
        user=user,
        book=book,
        defaults={
            'status': 'reading',
            'started_at': timezone.now()
        }
    )
    
    return Response({
        'status': 'success',
        'message': 'Added to currently reading'
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def check_book_in_lists(request, book_id):
    """Check which lists contain this book"""
    user = request.user
    book = get_object_or_404(Book, id=book_id)
    
    # Get all user's lists that contain this book
    lists = BookList.objects.filter(
        user=user,
        items__book=book
    ).values('id', 'name', 'list_type', 'is_default')
    
    # Get reading progress
    progress = None
    try:
        progress_obj = ReadingProgress.objects.get(user=user, book=book)
        progress = ReadingProgressSerializer(progress_obj).data
    except ReadingProgress.DoesNotExist:
        pass
    
    return Response({
        'status': 'success',
        'book_id': book_id,
        'in_lists': list(lists),
        'reading_progress': progress
    })
