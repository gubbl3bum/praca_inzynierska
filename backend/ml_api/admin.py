from django.contrib import admin
from .models import (
    Book, Author, Publisher, Category, BookAuthor, BookCategory,
    User, UserPreferences, BookReview, BookList, BookListItem,
    ReadingProgress
)

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'first_name', 'last_name', 'created_at')
    search_fields = ('first_name', 'last_name')
    list_filter = ('created_at',)
    ordering = ('last_name', 'first_name')

@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)
    ordering = ('name',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)
    ordering = ('name',)

class BookAuthorInline(admin.TabularInline):
    model = BookAuthor
    extra = 1

class BookCategoryInline(admin.TabularInline):
    model = BookCategory
    extra = 1

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author_names', 'publisher', 'price', 'publish_year', 'average_rating', 'ratings_count')
    search_fields = ('title', 'description')
    list_filter = ('publish_year', 'publisher', 'categories', 'created_at')
    filter_horizontal = []
    inlines = [BookAuthorInline, BookCategoryInline]
    ordering = ('-created_at',)
    
    def author_names(self, obj):
        return obj.author_names
    author_names.short_description = 'Authors'
    
    def average_rating(self, obj):
        return obj.average_rating
    average_rating.short_description = 'Avg Rating'
    
    def ratings_count(self, obj):
        return obj.ratings_count
    ratings_count.short_description = 'Reviews'

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_preferred_categories_count', 'get_preferred_authors_count', 'created_at')
    search_fields = ('user__username', 'user__email')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    
    def get_preferred_categories_count(self, obj):
        return len(obj.preferred_categories) if obj.preferred_categories else 0
    get_preferred_categories_count.short_description = 'Categories Count'
    
    def get_preferred_authors_count(self, obj):
        return len(obj.preferred_authors) if obj.preferred_authors else 0
    get_preferred_authors_count.short_description = 'Authors Count'

@admin.register(BookReview)
class BookReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'rating', 'created_at')
    search_fields = ('user__username', 'book__title', 'review_text')
    list_filter = ('rating', 'created_at')
    ordering = ('-created_at',)

# Inline relationships
@admin.register(BookAuthor)
class BookAuthorAdmin(admin.ModelAdmin):
    list_display = ('book', 'author', 'created_at')
    search_fields = ('book__title', 'author__first_name', 'author__last_name')
    list_filter = ('created_at',)

@admin.register(BookCategory)
class BookCategoryAdmin(admin.ModelAdmin):
    list_display = ('book', 'category', 'created_at')
    search_fields = ('book__title', 'category__name')
    list_filter = ('created_at',)

@admin.register(BookList)
class BookListAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'list_type', 'is_public', 'is_default', 'book_count', 'created_at')
    list_filter = ('list_type', 'is_public', 'is_default', 'created_at')
    search_fields = ('name', 'user__username', 'description')
    readonly_fields = ('created_at', 'updated_at', 'book_count')
    
    def book_count(self, obj):
        return obj.items.count()
    book_count.short_description = 'Books'

@admin.register(BookListItem)
class BookListItemAdmin(admin.ModelAdmin):
    list_display = ('book', 'book_list', 'priority', 'added_at')
    list_filter = ('added_at', 'book_list__list_type')
    search_fields = ('book__title', 'book_list__name', 'notes')
    readonly_fields = ('added_at', 'updated_at')

@admin.register(ReadingProgress)
class ReadingProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'status', 'progress_percentage', 'started_at', 'finished_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'book__title')
    readonly_fields = ('created_at', 'updated_at')