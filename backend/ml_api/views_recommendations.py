from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import User
from .services.user_similarity_service import get_user_similarity_service
from .serializers import BookListSerializer


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def collaborative_recommendations(request, user_id=None):
    """
    Get collaborative filtering recommendations
    Based on similar users
    """
    # Use authenticated user or specified user
    if user_id:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
    else:
        user = request.user
    
    # Parameters
    limit = min(int(request.GET.get('limit', 10)), 50)
    min_similarity = float(request.GET.get('min_similarity', 0.3))
    
    # Get service
    service = get_user_similarity_service()
    
    # Get recommendations
    recommendations = service.get_collaborative_recommendations(
        user,
        limit=limit,
        min_similarity=min_similarity
    )
    
    # Format response
    results = []
    for rec in recommendations:
        book_data = BookListSerializer(rec['book']).data
        book_data['recommendation_score'] = rec['recommendation_score']
        book_data['recommendation_type'] = rec['recommendation_type']
        book_data['recommendation_reason'] = rec['reason']
        results.append(book_data)
    
    return Response({
        'status': 'success',
        'user': {
            'id': user.id,
            'username': user.username
        },
        'recommendations': results,
        'count': len(results),
        'method': 'collaborative_filtering'
    })