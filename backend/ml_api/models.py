from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import AbstractUser
from decimal import Decimal

class Author(models.Model):
    """Model dla autorów książek"""
    name = models.CharField(max_length=300, unique=True)
    biography = models.TextField(null=True, blank=True)
    birth_year = models.IntegerField(null=True, blank=True)
    death_year = models.IntegerField(null=True, blank=True)
    nationality = models.CharField(max_length=100, null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    
    # Metadane
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'authors'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return self.name
    
    @property
    def book_count(self):
        """Liczba książek autora"""
        return self.books.count()
    
    @property
    def average_rating(self):
        """Średnia ocena książek autora"""
        from django.db.models import Avg
        result = self.books.aggregate(avg_rating=Avg('average_rating'))
        return result['avg_rating'] if result['avg_rating'] else 0

class Publisher(models.Model):
    """Model dla wydawców"""
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(null=True, blank=True)
    founded_year = models.IntegerField(null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    
    # Metadane
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'publishers'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return self.name
    
    @property
    def book_count(self):
        """Liczba książek wydawcy"""
        return self.books.count()

class Category(models.Model):
    """Model dla kategorii książek"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    
    # Metadane
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'categories'
        ordering = ['name']
        verbose_name_plural = 'categories'
    
    def __str__(self):
        return self.name
    
    @property
    def book_count(self):
        """Liczba książek w kategorii"""
        return self.books.count()

class Book(models.Model):
    # Podstawowe informacje
    isbn = models.CharField(max_length=20, unique=True, null=True, blank=True)
    title = models.CharField(max_length=500)
    
    # ZNORMALIZOWANE RELACJE
    authors = models.ManyToManyField(Author, related_name='books', blank=True)
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True, blank=True, related_name='books')
    categories = models.ManyToManyField(Category, related_name='books', blank=True)
    
    # Pozostałe informacje
    publication_year = models.IntegerField(null=True, blank=True)
    
    # Obrazki w różnych rozmiarach
    image_url_s = models.URLField(max_length=500, null=True, blank=True)
    image_url_m = models.URLField(max_length=500, null=True, blank=True)
    image_url_l = models.URLField(max_length=500, null=True, blank=True)
    
    # Dodatkowe informacje
    description = models.TextField(null=True, blank=True)
    page_count = models.IntegerField(null=True, blank=True)
    language = models.CharField(max_length=10, default='en', null=True, blank=True)
    
    # Oceny (denormalizowane dla wydajności)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    ratings_count = models.IntegerField(default=0, null=True, blank=True)
    
    # Open Library integration
    open_library_id = models.CharField(max_length=100, null=True, blank=True)
    
    # Metadane
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'books'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['isbn']),
            models.Index(fields=['title']),
            models.Index(fields=['publication_year']),
            models.Index(fields=['average_rating']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        authors_str = ", ".join([author.name for author in self.authors.all()[:2]])
        if self.authors.count() > 2:
            authors_str += f" (+{self.authors.count() - 2} more)"
        return f"{self.title} by {authors_str}"
    
    @property
    def primary_author(self):
        """Zwraca pierwszego autora"""
        return self.authors.first()
    
    @property
    def author_names(self):
        """Zwraca listę imion autorów"""
        return [author.name for author in self.authors.all()]
    
    @property
    def category_names(self):
        """Zwraca listę nazw kategorii"""
        return [category.name for category in self.categories.all()]
    
    @property
    def cover_image(self):
        """Zwraca najlepszy dostępny obrazek okładki"""
        return self.image_url_m or self.image_url_l or self.image_url_s
    
    @property
    def open_library_cover_small(self):
        """Generuje URL okładki małej z Open Library na podstawie ISBN"""
        if self.isbn:
            clean_isbn = self.isbn.replace('-', '').replace(' ', '')
            return f"https://covers.openlibrary.org/b/isbn/{clean_isbn}-S.jpg"
        return None
    
    @property
    def open_library_cover_medium(self):
        """Generuje URL okładki średniej z Open Library na podstawie ISBN"""
        if self.isbn:
            clean_isbn = self.isbn.replace('-', '').replace(' ', '')
            return f"https://covers.openlibrary.org/b/isbn/{clean_isbn}-M.jpg"
        return None
    
    @property
    def open_library_cover_large(self):
        """Generuje URL okładki dużej z Open Library na podstawie ISBN"""
        if self.isbn:
            clean_isbn = self.isbn.replace('-', '').replace(' ', '')
            return f"https://covers.openlibrary.org/b/isbn/{clean_isbn}-L.jpg"
        return None
    
    @property
    def open_library_url(self):
        """Zwraca URL do strony książki w Open Library"""
        if self.open_library_id:
            return f"https://openlibrary.org{self.open_library_id}"
        elif self.isbn:
            clean_isbn = self.isbn.replace('-', '').replace(' ', '')
            return f"https://openlibrary.org/isbn/{clean_isbn}"
        return None

class PredictionRequest(models.Model):
    feature1 = models.FloatField()
    feature2 = models.FloatField()
    feature3 = models.FloatField()
    feature4 = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Prediction Request {self.id} ({self.created_at})"

class PredictionResult(models.Model):
    request = models.OneToOneField(PredictionRequest, on_delete=models.CASCADE, related_name='result')
    prediction = models.FloatField()
    confidence = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Prediction Result {self.id} ({self.created_at})"

class User(models.Model):
    USER_TYPES = [
        ('dataset', 'Dataset User'),
        ('app', 'App User'),
    ]
    
    # Dla użytkowników z datasetu
    original_user_id = models.IntegerField(unique=True, null=True, blank=True)
    
    # Dla użytkowników aplikacji
    username = models.CharField(max_length=50, unique=True, null=True, blank=True)
    email = models.EmailField(max_length=100, unique=True, null=True, blank=True)
    password_hash = models.CharField(max_length=255, null=True, blank=True)
    
    # Wspólne dane
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    
    # Typ użytkownika
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    
    # Metadane
    preferences = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
    
    def __str__(self):
        if self.user_type == 'dataset':
            return f"Dataset User {self.original_user_id}"
        else:
            return f"App User {self.username}"
    
    @property
    def display_name(self):
        """Zwraca nazwę do wyświetlenia"""
        if self.user_type == 'app':
            if self.first_name and self.last_name:
                return f"{self.first_name} {self.last_name}"
            elif self.username:
                return self.username
        return f"User {self.original_user_id or self.id}"

class Rating(models.Model):
    RATING_SCALES = [
        ('0-10', '0-10 Scale'),
        ('1-5', '1-5 Scale'),
    ]
    
    SOURCE_TYPES = [
        ('dataset', 'Dataset Rating'),
        ('app', 'App Rating'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='ratings')
    
    # Znormalizowana ocena (zawsze 1-5)
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    
    # Oryginalna ocena (dla historii)
    original_rating = models.IntegerField(null=True, blank=True)
    rating_scale = models.CharField(max_length=10, choices=RATING_SCALES, default='1-5')
    
    # Typ źródła oceny
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ratings'
        unique_together = ['user', 'book']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user} rated {self.book} - {self.rating}/5"
    
    def save(self, *args, **kwargs):
        """Auto-normalize rating when saving"""
        if self.original_rating and self.rating_scale == '0-10':
            # Konwertuj z 0-10 na 1-5
            if self.original_rating == 0:
                self.rating = Decimal('1.0')
            else:
                self.rating = round(Decimal(self.original_rating) / 2 + Decimal('0.5'), 1)
        elif self.original_rating and self.rating_scale == '1-5':
            self.rating = Decimal(str(self.original_rating))
        
        super().save(*args, **kwargs)

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', 
                            limit_choices_to={'user_type': 'app'})
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    title = models.CharField(max_length=200, null=True, blank=True)
    content = models.TextField()
    helpful_votes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reviews'
        unique_together = ['user', 'book']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review by {self.user.display_name} for {self.book.title}"

class ReadingList(models.Model):
    LIST_TYPES = [
        ('want_to_read', 'Want to Read'),
        ('currently_reading', 'Currently Reading'),
        ('read', 'Read'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reading_lists',
                            limit_choices_to={'user_type': 'app'})
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reading_lists')
    list_type = models.CharField(max_length=20, choices=LIST_TYPES)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'reading_lists'
        unique_together = ['user', 'book', 'list_type']
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.user.display_name} - {self.book.title} ({self.get_list_type_display()})"

class Recommendation(models.Model):
    RECOMMENDATION_TYPES = [
        ('collaborative', 'Collaborative Filtering'),
        ('content_based', 'Content-Based'),
        ('hybrid', 'Hybrid'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='recommendations')
    recommendation_type = models.CharField(max_length=20, choices=RECOMMENDATION_TYPES)
    score = models.DecimalField(max_digits=5, decimal_places=4)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'recommendations'
        ordering = ['-score', '-created_at']
    
    def __str__(self):
        return f"Recommendation for {self.user.display_name}: {self.book.title} (Score: {self.score})"