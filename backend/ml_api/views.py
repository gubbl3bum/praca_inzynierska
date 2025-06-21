from django.shortcuts import render
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
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

@api_view(['GET'])
def books_list(request):
    """Lista wszystkich książek z opcjonalnymi filtrami i paginacją"""
    try:
        books = Book.objects.all()
        
        # Filtry z query params
        search = request.GET.get('search')
        if search:
            books = books.filter(
                Q(title__icontains=search) | 
                Q(author__icontains=search) |
                Q(description__icontains=search)
            )
        
        category = request.GET.get('category')
        if category:
            books = books.filter(categories__contains=[category])
            
        author = request.GET.get('author')
        if author:
            books = books.filter(author__icontains=author)
            
        # Filtry roku
        year_from = request.GET.get('year_from')
        if year_from:
            books = books.filter(publication_year__gte=int(year_from))
            
        year_to = request.GET.get('year_to')
        if year_to:
            books = books.filter(publication_year__lte=int(year_to))
            
        # Filtr ratingu
        rating_min = request.GET.get('rating_min')
        if rating_min:
            books = books.filter(average_rating__gte=float(rating_min))
        
        # Sortowanie
        sort = request.GET.get('sort', '-created_at')
        valid_sorts = [
            'title', '-title', 'author', '-author', 'created_at', '-created_at',
            'average_rating', '-average_rating', 'publication_year', '-publication_year'
        ]
        if sort in valid_sorts:
            books = books.order_by(sort)
        else:
            books = books.order_by('-created_at')
        
        # POPRAWIONA PAGINACJA
        page = int(request.GET.get('page', 1))
        page_size = min(int(request.GET.get('page_size', 20)), 100)  # max 100
        
        paginator = Paginator(books, page_size)
        page_obj = paginator.get_page(page)
        
        serializer = BookListSerializer(page_obj.object_list, many=True)
        
        return Response({
            'count': paginator.count,
            'num_pages': paginator.num_pages,
            'current_page': page_obj.number,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
            'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
            'results': serializer.data,
            'page_size': page_size
        })
        
    except Exception as e:
        return Response({
            'error': str(e),
            'count': 0,
            'results': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def books_top_rated(request):
    """Endpoint dla Top 100 książek z paginacją"""
    try:
        # Pobierz książki z oceną
        books = Book.objects.annotate(
            avg_rating=Avg('ratings__rating'),
            rating_count=Count('ratings')
        ).filter(
            avg_rating__isnull=False,
            avg_rating__gte=3.0,  # minimum 3.0
            rating_count__gte=1   # minimum 1 ocena
        )
        
        # Filtry czasowe
        time_filter = request.GET.get('filter', 'all')
        if time_filter == 'recent':
            current_year = timezone.now().year
            books = books.filter(publication_year__gte=current_year - 5)
        elif time_filter == 'classic':
            books = books.filter(publication_year__lt=2000)
        
        # Sortowanie według oceny
        books = books.order_by('-avg_rating', '-rating_count')
        
        # Paginacja
        page = int(request.GET.get('page', 1))
        page_size = min(int(request.GET.get('page_size', 20)), 100)
        
        paginator = Paginator(books, page_size)
        page_obj = paginator.get_page(page)
        
        serializer = BookListSerializer(page_obj.object_list, many=True)
        
        return Response({
            'count': min(paginator.count, 100),  # Limit do 100
            'num_pages': min(paginator.num_pages, 5),  # Max 5 stron (100/20)
            'current_page': page_obj.number,
            'has_next': page_obj.has_next() and page_obj.number < 5,
            'has_previous': page_obj.has_previous(),
            'next_page': page_obj.next_page_number() if page_obj.has_next() and page_obj.number < 5 else None,
            'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
            'results': serializer.data[:100],  # Zawsze max 100 wyników
            'page_size': page_size,
            'filter': time_filter
        })
        
    except Exception as e:
        return Response({
            'error': str(e),
            'count': 0,
            'results': []
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def books_featured(request):
    """Zwraca polecane książki dla strony głównej"""
    try:        
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