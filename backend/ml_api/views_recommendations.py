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
    user = request.user
    
    # Parameters
    limit = min(int(request.GET.get('limit', 24)), 50)
    min_similarity = float(request.GET.get('min_similarity', 0.3))
    
    # Get service
    service = get_user_similarity_service()
    
    try:
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
            book_data['recommendation_score'] = round(rec['recommendation_score'], 4)
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
    
    except Exception as e:
        print(f"Error in collaborative recommendations: {e}")
        import traceback
        traceback.print_exc()
        
        return Response({
            'status': 'error',
            'message': str(e),
            'recommendations': [],
            'count': 0
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)