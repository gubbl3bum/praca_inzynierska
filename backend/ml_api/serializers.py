from rest_framework import serializers
from .models import PredictionRequest, PredictionResult, Book

class PredictionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PredictionRequest
        fields = ['id', 'feature1', 'feature2', 'feature3', 'feature4', 'created_at']
        read_only_fields = ['id', 'created_at']

class PredictionResultSerializer(serializers.ModelSerializer):
    request = PredictionRequestSerializer(read_only=True)
    
    class Meta:
        model = PredictionResult
        fields = ['id', 'request', 'prediction', 'confidence', 'created_at']
        read_only_fields = ['id', 'created_at']

# Nowy serializer dla Book
class BookSerializer(serializers.ModelSerializer):
    cover_image = serializers.ReadOnlyField()  # Używamy property z modelu
    categories_list = serializers.ReadOnlyField()  # Używamy property z modelu
    
    class Meta:
        model = Book
        fields = [
            'id', 'isbn', 'title', 'author', 'publisher', 'publication_year',
            'image_url_s', 'image_url_m', 'image_url_l', 'cover_image',
            'description', 'categories', 'categories_list', 'page_count',
            'language', 'average_rating', 'ratings_count', 'google_books_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

# Lekki serializer dla list książek (bez opisu)
class BookListSerializer(serializers.ModelSerializer):
    cover_image = serializers.ReadOnlyField()
    categories_list = serializers.ReadOnlyField()
    
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'cover_image', 
            'categories', 'categories_list', 'average_rating'
        ]