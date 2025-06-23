from rest_framework import serializers
from .models import (
    Book, Author, Publisher, Category, BookReview, 
    UserBookList, UserBookListItem, User, UserPreferences,
    PredictionRequest, PredictionResult
)

class AuthorSerializer(serializers.ModelSerializer):
    book_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Author
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 
            'book_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'full_name', 'created_at', 'updated_at']

class AuthorSimpleSerializer(serializers.ModelSerializer):
    """Simple serializer for author lists"""
    class Meta:
        model = Author
        fields = ['id', 'full_name', 'first_name', 'last_name']

class PublisherSerializer(serializers.ModelSerializer):
    book_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Publisher
        fields = ['id', 'name', 'book_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class PublisherSimpleSerializer(serializers.ModelSerializer):
    """Simple serializer for publisher references"""
    class Meta:
        model = Publisher
        fields = ['id', 'name']

class CategorySerializer(serializers.ModelSerializer):
    book_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'book_count', 'created_at']
        read_only_fields = ['id', 'created_at']

class CategorySimpleSerializer(serializers.ModelSerializer):
    """Simple serializer for category lists"""
    class Meta:
        model = Category
        fields = ['id', 'name']

class BookSerializer(serializers.ModelSerializer):
    """Full book serializer with all relationships"""
    authors = AuthorSimpleSerializer(many=True, read_only=True)
    categories = CategorySimpleSerializer(many=True, read_only=True)
    publisher = PublisherSimpleSerializer(read_only=True)
    
    # Computed fields
    author_names = serializers.ReadOnlyField()
    category_names = serializers.ReadOnlyField()
    cover_image = serializers.ReadOnlyField()
    
    # Open Library integration
    open_library_cover_small = serializers.ReadOnlyField()
    open_library_cover_medium = serializers.ReadOnlyField()
    open_library_cover_large = serializers.ReadOnlyField()
    open_library_url = serializers.ReadOnlyField()
    
    # Legacy compatibility fields
    author = serializers.SerializerMethodField()
    best_cover_small = serializers.SerializerMethodField()
    best_cover_medium = serializers.SerializerMethodField()
    best_cover_large = serializers.SerializerMethodField()
    
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'description', 'keywords',
            'price', 'publish_month', 'publish_year',
            'authors', 'author', 'author_names',
            'categories', 'category_names', 
            'publisher',
            'isbn', 'open_library_id',
            'image_url_s', 'image_url_m', 'image_url_l',
            'cover_image', 'best_cover_small', 'best_cover_medium', 'best_cover_large',
            'open_library_cover_small', 'open_library_cover_medium', 'open_library_cover_large',
            'open_library_url',
            'average_rating', 'ratings_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_author(self, obj):
        """Legacy compatibility: return first author as string"""
        primary_author = obj.primary_author
        return primary_author.full_name if primary_author else None
    
    def get_best_cover_small(self, obj):
        """Return best available small cover"""
        return (obj.open_library_cover_small or 
                obj.image_url_s or None)
    
    def get_best_cover_medium(self, obj):
        """Return best available medium cover"""
        return (obj.open_library_cover_medium or 
                obj.image_url_m or 
                obj.cover_image or None)
    
    def get_best_cover_large(self, obj):
        """Return best available large cover"""
        return (obj.open_library_cover_large or 
                obj.image_url_l or None)

class BookListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for book lists"""
    authors = AuthorSimpleSerializer(many=True, read_only=True)
    categories = CategorySimpleSerializer(many=True, read_only=True)
    publisher = PublisherSimpleSerializer(read_only=True)
    
    # Legacy compatibility
    author = serializers.SerializerMethodField()
    author_names = serializers.ReadOnlyField()
    category_names = serializers.ReadOnlyField()
    cover_image = serializers.ReadOnlyField()
    best_cover_medium = serializers.SerializerMethodField()
    open_library_url = serializers.ReadOnlyField()
    
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'authors', 'author', 'author_names',
            'categories', 'category_names', 'publisher',
            'isbn', 'cover_image', 'best_cover_medium',
            'average_rating', 'ratings_count',
            'publish_year', 'open_library_url'
        ]
    
    def get_author(self, obj):
        """Legacy compatibility: return first author as string"""
        primary_author = obj.primary_author
        return primary_author.full_name if primary_author else None
    
    def get_best_cover_medium(self, obj):
        """Return best available medium cover"""
        return (obj.open_library_cover_medium or 
                obj.image_url_m or 
                obj.cover_image or None)

class BookCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating books"""
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
            'id', 'title', 'description', 'keywords',
            'price', 'publish_month', 'publish_year',
            'author_ids', 'category_ids', 'publisher_id',
            'isbn', 'open_library_id',
            'image_url_s', 'image_url_m', 'image_url_l'
        ]
        read_only_fields = ['id']
    
    def create(self, validated_data):
        author_ids = validated_data.pop('author_ids', [])
        category_ids = validated_data.pop('category_ids', [])
        publisher_id = validated_data.pop('publisher_id', None)
        
        # Create book
        book = Book.objects.create(**validated_data)
        
        # Add relationships
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
        
        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update relationships
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

class UserSerializer(serializers.ModelSerializer):
    """User serializer"""
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'full_name', 'created_at', 'last_login'
        ]
        read_only_fields = ['id', 'created_at']

class UserPreferencesSerializer(serializers.ModelSerializer):
    """User preferences serializer"""
    preferred_category_names = serializers.SerializerMethodField()
    preferred_author_names = serializers.SerializerMethodField()
    
    class Meta:
        model = UserPreferences
        fields = [
            'id', 'preferred_categories', 'preferred_authors',
            'preferred_category_names', 'preferred_author_names',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_preferred_category_names(self, obj):
        """Get names of preferred categories"""
        if obj.preferred_categories:
            categories = Category.objects.filter(id__in=obj.preferred_categories)
            return [cat.name for cat in categories]
        return []
    
    def get_preferred_author_names(self, obj):
        """Get names of preferred authors"""
        if obj.preferred_authors:
            authors = Author.objects.filter(id__in=obj.preferred_authors)
            return [author.full_name for author in authors]
        return []

class BookReviewSerializer(serializers.ModelSerializer):
    """Book review serializer"""
    user = UserSerializer(read_only=True)
    book = BookListSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    book_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = BookReview
        fields = [
            'id', 'user', 'book', 'user_id', 'book_id',
            'rating', 'review_text', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_rating(self, value):
        """Validate rating is between 1 and 10"""
        if not (1 <= value <= 10):
            raise serializers.ValidationError("Rating must be between 1 and 10")
        return value

class BookReviewSimpleSerializer(serializers.ModelSerializer):
    """Simple review serializer for lists"""
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = BookReview
        fields = [
            'id', 'user_name', 'rating', 'review_text', 'created_at'
        ]

class UserBookListSerializer(serializers.ModelSerializer):
    """User book list serializer"""
    user = UserSerializer(read_only=True)
    book_count = serializers.ReadOnlyField()
    books = serializers.SerializerMethodField()
    
    class Meta:
        model = UserBookList
        fields = [
            'id', 'user', 'name', 'description', 'is_favorites',
            'book_count', 'books', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_books(self, obj):
        """Get books in this list"""
        book_items = obj.items.select_related('book').all()[:10]  # Limit to 10 for performance
        books = [item.book for item in book_items]
        return BookListSerializer(books, many=True).data

class UserBookListSimpleSerializer(serializers.ModelSerializer):
    """Simple list serializer without books"""
    book_count = serializers.ReadOnlyField()
    
    class Meta:
        model = UserBookList
        fields = [
            'id', 'name', 'description', 'is_favorites',
            'book_count', 'created_at', 'updated_at'
        ]

class UserBookListItemSerializer(serializers.ModelSerializer):
    """Book list item serializer"""
    book = BookListSerializer(read_only=True)
    list_name = serializers.CharField(source='list.name', read_only=True)
    
    class Meta:
        model = UserBookListItem
        fields = ['id', 'book', 'list_name', 'added_at']

# Statistics serializers
class BookStatisticsSerializer(serializers.Serializer):
    """Book statistics serializer"""
    total_books = serializers.IntegerField()
    total_authors = serializers.IntegerField()
    total_publishers = serializers.IntegerField()
    total_categories = serializers.IntegerField()
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=2)
    total_reviews = serializers.IntegerField()
    
    top_authors = serializers.ListField(
        child=serializers.DictField(), 
        required=False
    )
    top_categories = serializers.ListField(
        child=serializers.DictField(), 
        required=False
    )
    recent_books = BookListSerializer(many=True, required=False)

class UserStatisticsSerializer(serializers.Serializer):
    """User statistics serializer"""
    total_users = serializers.IntegerField()
    total_reviews = serializers.IntegerField()
    total_lists = serializers.IntegerField()
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=2)
    
    most_active_users = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )
    recent_reviews = BookReviewSimpleSerializer(many=True, required=False)

