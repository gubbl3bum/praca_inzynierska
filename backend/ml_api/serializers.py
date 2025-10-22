from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import (
    Book, Author, Publisher, Category, BookAuthor, BookCategory,
    User, UserPreferences, BookReview, RefreshToken,
    BookList, BookListItem, ReadingProgress
)

class AuthorSerializer(serializers.ModelSerializer):
    book_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Author
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 
            'book_count', 'created_at'
        ]
        read_only_fields = ['id', 'full_name', 'created_at']
    
    def get_book_count(self, obj):
        return obj.books.count()

class AuthorSimpleSerializer(serializers.ModelSerializer):
    """Simple serializer for author lists"""
    class Meta:
        model = Author
        fields = ['id', 'full_name', 'first_name', 'last_name']

class PublisherSerializer(serializers.ModelSerializer):
    book_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Publisher
        fields = ['id', 'name', 'book_count', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_book_count(self, obj):
        return obj.books.count()

class PublisherSimpleSerializer(serializers.ModelSerializer):
    """Simple serializer for publisher references"""
    class Meta:
        model = Publisher
        fields = ['id', 'name']

class CategorySerializer(serializers.ModelSerializer):
    book_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'book_count', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_book_count(self, obj):
        return obj.books.count()

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
    category_names = serializers.SerializerMethodField()
    
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
            'isbn', 'cover_image_url',
            'best_cover_small', 'best_cover_medium', 'best_cover_large',
            'average_rating', 'ratings_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_category_names(self, obj):
        return [cat.name for cat in obj.categories.all()]
    
    def get_author(self, obj):
        """Legacy compatibility: return first author as string"""
        authors = obj.authors.all()
        if authors:
            return authors[0].full_name
        return 'Unknown Author'
    
    def get_best_cover_small(self, obj):
        """Return best available small cover"""
        return obj.cover_image_url
    
    def get_best_cover_medium(self, obj):
        """Return best available medium cover"""
        return obj.cover_image_url
    
    def get_best_cover_large(self, obj):
        """Return best available large cover"""
        return obj.cover_image_url

class BookListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for book lists"""
    authors = AuthorSimpleSerializer(many=True, read_only=True)
    categories = CategorySimpleSerializer(many=True, read_only=True)
    publisher = PublisherSimpleSerializer(read_only=True)
    
    # Legacy compatibility
    author = serializers.SerializerMethodField()
    author_names = serializers.ReadOnlyField()
    category_names = serializers.SerializerMethodField()
    best_cover_medium = serializers.SerializerMethodField()
    
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'authors', 'author', 'author_names',
            'categories', 'category_names', 'publisher',
            'isbn', 'cover_image_url', 'best_cover_medium',
            'average_rating', 'ratings_count',
            'publish_year'
        ]
    
    def get_category_names(self, obj):
        return [cat.name for cat in obj.categories.all()]
    
    def get_author(self, obj):
        """Legacy compatibility: return first author as string"""
        authors = obj.authors.all()
        if authors:
            return authors[0].full_name
        return 'Unknown Author'
    
    def get_best_cover_medium(self, obj):
        """Return best available medium cover"""
        return obj.cover_image_url

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
            'isbn', 'cover_image_url'
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

# =============================================================================
# AUTH SERIALIZERS 
# =============================================================================

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for registering new users"""
    
    password = serializers.CharField(
        write_only=True, 
        min_length=8,
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 
            'password', 'password_confirm'
        ]
    
    def validate(self, attrs):
        """Validate that passwords match"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords must match")
        return attrs
    
    def validate_email(self, value):
        """Check if email is unique"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists")
        return value
    
    def validate_username(self, value):
        """Check if username is unique"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken")
        return value
    
    def create(self, validated_data):
        """Create a new user"""
        validated_data.pop('password_confirm')  # Remove password confirmation
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user

class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """Check login credentials"""
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            # Check if user exists and password is correct
            try:
                user = User.objects.get(email=email)
                if not user.check_password(password):
                    raise serializers.ValidationError("Invalid login credentials")
                if not user.is_active:
                    raise serializers.ValidationError("Account has been deactivated")
                attrs['user'] = user
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid login credentials")
        else:
            raise serializers.ValidationError("Email and password are required")
        
        return attrs

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'full_name', 'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'username', 'date_joined', 'last_login']

class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password"""
    
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(
        write_only=True, 
        min_length=8,
        validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate_current_password(self, value):
        """Check if current password is correct"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect")
        return value
    
    def validate(self, attrs):
        """Check if new passwords match"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords must match")
        return attrs

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
    user = UserProfileSerializer(read_only=True)
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

