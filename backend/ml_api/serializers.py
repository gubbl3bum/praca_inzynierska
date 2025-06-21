from rest_framework import serializers
from .models import (
    PredictionRequest, PredictionResult, Book, Author, Publisher, Category
)

class AuthorSerializer(serializers.ModelSerializer):
    book_count = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()
    
    class Meta:
        model = Author
        fields = [
            'id', 'name', 'biography', 'birth_year', 'death_year', 
            'nationality', 'website', 'book_count', 'average_rating',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class AuthorSimpleSerializer(serializers.ModelSerializer):
    """Uproszczony serializer dla autorów (do użycia w listach książek)"""
    class Meta:
        model = Author
        fields = ['id', 'name']

class PublisherSerializer(serializers.ModelSerializer):
    book_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Publisher
        fields = [
            'id', 'name', 'description', 'founded_year', 'country', 
            'website', 'book_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class PublisherSimpleSerializer(serializers.ModelSerializer):
    """Uproszczony serializer dla wydawców"""
    class Meta:
        model = Publisher
        fields = ['id', 'name', 'country']

class CategorySerializer(serializers.ModelSerializer):
    book_count = serializers.ReadOnlyField()
    subcategories = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'description', 'parent', 'subcategories',
            'book_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class CategorySimpleSerializer(serializers.ModelSerializer):
    """Uproszczony serializer dla kategorii"""
    class Meta:
        model = Category
        fields = ['id', 'name']

class BookSerializer(serializers.ModelSerializer):
    """Pełny serializer dla książek z wszystkimi relacjami"""
    authors = AuthorSimpleSerializer(many=True, read_only=True)
    publisher = PublisherSimpleSerializer(read_only=True)
    categories = CategorySimpleSerializer(many=True, read_only=True)
    
    # Compatibility fields (dla zachowania kompatybilności z frontendem)
    author = serializers.SerializerMethodField()
    author_names = serializers.ReadOnlyField()
    category_names = serializers.ReadOnlyField()
    
    # Cover images
    cover_image = serializers.ReadOnlyField()
    best_cover_small = serializers.SerializerMethodField()
    best_cover_medium = serializers.SerializerMethodField()
    best_cover_large = serializers.SerializerMethodField()
    
    # Open Library
    open_library_cover_small = serializers.ReadOnlyField()
    open_library_cover_medium = serializers.ReadOnlyField()
    open_library_cover_large = serializers.ReadOnlyField()
    open_library_url = serializers.ReadOnlyField()
    
    class Meta:
        model = Book
        fields = [
            'id', 'isbn', 'title', 'authors', 'author', 'author_names',
            'publisher', 'publication_year', 'image_url_s', 'image_url_m', 'image_url_l',
            'cover_image', 'best_cover_small', 'best_cover_medium', 'best_cover_large',
            'description', 'categories', 'category_names', 'page_count',
            'language', 'average_rating', 'ratings_count',
            'open_library_id', 'open_library_cover_small', 'open_library_cover_medium',
            'open_library_cover_large', 'open_library_url',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_author(self, obj):
        """Compatibility: zwraca pierwszego autora jako string"""
        primary_author = obj.primary_author
        return primary_author.name if primary_author else None
    
    def get_best_cover_small(self, obj):
        """Zwraca najlepszą okładkę małą"""
        return (obj.open_library_cover_small or 
                obj.image_url_s or None)

    def get_best_cover_medium(self, obj):
        """Zwraca najlepszą okładkę średnią"""
        return (obj.open_library_cover_medium or 
                obj.image_url_m or 
                obj.cover_image or None)

    def get_best_cover_large(self, obj):
        """Zwraca najlepszą okładkę dużą"""
        return (obj.open_library_cover_large or 
                obj.image_url_l or None)

class BookListSerializer(serializers.ModelSerializer):
    """Lekki serializer dla list książek"""
    authors = AuthorSimpleSerializer(many=True, read_only=True)
    publisher = PublisherSimpleSerializer(read_only=True)
    categories = CategorySimpleSerializer(many=True, read_only=True)
    
    # Compatibility fields
    author = serializers.SerializerMethodField()
    author_names = serializers.ReadOnlyField()
    category_names = serializers.ReadOnlyField()
    
    # Cover
    cover_image = serializers.ReadOnlyField()
    best_cover_medium = serializers.SerializerMethodField()
    open_library_url = serializers.ReadOnlyField()
    
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'authors', 'author', 'author_names', 'isbn',
            'publisher', 'cover_image', 'best_cover_medium',
            'categories', 'category_names', 'average_rating', 'ratings_count',
            'publication_year', 'open_library_url'
        ]
    
    def get_author(self, obj):
        """Compatibility: zwraca pierwszego autora jako string"""
        primary_author = obj.primary_author
        return primary_author.name if primary_author else None
    
    def get_best_cover_medium(self, obj):
        """Zwraca najlepszą okładkę średnią"""
        return (obj.open_library_cover_medium or 
                obj.image_url_m or 
                obj.cover_image or None)

class BookCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer do tworzenia/edycji książek"""
    author_ids = serializers.ListField(
        child=serializers.IntegerField(), 
        write_only=True, 
        required=False
    )
    category_ids = serializers.ListField(
        child=serializers.IntegerField(), 
        write_only=True, 
        required=False
    )
    publisher_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Book
        fields = [
            'id', 'isbn', 'title', 'author_ids', 'publisher_id', 'category_ids',
            'publication_year', 'image_url_s', 'image_url_m', 'image_url_l',
            'description', 'page_count', 'language', 'average_rating', 'ratings_count',
            'open_library_id'
        ]
        read_only_fields = ['id']
    
    def create(self, validated_data):
        author_ids = validated_data.pop('author_ids', [])
        category_ids = validated_data.pop('category_ids', [])
        publisher_id = validated_data.pop('publisher_id', None)
        
        # Utwórz książkę
        book = Book.objects.create(**validated_data)
        
        # Dodaj relacje
        if author_ids:
            book.authors.set(author_ids)
        if category_ids:
            book.categories.set(category_ids)
        if publisher_id:
            try:
                publisher = Publisher.objects.get(id=publisher_id)
                book.publisher = publisher
                book.save()
            except Publisher.DoesNotExist:
                pass
        
        return book
    
    def update(self, instance, validated_data):
        author_ids = validated_data.pop('author_ids', None)
        category_ids = validated_data.pop('category_ids', None)
        publisher_id = validated_data.pop('publisher_id', None)
        
        # Zaktualizuj podstawowe pola
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Zaktualizuj relacje
        if author_ids is not None:
            instance.authors.set(author_ids)
        if category_ids is not None:
            instance.categories.set(category_ids)
        if publisher_id is not None:
            try:
                publisher = Publisher.objects.get(id=publisher_id)
                instance.publisher = publisher
                instance.save()
            except Publisher.DoesNotExist:
                instance.publisher = None
                instance.save()
        
        return instance

class OpenLibraryBookSerializer(serializers.ModelSerializer):
    """Serializer skupiony na danych z Open Library"""
    authors = AuthorSimpleSerializer(many=True, read_only=True)
    open_library_covers = serializers.SerializerMethodField()
    open_library_url = serializers.ReadOnlyField()
    
    class Meta:
        model = Book
        fields = [
            'id', 'isbn', 'title', 'authors',
            'open_library_id', 'open_library_url',
            'open_library_covers', 'category_names'
        ]
    
    def get_open_library_covers(self, obj):
        """Zwraca wszystkie dostępne rozmiary okładek z Open Library"""
        return {
            'small': obj.open_library_cover_small,
            'medium': obj.open_library_cover_medium,
            'large': obj.open_library_cover_large
        }

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