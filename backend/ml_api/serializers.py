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
            """Zwraca najlepszą okładkę małą bez wywoływania nieistniejącej metody"""
            return (getattr(obj, 'open_library_cover_small', None) or 
                    getattr(obj, 'image_url_s', None) or 
                    None)

        def get_best_cover_medium(self, obj):
            """Zwraca najlepszą okładkę średnią bez wywoływania nieistniejącej metody"""
            return (getattr(obj, 'open_library_cover_medium', None) or 
                    getattr(obj, 'image_url_m', None) or 
                    getattr(obj, 'cover_url', None) or 
                    None)

        def get_best_cover_large(self, obj):
            """Zwraca najlepszą okładkę dużą bez wywoływania nieistniejącej metody"""
            return (getattr(obj, 'open_library_cover_large', None) or 
                    getattr(obj, 'image_url_l', None) or 
                    None)

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
        """Zwraca najlepszą okładkę średnią bez wywoływania nieistniejącej metody"""
        return (getattr(obj, 'open_library_cover_medium', None) or 
                getattr(obj, 'image_url_m', None) or 
                getattr(obj, 'cover_url', None) or 
                None)

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