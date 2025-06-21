from django.contrib import admin
from .models import (
    PredictionRequest, PredictionResult, Book, Author, Publisher, Category,
    User, Rating, Review, ReadingList, Recommendation
)

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name', 'book_count', 'nationality', 'birth_year', 'created_at']
    list_filter = ['nationality', 'birth_year', 'created_at']
    search_fields = ['name', 'biography']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at', 'book_count']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'biography')
        }),
        ('Personal Details', {
            'fields': ('birth_year', 'death_year', 'nationality', 'website')
        }),
        ('Metadata', {
            'fields': ('book_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def book_count(self, obj):
        return obj.book_count
    book_count.short_description = 'Books Count'

@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ['name', 'book_count', 'country', 'founded_year', 'created_at']
    list_filter = ['country', 'founded_year', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    readonly_fields = ['created_at', 'updated_at', 'book_count']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description')
        }),
        ('Company Details', {
            'fields': ('founded_year', 'country', 'website')
        }),
        ('Metadata', {
            'fields': ('book_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def book_count(self, obj):
        return obj.book_count
    book_count.short_description = 'Books Count'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'book_count', 'created_at']
    list_filter = ['parent', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    readonly_fields = ['book_count']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'parent')
        }),
        ('Statistics', {
            'fields': ('book_count',),
            'classes': ('collapse',)
        })
    )
    
    def book_count(self, obj):
        return obj.book_count
    book_count.short_description = 'Books Count'

class AuthorInline(admin.TabularInline):
    model = Book.authors.through
    extra = 1
    verbose_name = "Author"
    verbose_name_plural = "Authors"

class CategoryInline(admin.TabularInline):
    model = Book.categories.through
    extra = 1
    verbose_name = "Category"
    verbose_name_plural = "Categories"

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'get_authors', 'publisher', 'publication_year', 
        'average_rating', 'ratings_count', 'get_categories', 'created_at'
    ]
    list_filter = [
        'publication_year', 'language', 'publisher', 
        'authors', 'categories', 'created_at'
    ]
    search_fields = ['title', 'isbn', 'description', 'authors__name', 'publisher__name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    filter_horizontal = ['authors', 'categories']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'isbn', 'authors', 'publisher', 'publication_year')
        }),
        ('Cover Images', {
            'fields': ('image_url_s', 'image_url_m', 'image_url_l'),
            'description': 'URLs to book cover images'
        }),
        ('Open Library Integration', {
            'fields': ('open_library_id',),
            'description': 'Open Library data'
        }),
        ('Content', {
            'fields': ('description', 'categories', 'page_count', 'language')
        }),
        ('Ratings', {
            'fields': ('average_rating', 'ratings_count')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_authors(self, obj):
        """Zwraca listę autorów"""
        return ", ".join([author.name for author in obj.authors.all()[:3]])
    get_authors.short_description = 'Authors'
    
    def get_categories(self, obj):
        """Zwraca listę kategorii"""
        return ", ".join([cat.name for cat in obj.categories.all()[:3]])
    get_categories.short_description = 'Categories'

@admin.register(PredictionRequest)
class PredictionRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'feature1', 'feature2', 'feature3', 'feature4', 'created_at']
    list_filter = ['created_at']
    ordering = ['-created_at']

@admin.register(PredictionResult)
class PredictionResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'prediction', 'confidence', 'created_at']
    list_filter = ['created_at']
    ordering = ['-created_at']

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'user_type', 'email', 'age', 'country', 'created_at']
    list_filter = ['user_type', 'country', 'age', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'last_login']
    
    fieldsets = (
        ('User Type', {
            'fields': ('user_type', 'original_user_id')
        }),
        ('Account Information', {
            'fields': ('username', 'email', 'password_hash')
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'age')
        }),
        ('Location', {
            'fields': ('city', 'state', 'country')
        }),
        ('Preferences & Metadata', {
            'fields': ('preferences', 'created_at', 'last_login'),
            'classes': ('collapse',)
        })
    )

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'book', 'rating', 'source_type', 'rating_scale', 'created_at']
    list_filter = ['rating', 'source_type', 'rating_scale', 'created_at']
    search_fields = ['user__username', 'book__title']
    ordering = ['-created_at']
    readonly_fields = ['created_at']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'book', 'title', 'helpful_votes', 'created_at']
    list_filter = ['helpful_votes', 'created_at']
    search_fields = ['user__username', 'book__title', 'title', 'content']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ReadingList)
class ReadingListAdmin(admin.ModelAdmin):
    list_display = ['user', 'book', 'list_type', 'added_at']
    list_filter = ['list_type', 'added_at']
    search_fields = ['user__username', 'book__title']
    ordering = ['-added_at']
    readonly_fields = ['added_at']

@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ['user', 'book', 'recommendation_type', 'score', 'created_at']
    list_filter = ['recommendation_type', 'score', 'created_at']
    search_fields = ['user__username', 'book__title']
    ordering = ['-score', '-created_at']
    readonly_fields = ['created_at']