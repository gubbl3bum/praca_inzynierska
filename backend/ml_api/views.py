from django.shortcuts import render
from django.db.models import Q
from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .models import PredictionRequest, PredictionResult, Book
from .serializers import (
    PredictionRequestSerializer, 
    PredictionResultSerializer, 
    BookSerializer, 
    BookListSerializer
)
from .ml_model import predict

# Istniejące widoki ML
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


# Nowe widoki dla książek
class BookPagination(PageNumberPagination):
    page_size = 12  # 12 książek na stronę
    page_size_query_param = 'page_size'
    max_page_size = 100

class BookListView(generics.ListAPIView):
    """
    Zwraca listę wszystkich książek z opcjonalnym filtrowaniem i wyszukiwaniem
    """
    queryset = Book.objects.all()
    serializer_class = BookListSerializer
    pagination_class = BookPagination
    
    def get_queryset(self):
        queryset = Book.objects.all()
        
        # Wyszukiwanie po tytule i autorze
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(author__icontains=search)
            )
        
        # Filtrowanie po kategorii
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(categories__icontains=category)
        
        # Filtrowanie po autorze
        author = self.request.query_params.get('author', None)
        if author:
            queryset = queryset.filter(author__icontains=author)
        
        # Sortowanie
        ordering = self.request.query_params.get('ordering', '-created_at')
        if ordering in ['title', '-title', 'author', '-author', 'average_rating', '-average_rating', 'created_at', '-created_at']:
            queryset = queryset.order_by(ordering)
        
        return queryset

class BookDetailView(generics.RetrieveAPIView):
    """
    Zwraca szczegóły pojedynczej książki
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer

@api_view(['GET'])
def featured_books(request):
    """
    Zwraca polecane książki dla strony głównej
    """
    # Pobierz najlepiej oceniane książki
    top_rated = Book.objects.filter(
        average_rating__gte=4.0
    ).order_by('-average_rating', '-ratings_count')[:8]
    
    # Pobierz najnowsze książki
    recent = Book.objects.order_by('-created_at')[:8]
    
    # Pobierz popularne książki (najwięcej ocen)
    popular = Book.objects.order_by('-ratings_count')[:8]
    
    data = {
        'top_rated': BookListSerializer(top_rated, many=True).data,
        'recent': BookListSerializer(recent, many=True).data,
        'popular': BookListSerializer(popular, many=True).data,
    }
    
    return Response(data)

@api_view(['GET'])
def book_categories(request):
    """
    Zwraca listę wszystkich dostępnych kategorii
    """
    # Pobierz wszystkie niepuste kategorie
    categories_raw = Book.objects.exclude(
        categories__isnull=True
    ).exclude(
        categories__exact=''
    ).values_list('categories', flat=True)
    
    # Przekształć w płaską listę unikalnych kategorii
    all_categories = set()
    for cat_string in categories_raw:
        if cat_string:
            categories = [cat.strip() for cat in cat_string.split(',')]
            all_categories.update(categories)
    
    return Response(sorted(list(all_categories)))