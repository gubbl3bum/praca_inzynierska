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

# Zaktualizowany serializer dla Book z Open Library
class BookSerializer(serializers.ModelSerializer):
    cover_image = serializers.ReadOnlyField()
    categories_list = serializers.ReadOnlyField()
    
    # Dodatkowe pola z Open Library
    open_library_cover_small = serializers.ReadOnlyField()
    open_library_cover_medium = serializers.ReadOnlyField()
    open_library_cover_large = serializers.ReadOnlyField()
    open_library_url = serializers.ReadOnlyField()
    
    # Metody dla różnych rozmiarów okładek
    best_cover_small = serializers.SerializerMethodField()
    best_cover_medium = serializers.SerializerMethodField()
    best_cover_large = serializers.SerializerMethodField()
    
    class Meta:
        model = Book
        fields = [
            'id', 'isbn', 'title', 'author', 'publisher', 'publication_year',
            'image_url_s', 'image_url_m', 'image_url_l', 
            'cover_image', 'best_cover_small', 'best_cover_medium', 'best_cover_large',
            'description', 'categories', 'categories_list', 'page_count',
            'language', 'average_rating', 'ratings_count', 
            'open_library_id', 'open_library_cover_small', 'open_library_cover_medium', 
            'open_library_cover_large', 'open_library_url',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_best_cover_small(self, obj):
        return obj.get_best_cover_url('S')
    
    def get_best_cover_medium(self, obj):
        return obj.get_best_cover_url('M')
    
    def get_best_cover_large(self, obj):
        return obj.get_best_cover_url('L')

# Lekki serializer dla list książek (bez opisu) - zaktualizowany dla Open Library
class BookListSerializer(serializers.ModelSerializer):
    cover_image = serializers.ReadOnlyField()
    categories_list = serializers.ReadOnlyField()
    best_cover_medium = serializers.SerializerMethodField()
    open_library_url = serializers.ReadOnlyField()
    
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'isbn',
            'cover_image', 'best_cover_medium',
            'categories', 'categories_list', 
            'average_rating', 'ratings_count',
            'open_library_url'
        ]
    
    def get_best_cover_medium(self, obj):
        return obj.get_best_cover_url('M')

# Nowy serializer specjalnie dla Open Library danych
class OpenLibraryBookSerializer(serializers.ModelSerializer):
    """Serializer skupiony na danych z Open Library"""
    open_library_covers = serializers.SerializerMethodField()
    open_library_url = serializers.ReadOnlyField()
    
    class Meta:
        model = Book
        fields = [
            'id', 'isbn', 'title', 'author',
            'open_library_id', 'open_library_url',
            'open_library_covers', 'categories_list'
        ]
    
    def get_open_library_covers(self, obj):
        """Zwraca wszystkie dostępne rozmiary okładek z Open Library"""
        return {
            'small': obj.open_library_cover_small,
            'medium': obj.open_library_cover_medium,
            'large': obj.open_library_cover_large
        }