from django.db import models
from django.contrib.postgres.fields import ArrayField

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

# Naprawiony model Book - zgodny ze schematem bazy
class Book(models.Model):
    isbn = models.CharField(max_length=20, unique=True, null=True, blank=True)
    title = models.CharField(max_length=500)
    author = models.CharField(max_length=300, null=True, blank=True)
    publisher = models.CharField(max_length=200, null=True, blank=True)
    publication_year = models.IntegerField(null=True, blank=True)
    
    # Obrazki w różnych rozmiarach
    image_url_s = models.URLField(max_length=500, null=True, blank=True)
    image_url_m = models.URLField(max_length=500, null=True, blank=True)
    image_url_l = models.URLField(max_length=500, null=True, blank=True)
    
    # Dodatkowe informacje
    description = models.TextField(null=True, blank=True)
    # Używamy ArrayField dla PostgreSQL
    categories = ArrayField(models.CharField(max_length=100), null=True, blank=True)
    page_count = models.IntegerField(null=True, blank=True)
    language = models.CharField(max_length=10, default='en', null=True, blank=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    ratings_count = models.IntegerField(default=0, null=True, blank=True)
    google_books_id = models.CharField(max_length=50, null=True, blank=True)
    
    # Metadane
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'books'  # Używamy tej samej nazwy tabeli co w schemacie SQL
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} by {self.author}"
    
    @property
    def cover_image(self):
        """Zwraca najlepszy dostępny obrazek okładki"""
        return self.image_url_m or self.image_url_l or self.image_url_s
    
    @property
    def categories_list(self):
        """Zwraca kategorie jako listę"""
        return self.categories if self.categories else []