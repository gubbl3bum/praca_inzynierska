from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Book, Author, Category, User, BookReview, BookSimilarity
from .services.similarity_service import BookSimilarityService

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

@api_view(['GET'])
def book_recommendations(request, book_id):
    """API endpoint dla rekomendacji książek"""
    try:
        book = Book.objects.get(id=book_id)
        
        # Parametry
        limit = min(int(request.GET.get('limit', 10)), 50)  # Max 50
        min_similarity = float(request.GET.get('min_similarity', 0.1))
        include_details = request.GET.get('details', 'false').lower() == 'true'
        
        # Użyj serwisu do znalezienia podobnych książek
        service = BookSimilarityService()
        similar_books = service.get_similar_books(
            book, 
            limit=limit, 
            min_similarity=min_similarity
        )
        
        # Przygotuj dane odpowiedzi
        recommendations = []
        for similarity_data in similar_books:
            similar_book = similarity_data['book']
            
            book_data = {
                'id': similar_book.id,
                'title': similar_book.title,
                'authors': similar_book.author_names,
                'price': str(similar_book.price) if similar_book.price else None,
                'publish_year': similar_book.publish_year,
                'average_rating': float(similar_book.average_rating) if similar_book.average_rating else 0,
                'ratings_count': similar_book.ratings_count,
                'description': (similar_book.description[:200] + '...') if similar_book.description and len(similar_book.description) > 200 else similar_book.description,
                'cover_image_url': similar_book.cover_image_url,
                'categories': [cat.name for cat in similar_book.categories.all()],
                'similarity_score': round(similarity_data['similarity'], 4),
            }
            
            # Dodaj szczegóły podobieństwa jeśli wymagane
            if include_details and 'details' in similarity_data:
                book_data['similarity_details'] = {
                    'category_similarity': round(similarity_data['details']['category'], 4),
                    'keyword_similarity': round(similarity_data['details']['keyword'], 4),
                    'author_similarity': round(similarity_data['details']['author'], 4),
                    'description_similarity': round(similarity_data['details']['description'], 4),
                    'reason': generate_similarity_reason(similarity_data)
                }
            
            recommendations.append(book_data)
        
        return Response({
            'status': 'success',
            'book': {
                'id': book.id,
                'title': book.title,
                'authors': book.author_names
            },
            'recommendations': recommendations,
            'count': len(recommendations),
            'parameters': {
                'limit': limit,
                'min_similarity': min_similarity,
                'include_details': include_details
            }
        })
        
    except Book.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Book not found'
        }, status=404)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=500)

def generate_similarity_reason(similarity_data):
    """Generuj tekstowe uzasadnienie podobieństwa"""
    details = similarity_data.get('details', {})
    reasons = []
    
    if details.get('category', 0) > 0.5:
        reasons.append("similar categories")
    if details.get('keyword', 0) > 0.3:
        reasons.append("matching keywords")
    if details.get('author', 0) > 0.8:
        reasons.append("same author")
    if details.get('description', 0) > 0.2:
        reasons.append("similar themes")
    
    if not reasons:
        return "general similarity"
    
    return ", ".join(reasons)

@api_view(['GET'])
def similarity_stats(request):
    """Statystyki podobieństw w systemie"""
    try:
        from django.db.models import Avg, Max, Min, Count
        
        stats = {
            'total_similarities': BookSimilarity.objects.count(),
            'total_books': Book.objects.count(),
            'avg_similarity': BookSimilarity.objects.aggregate(
                avg=Avg('cosine_similarity')
            )['avg'] or 0,
            'max_similarity': BookSimilarity.objects.aggregate(
                max=Max('cosine_similarity')
            )['max'] or 0,
            'min_similarity': BookSimilarity.objects.aggregate(
                min=Min('cosine_similarity')
            )['min'] or 0,
        }
        
        # Dodaj coverage percentage
        total_books = stats['total_books']
        if total_books > 1:
            max_possible_similarities = total_books * (total_books - 1) / 2
            stats['coverage_percentage'] = (stats['total_similarities'] / max_possible_similarities) * 100
        else:
            stats['coverage_percentage'] = 0
        
        # Top books by similarity count
        top_books = Book.objects.annotate(
            similarity_count=Count('similarities_as_book1') + Count('similarities_as_book2')
        ).order_by('-similarity_count')[:10]
        
        stats['top_similar_books'] = [
            {
                'id': book.id,
                'title': book.title,
                'authors': book.author_names,
                'similarity_count': book.similarity_count
            }
            for book in top_books
        ]
        
        return Response({
            'status': 'success',
            'stats': stats
        })
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=500)

@api_view(['POST'])
def recalculate_similarities(request, book_id=None):
    """Force recalculation of similarities"""
    try:
        service = get_similarity_service()  # Użyj singleton
        
        if book_id:
            # Recalculate for specific book
            book = Book.objects.get(id=book_id)
            count = service.calculate_similarities_for_book(book)
            
            return Response({
                'status': 'success',
                'message': f'Recalculated similarities for {book.title}',
                'similarities_created': count
            })
        else:
            # Recalculate for all books (dangerous!)
            limit = int(request.data.get('limit', 10))  # Safety limit
            books = Book.objects.all()[:limit]
            
            total_count = 0
            for book in books:
                count = service.calculate_similarities_for_book(book)
                total_count += count
            
            return Response({
                'status': 'success',
                'message': f'Recalculated similarities for {len(books)} books',
                'total_similarities_created': total_count
            })
            
    except Book.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Book not found'
        }, status=404)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=500)