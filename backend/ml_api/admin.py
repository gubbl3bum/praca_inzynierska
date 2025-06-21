from django.contrib import admin
from .models import PredictionRequest, PredictionResult, Book

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

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'author', 'isbn', 'publication_year', 'average_rating', 'has_open_library_id']
    list_filter = ['publication_year', 'language', 'created_at']
    search_fields = ['title', 'author', 'isbn', 'open_library_id']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'author', 'isbn', 'publisher', 'publication_year')
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
    
    def has_open_library_id(self, obj):
        return bool(obj.open_library_id)
    has_open_library_id.boolean = True
    has_open_library_id.short_description = 'Has OL ID'