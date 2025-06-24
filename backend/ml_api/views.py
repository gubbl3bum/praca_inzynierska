from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Book, Author, Category, User, BookReview

@api_view(['GET'])
def featured_books(request):
    """Polecane książki"""
    try:
        books = Book.objects.all()[:12]
        book_data = []
        
        for book in books:
            book_data.append({
                'id': book.id,
                'title': book.title,
                'authors': book.author_names,
                'price': str(book.price) if book.price else None,
                'publish_year': book.publish_year,
                'average_rating': book.average_rating,
                'ratings_count': book.ratings_count,
                'description': book.description[:200] + '...' if book.description and len(book.description) > 200 else book.description,
            })
        
        return Response({
            'status': 'success',
            'count': len(book_data),
            'books': book_data
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=500)

@api_view(['GET'])
def book_list(request):
    """Lista książek"""
    try:
        books = Book.objects.all()[:20]
        book_data = []
        
        for book in books:
            book_data.append({
                'id': book.id,
                'title': book.title,
                'authors': book.author_names,
                'price': str(book.price) if book.price else None,
                'publish_year': book.publish_year,
                'average_rating': book.average_rating,
                'ratings_count': book.ratings_count,
            })
        
        return Response({
            'status': 'success',
            'count': len(book_data),
            'books': book_data
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=500)

@api_view(['GET'])
def top_books(request):
    """Top książki"""
    try:
        books = Book.objects.all()[:200]
        book_data = []
        
        for book in books:
            book_data.append({
                'id': book.id,
                'title': book.title,
                'authors': book.author_names,
                'price': str(book.price) if book.price else None,
                'publish_year': book.publish_year,
                'average_rating': book.average_rating,
                'ratings_count': book.ratings_count,
            })
        
        return Response({
            'status': 'success',
            'count': len(book_data),
            'books': book_data
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=500)

@api_view(['GET'])
def stats(request):
    """Statystyki systemu"""
    try:
        return Response({
            'status': 'success',
            'stats': {
                'books': Book.objects.count(),
                'authors': Author.objects.count(),
                'categories': Category.objects.count(),
                'users': User.objects.count(),
                'reviews': BookReview.objects.count()
            }
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=500)