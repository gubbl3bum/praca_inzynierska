from django.shortcuts import render
from django.db.models import Q, Avg, Count
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import PredictionRequest, PredictionResult, Book, User, Rating
from .serializers import PredictionRequestSerializer, PredictionResultSerializer, BookSerializer, BookListSerializer
from .ml_model import predict
import os
from django.utils import timezone

@api_view(['POST'])
def prediction(request):
    serializer = PredictionRequestSerializer(data=request.data)
    if serializer.is_valid():
        prediction_request = serializer.save()
        
        # Przygotuj dane dla modelu ML
        features = [
            prediction_request.feature1,
            prediction_request.feature2,
            prediction_request.feature3,
            prediction_request.feature4,
        ]
        
        # Uzyskaj predykcję z modelu ML
        prediction_value, confidence = predict(features)
        
        # Zapisz wynik
        prediction_result = PredictionResult.objects.create(
            request=prediction_request,
            prediction=prediction_value,
            confidence=confidence
        )
        
        # Zwróć wynik
        result_serializer = PredictionResultSerializer(prediction_result)
        return Response(result_serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def prediction_history(request):
    results = PredictionResult.objects.all().order_by('-created_at')[:10]
    serializer = PredictionResultSerializer(results, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def api_status(request):
    """Endpoint pokazujący status API i statystyki"""
    try:
        # Zbierz statystyki
        prediction_count = PredictionRequest.objects.count()
        result_count = PredictionResult.objects.count()
        
        # Znajdź najnowszą predykcję
        latest_prediction = PredictionResult.objects.order_by('-created_at').first()
        
        # Sprawdź czy model istnieje
        model_path = os.path.join(os.path.dirname(__file__), 'model.pkl')
        model_exists = os.path.exists(model_path)
        
        # Nowe statystyki dla ujednoliconego schematu
        books_count = Book.objects.count()
        users_count = User.objects.count()
        ratings_count = Rating.objects.count()
        
        # Przygotuj response
        response_data = {
            'status': 'healthy',
            'timestamp': timezone.now(),
            'version': '1.0.0',
            'database': {
                'connected': True,
                'total_predictions': prediction_count,
                'total_results': result_count,
                'total_books': books_count,
                'total_users': users_count,
                'total_ratings': ratings_count
            },
            'ml_model': {
                'loaded': model_exists,
                'path': model_path
            },
            'latest_prediction': None
        }
        
        if latest_prediction:
            response_data['latest_prediction'] = {
                'id': latest_prediction.id,
                'prediction': latest_prediction.prediction,
                'confidence': latest_prediction.confidence,
                'created_at': latest_prediction.created_at
            }
            
        return Response(response_data)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e),
            'timestamp': timezone.now()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ZAKTUALIZOWANE ENDPOINTY DLA UJEDNOLICONEGO SCHEMATU

@api_view(['GET'])
def books_list(request):
    """Lista wszystkich książek z opcjonalnymi filtrami"""
    try:
        books = Book.objects.all()
        
        # Filtry z query params
        search = request.GET.get('search')
        if search:
            books = books.filter(
                Q(title__icontains=search) | 
                Q(author__icontains=search)
            )
        
        category = request.GET.get('category')
        if category:
            books = books.filter(categories__contains=[category])
        
        # Paginacja
        limit = min(int(request.GET.get('limit', 20)), 100)
        offset = int(request.GET.get('offset', 0))
        
        total_count = books.count()
        books = books[offset:offset + limit]
        
        serializer = BookListSerializer(books, many=True)
        
        return Response({
            'count': total_count,
            'results': serializer.data,
            'limit': limit,
            'offset': offset
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def books_featured(request):
    """Zwraca polecane książki dla strony głównej - UJEDNOLICONY SCHEMAT"""
    try:
        # POPRAWIONE: Użyj nowego modelu Rating zamiast starych tabel
        
        # Top rated books - książki z najwyższą średnią oceną z ujednoliconej tabeli ratings
        top_rated = Book.objects.annotate(
            avg_rating=Avg('ratings__rating'),
            rating_count=Count('ratings')
        ).filter(
            avg_rating__isnull=False,
            rating_count__gte=5  # Minimum 5 ocen
        ).order_by('-avg_rating', '-rating_count')[:8]
        
        # Recent books - ostatnio dodane
        recent = Book.objects.order_by('-created_at')[:8]
        
        # Popular books - z największą liczbą ocen
        popular = Book.objects.annotate(
            rating_count=Count('ratings')
        ).filter(
            rating_count__gt=0
        ).order_by('-rating_count')[:8]
        
        # Jeśli nie ma wystarczająco danych, użyj wszystkich dostępnych książek
        if not top_rated.exists():
            all_books = Book.objects.all()[:8]
            top_rated = all_books
            
        if not popular.exists():
            popular = Book.objects.all()[:8]
        
        response_data = {
            'top_rated': BookListSerializer(top_rated, many=True).data,
            'recent': BookListSerializer(recent, many=True).data,
            'popular': BookListSerializer(popular, many=True).data
        }
        
        return Response(response_data)
        
    except Exception as e:
        # Lepsze error handling z logowaniem
        import traceback
        error_details = {
            'error': str(e),
            'traceback': traceback.format_exc(),
            'top_rated': [],
            'recent': [],
            'popular': []
        }
        print(f"Error in books_featured: {error_details}")  # Log do konsoli
        
        return Response({
            'error': str(e),
            'top_rated': [],
            'recent': [],
            'popular': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def book_detail(request, book_id):
    """Szczegóły pojedynczej książki"""
    try:
        book = Book.objects.get(id=book_id)
        serializer = BookSerializer(book)
        return Response(serializer.data)
        
    except Book.DoesNotExist:
        return Response({
            'error': 'Book not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def books_search(request):
    """Wyszukiwanie książek"""
    try:
        query = request.GET.get('q', '').strip()
        
        if not query:
            return Response({
                'error': 'Search query is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        books = Book.objects.filter(
            Q(title__icontains=query) | 
            Q(author__icontains=query) |
            Q(description__icontains=query)
        )
        
        # Limit rezultatów
        limit = min(int(request.GET.get('limit', 20)), 50)
        books = books[:limit]
        
        serializer = BookListSerializer(books, many=True)
        
        return Response({
            'query': query,
            'count': len(serializer.data),
            'results': serializer.data
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# NOWE ENDPOINTY DLA UJEDNOLICONEGO SCHEMATU

@api_view(['GET'])
def users_stats(request):
    """Statystyki użytkowników"""
    try:
        dataset_users = User.objects.filter(user_type='dataset').count()
        app_users = User.objects.filter(user_type='app').count()
        
        return Response({
            'dataset_users': dataset_users,
            'app_users': app_users,
            'total_users': dataset_users + app_users
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def ratings_stats(request):
    """Statystyki ocen"""
    try:
        dataset_ratings = Rating.objects.filter(source_type='dataset').count()
        app_ratings = Rating.objects.filter(source_type='app').count()
        
        avg_rating = Rating.objects.aggregate(avg=Avg('rating'))['avg']
        
        return Response({
            'dataset_ratings': dataset_ratings,
            'app_ratings': app_ratings,
            'total_ratings': dataset_ratings + app_ratings,
            'average_rating': round(avg_rating, 2) if avg_rating else 0
        })
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)