from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Count

from .models import (
    UserPreferenceProfile, Category, Author, Publisher
)
from .serializers import (
    UserPreferenceProfileSerializer,
    CategorySimpleForPreferencesSerializer,
    AuthorSimpleForPreferencesSerializer,
    PublisherSimpleForPreferencesSerializer
)


@api_view(['GET'])
def get_preference_options(request):
    """
    Get all available options for preference form
    (categories, popular authors, publishers)
    """
    # Get all categories
    categories = Category.objects.all().order_by('name')
    
    # Get popular authors (with most books)
    authors = Author.objects.annotate(
        book_count=Count('books')
    ).filter(book_count__gt=0).order_by('-book_count', 'last_name')[:100]
    
    # Get popular publishers
    publishers = Publisher.objects.annotate(
        book_count=Count('books')
    ).filter(book_count__gt=0).order_by('-book_count', 'name')[:50]
    
    return Response({
        'status': 'success',
        'options': {
            'categories': CategorySimpleForPreferencesSerializer(categories, many=True).data,
            'authors': AuthorSimpleForPreferencesSerializer(authors, many=True).data,
            'publishers': PublisherSimpleForPreferencesSerializer(publishers, many=True).data
        }
    })


@api_view(['GET', 'POST', 'PUT'])
@permission_classes([permissions.IsAuthenticated])
def user_preference_profile(request):
    """
    GET: Get user's preference profile
    POST/PUT: Create or update preference profile
    """
    user = request.user
    
    if request.method == 'GET':
        try:
            profile = user.preference_profile
            serializer = UserPreferenceProfileSerializer(profile)
            return Response({
                'status': 'success',
                'profile': serializer.data
            })
        except UserPreferenceProfile.DoesNotExist:
            return Response({
                'status': 'success',
                'profile': None,
                'message': 'No preference profile yet'
            })
    
    elif request.method in ['POST', 'PUT']:
        try:
            profile = user.preference_profile
            serializer = UserPreferenceProfileSerializer(
                profile, 
                data=request.data,
                partial=True
            )
        except UserPreferenceProfile.DoesNotExist:
            serializer = UserPreferenceProfileSerializer(data=request.data)
        
        if serializer.is_valid():
            profile = serializer.save(user=user, completed=True)
            
            return Response({
                'status': 'success',
                'message': 'Preferences saved successfully!',
                'profile': UserPreferenceProfileSerializer(profile).data
            }, status=status.HTTP_200_OK)
        
        return Response({
            'status': 'error',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def check_preference_profile(request):
    """
    Check if user has completed preference profile
    Skip for staff users
    """
    user = request.user
    
    # Skip preference form for staff/admin users
    if user.is_staff:
        return Response({
            'status': 'success',
            'has_profile': True,  # Treat as if they have profile
            'should_show_form': False,  # Never show form for staff
            'is_staff': True
        })
    
    try:
        profile = user.preference_profile
        has_profile = profile.completed
    except UserPreferenceProfile.DoesNotExist:
        has_profile = False
    
    return Response({
        'status': 'success',
        'has_profile': has_profile,
        'should_show_form': not has_profile,
        'is_staff': False
    })