# Search serializers
class BookSearchSerializer(serializers.ModelSerializer):
    """Book search results serializer"""
    authors = AuthorSimpleSerializer(many=True, read_only=True)
    categories = CategorySimpleSerializer(many=True, read_only=True)
    publisher = PublisherSimpleSerializer(read_only=True)
    
    # Legacy compatibility and computed fields
    author = serializers.SerializerMethodField()
    best_cover_medium = serializers.SerializerMethodField()
    
    # Highlighting fields for search results
    title_highlight = serializers.CharField(required=False)
    description_highlight = serializers.CharField(required=False)
    
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'title_highlight',
            'description', 'description_highlight',
            'authors', 'author', 'categories', 'publisher',
            'best_cover_medium', 'average_rating', 'ratings_count',
            'publish_year'
        ]
    
    def get_author(self, obj):
        """Return first author name"""
        primary_author = obj.primary_author
        return primary_author.full_name if primary_author else None
    
    def get_best_cover_medium(self, obj):
        """Return best available medium cover"""
        return (obj.open_library_cover_medium or 
                obj.image_url_m or 
                obj.cover_image or None)

class AuthorSearchSerializer(serializers.ModelSerializer):
    """Author search results serializer"""
    book_count = serializers.ReadOnlyField()
    recent_books = serializers.SerializerMethodField()
    
    class Meta:
        model = Author
        fields = ['id', 'full_name', 'book_count', 'recent_books']
    
    def get_recent_books(self, obj):
        """Get recent books by this author"""
        recent_books = obj.books.order_by('-created_at')[:3]
        return BookListSerializer(recent_books, many=True).data

# Legacy ML prediction serializers (preserved)
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

# Recommendation serializers
class BookRecommendationSerializer(serializers.ModelSerializer):
    """Book recommendation serializer"""
    authors = AuthorSimpleSerializer(many=True, read_only=True)
    categories = CategorySimpleSerializer(many=True, read_only=True)
    
    # Recommendation specific fields
    recommendation_score = serializers.DecimalField(max_digits=5, decimal_places=4, required=False)
    recommendation_reason = serializers.CharField(required=False)
    
    # Legacy compatibility
    author = serializers.SerializerMethodField()
    best_cover_medium = serializers.SerializerMethodField()
    
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'authors', 'author', 'categories',
            'best_cover_medium', 'average_rating', 'ratings_count',
            'recommendation_score', 'recommendation_reason'
        ]
    
    def get_author(self, obj):
        """Return first author name"""
        primary_author = obj.primary_author
        return primary_author.full_name if primary_author else None
    
    def get_best_cover_medium(self, obj):
        """Return best available medium cover"""
        return (obj.open_library_cover_medium or 
                obj.image_url_m or 
                obj.cover_image or None)