# =============================================================================
# STATISTICS SERIALIZERS
# =============================================================================

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
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=2)
    
    most_active_users = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )
    recent_reviews = BookReviewSimpleSerializer(many=True, required=False)

# =============================================================================
# SEARCH SERIALIZERS
# =============================================================================

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
        authors = obj.authors.all()
        if authors:
            return authors[0].full_name
        return 'Unknown Author'
    
    def get_best_cover_medium(self, obj):
        """Return best available medium cover"""
        return obj.cover_image_url

class AuthorSearchSerializer(serializers.ModelSerializer):
    """Author search results serializer"""
    book_count = serializers.SerializerMethodField()
    recent_books = serializers.SerializerMethodField()
    
    class Meta:
        model = Author
        fields = ['id', 'full_name', 'book_count', 'recent_books']
    
    def get_book_count(self, obj):
        return obj.books.count()
    
    def get_recent_books(self, obj):
        """Get recent books by this author"""
        recent_books = obj.books.order_by('-created_at')[:3]
        return BookListSerializer(recent_books, many=True).data

# =============================================================================
# RECOMMENDATION SERIALIZERS
# =============================================================================

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
        authors = obj.authors.all()
        if authors:
            return authors[0].full_name
        return 'Unknown Author'
    
    def get_best_cover_medium(self, obj):
        """Return best available medium cover"""
        return obj.cover_image_url
    
# =============================================================================
# BOOK LIST SERIALIZERS
# =============================================================================

class BookListItemSerializer(serializers.ModelSerializer):
    """Book list item with book details"""
    book = BookListSerializer(read_only=True)
    book_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = BookListItem
        fields = [
            'id', 'book', 'book_id', 'notes', 'priority',
            'added_at', 'updated_at'
        ]
        read_only_fields = ['id', 'added_at', 'updated_at']

class BookListDetailSerializer(serializers.ModelSerializer):
    """Detailed book list with items"""
    items = BookListItemSerializer(many=True, read_only=True)
    book_count = serializers.ReadOnlyField()
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = BookList
        fields = [
            'id', 'name', 'list_type', 'description', 'is_public', 
            'is_default', 'book_count', 'user_username',
            'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_default', 'created_at', 'updated_at']

class BookListSimpleSerializer(serializers.ModelSerializer):
    """Simple book list without items"""
    book_count = serializers.ReadOnlyField()
    
    class Meta:
        model = BookList
        fields = [
            'id', 'name', 'list_type', 'description', 'is_public',
            'is_default', 'book_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_default', 'created_at', 'updated_at']

class BookListCreateUpdateSerializer(serializers.ModelSerializer):
    """Create/update book list"""
    
    class Meta:
        model = BookList
        fields = ['name', 'list_type', 'description', 'is_public']
    
    def validate_list_type(self, value):
        """Prevent creating custom lists with reserved types"""
        if value in ['favorites', 'to_read', 'reading', 'read']:
            # Check if this is an update of existing default list
            if not self.instance or not self.instance.is_default:
                raise serializers.ValidationError(
                    "Cannot create custom list with reserved type. Use 'custom' instead."
                )
        return value

class ReadingProgressSerializer(serializers.ModelSerializer):
    """Reading progress serializer"""
    book = BookListSerializer(read_only=True)
    book_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = ReadingProgress
        fields = [
            'id', 'book', 'book_id', 'status', 'progress_percentage',
            'current_page', 'total_pages', 'started_at', 'finished_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_progress_percentage(self, value):
        """Validate progress percentage"""
        if value < 0 or value > 100:
            raise serializers.ValidationError("Progress must be between 0 and 100")
        return value

class AddToListSerializer(serializers.Serializer):
    """Add book to list"""
    book_id = serializers.IntegerField()
    notes = serializers.CharField(required=False, allow_blank=True)
    priority = serializers.IntegerField(required=False, default=0)
    
    def validate_book_id(self, value):
        """Check if book exists"""
        if not Book.objects.filter(id=value).exists():
            raise serializers.ValidationError("Book not found")
        return value