from django.db import models
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
import uuid
from datetime import timedelta
import json

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
    
class UserManager(BaseUserManager):
    """Manager dla custom User modelu"""
    
    def create_user(self, email, username, password=None, **extra_fields):
        """Tworzenie zwykłego użytkownika"""
        if not email:
            raise ValueError('Email jest wymagany')
        if not username:
            raise ValueError('Username jest wymagany')
        
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=username,
            **extra_fields
        )
        user.set_password(password)  # Automatyczne hashowanie
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, username, password=None, **extra_fields):
        """Tworzenie superusera (admina)"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        return self.create_user(email, username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    
    # Pola wymagane przez Django auth
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    # Timestamps
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Manager i konfiguracja
    objects = UserManager()
    
    USERNAME_FIELD = 'email'  # Logowanie przez email
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return self.username
    
    @property
    def full_name(self):
        """Zwraca pełne imię i nazwisko"""
        return f"{self.first_name} {self.last_name}".strip() or self.username

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
    
class BookSimilarity(models.Model):
    """
    Prekalkulowane podobieństwa między książkami
    """
    book1 = models.ForeignKey(
        'Book', 
        on_delete=models.CASCADE, 
        related_name='similarities_as_book1'
    )
    book2 = models.ForeignKey(
        'Book', 
        on_delete=models.CASCADE, 
        related_name='similarities_as_book2'
    )
    
    # Podobieństwo kosinusowe (0.0 - 1.0)
    cosine_similarity = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    
    # Szczegółowe podobieństwa dla różnych aspektów
    category_similarity = models.FloatField(default=0.0)
    keyword_similarity = models.FloatField(default=0.0)
    author_similarity = models.FloatField(default=0.0)
    description_similarity = models.FloatField(default=0.0)
    
    # Metadane obliczenia
    calculated_at = models.DateTimeField(auto_now=True)
    version = models.IntegerField(default=1)  # Wersja algorytmu
    
    class Meta:
        db_table = 'book_similarities'
        unique_together = ['book1', 'book2']
        indexes = [
            models.Index(fields=['book1', 'cosine_similarity']),
            models.Index(fields=['book2', 'cosine_similarity']),
            models.Index(fields=['cosine_similarity']),
        ]
    
    def __str__(self):
        return f"{self.book1.title} ↔ {self.book2.title}: {self.cosine_similarity:.3f}"
    
    @classmethod
    def get_similar_books(cls, book, limit=10, min_similarity=0.1):
        """
        Znajdź podobne książki dla danej książki
        """
        # Zapytanie uwzględniające obie strony relacji
        similar = cls.objects.filter(
            models.Q(book1=book) | models.Q(book2=book),
            cosine_similarity__gte=min_similarity
        ).select_related('book1', 'book2').order_by('-cosine_similarity')[:limit]
        
        # Zwróć książki z ich podobieństwami
        results = []
        for sim in similar:
            other_book = sim.book2 if sim.book1 == book else sim.book1
            results.append({
                'book': other_book,
                'similarity': sim.cosine_similarity,
                'details': {
                    'category': sim.category_similarity,
                    'keyword': sim.keyword_similarity,
                    'author': sim.author_similarity,
                    'description': sim.description_similarity
                }
            })
        
        return results

class BookVector(models.Model):
    """
    Wektor cech książki dla szybkich obliczeń podobieństwa
    """
    book = models.OneToOneField(
        'Book', 
        on_delete=models.CASCADE, 
        related_name='vector'
    )
    
    # Wektory jako JSON
    category_vector = models.JSONField(default=dict)  # {category_id: weight}
    keyword_vector = models.JSONField(default=dict)   # {keyword: tfidf_score}
    author_vector = models.JSONField(default=dict)    # {author_id: weight}
    description_vector = models.JSONField(default=dict)  # {word: tfidf_score}
    
    # Kombinowany wektor (znormalizowany)
    combined_vector = models.JSONField(default=dict)
    
    # Metadane
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    version = models.IntegerField(default=1)
    
    class Meta:
        db_table = 'book_vectors'
        indexes = [
            models.Index(fields=['updated_at']),
        ]
    
    def __str__(self):
        return f"Vector for {self.book.title}"
    
class RefreshToken(models.Model):
    """Model do przechowywania refresh tokenów"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='refresh_tokens')
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    # Dodatkowe informacje dla bezpieczeństwa
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        db_table = 'refresh_tokens'
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['user', 'is_active']),
        ]
    
    def __str__(self):
        return f"RefreshToken for {self.user.username}"
    
    def is_expired(self):
        """Sprawdza czy token wygasł"""
        return timezone.now() > self.expires_at
    
    def revoke(self):
        """Unieważnia token"""
        self.is_active = False
        self.save()
    
    @classmethod
    def create_for_user(cls, user, ip_address=None, user_agent=None):
        """Tworzy nowy refresh token dla użytkownika"""
        # Usuń stare, nieaktywne tokeny
        cls.objects.filter(
            user=user, 
            is_active=False
        ).delete()
        
        # Ograniczenie maksymalnej liczby aktywnych tokenów (np. 5 urządzeń)
        active_tokens = cls.objects.filter(user=user, is_active=True).order_by('-created_at')
        if active_tokens.count() >= 5:
            # Usuń najstarsze tokeny
            for token in active_tokens[4:]:
                token.revoke()
        
        # Utwórz nowy token ważny przez 30 dni
        expires_at = timezone.now() + timedelta(days=30)
        
        return cls.objects.create(
            user=user,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent
        )