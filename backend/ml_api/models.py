from django.db import models
from decimal import Decimal

class Author(models.Model):
    first_name = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'authors'
        unique_together = ['first_name', 'last_name']
        indexes = [
            models.Index(fields=['last_name']),
        ]
    
    @property
    def full_name(self):
        if self.first_name:
            return f"{self.first_name} {self.last_name}"
        return self.last_name
    
    def __str__(self):
        return self.full_name

class Publisher(models.Model):
    name = models.CharField(max_length=200, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'publishers'
        indexes = [
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'categories'
        indexes = [
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True, null=True)
    keywords = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    publish_month = models.CharField(max_length=20, blank=True, null=True)
    publish_year = models.IntegerField(blank=True, null=True)
    isbn = models.CharField(max_length=20, blank=True, null=True, db_index=True)
    cover_image_url = models.URLField(blank=True, null=True)
    
    # Relacje many-to-many
    authors = models.ManyToManyField('Author', through='BookAuthor', related_name='books')
    categories = models.ManyToManyField('Category', through='BookCategory', related_name='books')
    publisher = models.ForeignKey('Publisher', on_delete=models.SET_NULL, null=True, blank=True, related_name='books')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'books'
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['publish_year']),
            models.Index(fields=['isbn']),
        ]
    
    def __str__(self):
        return self.title
    
    @property
    def average_rating(self):
        """Wylicz średnią ocenę na bieżąco"""
        from django.db.models import Avg
        result = self.reviews.aggregate(avg_rating=Avg('rating'))
        return round(result['avg_rating'] or 0, 2)
    
    @property
    def ratings_count(self):
        """Wylicz liczbę ocen na bieżąco"""
        return self.reviews.count()
    
    @property
    def author_names(self):
        """Zwróć nazwy autorów jako string"""
        return ", ".join([author.full_name for author in self.authors.all()])

class BookAuthor(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'book_authors'
        unique_together = ['book', 'author']

class BookCategory(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'book_categories'
        unique_together = ['book', 'category']

class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=128)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return self.username

class UserPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    preferred_categories = models.JSONField(default=list)  # Lista ID kategorii
    preferred_authors = models.JSONField(default=list)     # Lista ID autorów
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_preferences'

class BookReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField()  # 1-10
    review_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'book_reviews'
        unique_together = ['user', 'book']
        indexes = [
            models.Index(fields=['rating']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.book.title} ({self.rating}/10)"