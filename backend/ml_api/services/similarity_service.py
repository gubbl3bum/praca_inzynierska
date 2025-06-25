import os
import sys
import math
import json
import nltk
from collections import defaultdict, Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from django.db import transaction, models
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta

# Dodaj path do Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from ml_api.models import Book, BookSimilarity, BookVector, Category, Author

class BookSimilarityService:
    """
    Serwis do wyliczania i zarządzania podobieństwami książek
    """
    
    def __init__(self):
        self.min_similarity_threshold = 0.05  # Minimum similarity to store
        self.tfidf_vectorizer = None
        self.category_weights = {
            'category': 0.4,      # Kategorie są ważne
            'keyword': 0.3,       # Słowa kluczowe
            'author': 0.2,        # Autor
            'description': 0.1    # Opis (mniej ważny bo może być bardzo różny)
        }
        
        # NLTK - inicjalizuj raz przy tworzeniu serwisu
        self._nltk_initialized = False
        self._stop_words = None
        
        # POPRAWKA: Wywołaj inicjalizację NLTK od razu
        self._ensure_nltk_data()
    
    def _ensure_nltk_data(self):
        """Upewnij się że NLTK data jest pobrana - TYLKO RAZ"""
        if self._nltk_initialized:
            return
            
        try:
            # Test czy data już jest
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
            nltk.data.find('corpora/wordnet')
            print("✅ NLTK data already available")
        except LookupError:
            print("📥 Downloading NLTK data (one-time setup)...")
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True) 
            nltk.download('wordnet', quiet=True)
            nltk.download('omw-1.4', quiet=True)
            print("✅ NLTK data downloaded successfully")
        
        # Cache stop words
        from nltk.corpus import stopwords
        self._stop_words = set(stopwords.words('english'))
        
        # Dodaj custom stopwords dla książek
        custom_stopwords = {
            'book', 'novel', 'story', 'author', 'writer', 'tale', 'narrative',
            'chapter', 'page', 'read', 'reading', 'written', 'write', 'tells',
            'follows', 'chronicles', 'explores', 'examines', 'describes'
        }
        self._stop_words.update(custom_stopwords)
        
        self._nltk_initialized = True
    
    def ensure_nltk_data(self):
        """Backward compatibility - deprecated"""
        if not self._nltk_initialized:
            self._ensure_nltk_data()
    
    def extract_features_from_book(self, book):
        """
        Wyciągnij cechy z książki do wektoryzacji
        """
        features = {
            'categories': [],
            'keywords': [],
            'authors': [],
            'description_words': []
        }
        
        # Kategorie
        categories = book.categories.all()
        features['categories'] = [cat.name.lower() for cat in categories]
        
        # Autorzy
        authors = book.authors.all()
        features['authors'] = [f"{author.first_name} {author.last_name}".strip().lower() for author in authors]
        
        # Słowa kluczowe
        if book.keywords:
            keywords = [kw.strip().lower() for kw in book.keywords.split(',') if kw.strip()]
            features['keywords'] = keywords
        
        # Słowa z opisu
        if book.description:
            # NLTK już zainicjalizowane, używaj cache
            from nltk.tokenize import word_tokenize
            
            # Zabezpieczenie - upewnij się że stop_words są zainicjalizowane
            if self._stop_words is None:
                self._ensure_nltk_data()
            
            words = word_tokenize(book.description.lower())
            # Filtruj słowa używając cached stop_words
            filtered_words = [
                word for word in words 
                if word.isalpha() and len(word) > 2 and word not in self._stop_words
            ]
            features['description_words'] = filtered_words[:50]  # Max 50 słów
        
        return features
    
    def create_book_vector(self, book):
        """
        Stwórz wektor dla książki
        """
        features = self.extract_features_from_book(book)
        
        # Wektory dla każdego typu cechy
        vectors = {
            'category_vector': {},
            'keyword_vector': {},
            'author_vector': {},
            'description_vector': {}
        }
        
        # Wektor kategorii (binary)
        for category in features['categories']:
            vectors['category_vector'][category] = 1.0
        
        # Wektor autorów (binary)
        for author in features['authors']:
            vectors['author_vector'][author] = 1.0
        
        # Wektor słów kluczowych (binary)
        for keyword in features['keywords']:
            vectors['keyword_vector'][keyword] = 1.0
        
        # Wektor opisu (TF-IDF like)
        if features['description_words']:
            word_counts = Counter(features['description_words'])
            total_words = len(features['description_words'])
            
            for word, count in word_counts.items():
                # Prosta TF (term frequency)
                tf = count / total_words
                vectors['description_vector'][word] = tf
        
        # Kombinowany wektor
        combined = {}
        
        # Dodaj wszystkie cechy z wagami
        for category, weight in vectors['category_vector'].items():
            combined[f"cat_{category}"] = weight * self.category_weights['category']
        
        for keyword, weight in vectors['keyword_vector'].items():
            combined[f"kw_{keyword}"] = weight * self.category_weights['keyword']
        
        for author, weight in vectors['author_vector'].items():
            combined[f"auth_{author}"] = weight * self.category_weights['author']
        
        for word, weight in vectors['description_vector'].items():
            combined[f"desc_{word}"] = weight * self.category_weights['description']
        
        vectors['combined_vector'] = combined
        
        return vectors
    
    def cosine_similarity_vectors(self, vector1, vector2):
        """
        Wylicz podobieństwo kosinusowe między dwoma wektorami (dict)
        """
        # Znajdź wszystkie unikalne klucze
        all_keys = set(vector1.keys()) | set(vector2.keys())
        
        if not all_keys:
            return 0.0
        
        # Konwertuj na numpy arrays
        v1 = np.array([vector1.get(key, 0.0) for key in all_keys])
        v2 = np.array([vector2.get(key, 0.0) for key in all_keys])
        
        # Wylicz podobieństwo kosinusowe
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return np.dot(v1, v2) / (norm1 * norm2)
    
    def calculate_detailed_similarity(self, book1_vector, book2_vector):
        """
        Wylicz szczegółowe podobieństwa dla różnych aspektów
        """
        similarities = {}
        
        # Podobieństwo kategorii
        similarities['category_similarity'] = self.cosine_similarity_vectors(
            book1_vector['category_vector'], 
            book2_vector['category_vector']
        )
        
        # Podobieństwo słów kluczowych
        similarities['keyword_similarity'] = self.cosine_similarity_vectors(
            book1_vector['keyword_vector'], 
            book2_vector['keyword_vector']
        )
        
        # Podobieństwo autorów
        similarities['author_similarity'] = self.cosine_similarity_vectors(
            book1_vector['author_vector'], 
            book2_vector['author_vector']
        )
        
        # Podobieństwo opisu
        similarities['description_similarity'] = self.cosine_similarity_vectors(
            book1_vector['description_vector'], 
            book2_vector['description_vector']
        )
        
        return similarities
    
    def calculate_similarity_between_books(self, book1, book2):
        """
        Wylicz podobieństwo między dwoma książkami
        """
        # Stwórz wektory
        vector1 = self.create_book_vector(book1)
        vector2 = self.create_book_vector(book2)
        
        # Ogólne podobieństwo kosinusowe
        cosine_sim = self.cosine_similarity_vectors(
            vector1['combined_vector'], 
            vector2['combined_vector']
        )
        
        # Szczegółowe podobieństwa
        detailed_similarities = self.calculate_detailed_similarity(vector1, vector2)
        
        return {
            'cosine_similarity': cosine_sim,
            **detailed_similarities
        }
    
    def update_book_vector(self, book):
        """
        Zaktualizuj wektor dla książki
        """
        vector_data = self.create_book_vector(book)
        
        book_vector, created = BookVector.objects.get_or_create(
            book=book,
            defaults=vector_data
        )
        
        if not created:
            # Aktualizuj istniejący wektor
            for key, value in vector_data.items():
                setattr(book_vector, key, value)
            book_vector.save()
        
        return book_vector
    
    def calculate_similarities_for_book(self, target_book, batch_size=100):
        """
        Wylicz podobieństwa dla jednej książki względem wszystkich innych
        """
        print(f"📊 Calculating similarities for: {target_book.title}")
        
        # Zaktualizuj wektor docelowej książki
        self.update_book_vector(target_book)
        
        # Pobierz wszystkie inne książki batch'ami
        other_books = Book.objects.exclude(id=target_book.id)
        total_books = other_books.count()
        processed = 0
        similarities_created = 0
        
        print(f"📚 Processing {total_books} other books...")
        
        with transaction.atomic():
            # Usuń stare podobieństwa dla tej książki
            BookSimilarity.objects.filter(
                Q(book1=target_book) | Q(book2=target_book)
            ).delete()
            
            for i in range(0, total_books, batch_size):
                batch = other_books[i:i + batch_size]
                
                for other_book in batch:
                    # Zaktualizuj wektor drugiej książki
                    self.update_book_vector(other_book)
                    
                    # Wylicz podobieństwo
                    similarity_data = self.calculate_similarity_between_books(
                        target_book, other_book
                    )
                    
                    # Zapisz tylko jeśli podobieństwo jest wystarczające
                    if similarity_data['cosine_similarity'] >= self.min_similarity_threshold:
                        # Upewnij się że book1.id < book2.id (dla unikatowości)
                        book1, book2 = (target_book, other_book) if target_book.id < other_book.id else (other_book, target_book)
                        
                        BookSimilarity.objects.create(
                            book1=book1,
                            book2=book2,
                            **similarity_data
                        )
                        similarities_created += 1
                    
                    processed += 1
                
                if (i + batch_size) % (batch_size * 5) == 0:  # Progress every 5 batches
                    print(f"   Processed {min(i + batch_size, total_books)}/{total_books} books...")
        
        print(f"✅ Created {similarities_created} similarity records for {target_book.title}")
        return similarities_created
    
    def calculate_all_similarities(self, batch_size=50):
        """
        Wylicz podobieństwa dla wszystkich książek
        """
        print("🚀 CALCULATING ALL BOOK SIMILARITIES")
        print("=" * 50)
        
        books = Book.objects.all()
        total_books = books.count()
        
        print(f"📚 Processing {total_books} books...")
        
        processed = 0
        total_similarities = 0
        
        for book in books:
            try:
                similarities_count = self.calculate_similarities_for_book(book, batch_size)
                total_similarities += similarities_count
                processed += 1
                
                if processed % 10 == 0:
                    print(f"📈 Progress: {processed}/{total_books} books processed")
                
            except Exception as e:
                print(f"❌ Error processing {book.title}: {e}")
                continue
        
        print("=" * 50)
        print(f"✅ SIMILARITY CALCULATION COMPLETED!")
        print(f"📊 Books processed: {processed}/{total_books}")
        print(f"🔗 Total similarities created: {total_similarities}")
        
        return total_similarities
    
    def get_similar_books(self, book, limit=10, min_similarity=0.1):
        """
        Znajdź podobne książki (z cache lub wylicz dynamicznie)
        """
        # Sprawdź czy są prekalkulowane podobieństwa
        cached_similarities = BookSimilarity.get_similar_books(
            book, limit=limit, min_similarity=min_similarity
        )
        
        if cached_similarities:
            return cached_similarities
        
        # Jeśli brak cache, wylicz dynamicznie dla kilku najbardziej popularnych książek
        print(f"⚡ Dynamic calculation for {book.title}")
        
        # Weź np. 100 najpopularniejszych książek do porównania
        popular_books = Book.objects.exclude(id=book.id).annotate(
            review_count=Count('reviews')
        ).order_by('-review_count')[:100]
        
        dynamic_similarities = []
        
        for other_book in popular_books:
            similarity_data = self.calculate_similarity_between_books(book, other_book)
            
            if similarity_data['cosine_similarity'] >= min_similarity:
                dynamic_similarities.append({
                    'book': other_book,
                    'similarity': similarity_data['cosine_similarity'],
                    'details': {
                        'category': similarity_data['category_similarity'],
                        'keyword': similarity_data['keyword_similarity'],
                        'author': similarity_data['author_similarity'],
                        'description': similarity_data['description_similarity']
                    }
                })
        
        # Sortuj według podobieństwa
        dynamic_similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        return dynamic_similarities[:limit]

# Singleton instance - utwórz raz i używaj wszędzie
_service_instance = None

def get_similarity_service():
    """Pobierz singleton instance serwisu"""
    global _service_instance
    if _service_instance is None:
        print("🚀 Initializing BookSimilarityService singleton...")
        _service_instance = BookSimilarityService()
        print("✅ BookSimilarityService ready!")
    return _service_instance

# Funkcje pomocnicze do uruchamiania

def calculate_similarities_for_single_book(book_id):
    """Wylicz podobieństwa dla pojedynczej książki"""
    try:
        book = Book.objects.get(id=book_id)
        service = get_similarity_service()  # Użyj singleton
        return service.calculate_similarities_for_book(book)
    except Book.DoesNotExist:
        print(f"❌ Book with ID {book_id} not found")
        return 0

def calculate_all_book_similarities():
    """Wylicz podobieństwa dla wszystkich książek"""
    service = get_similarity_service()  # Użyj singleton
    return service.calculate_all_similarities()

def get_book_recommendations(book_id, limit=10):
    """Pobierz rekomendacje dla książki"""
    try:
        book = Book.objects.get(id=book_id)
        service = get_similarity_service()  # Użyj singleton
        return service.get_similar_books(book, limit=limit)
    except Book.DoesNotExist:
        print(f"❌ Book with ID {book_id} not found")
        return []

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Book Similarity Calculator')
    parser.add_argument('--all', action='store_true', help='Calculate similarities for all books')
    parser.add_argument('--book', type=int, help='Calculate similarities for specific book ID')
    parser.add_argument('--recommend', type=int, help='Get recommendations for book ID')
    parser.add_argument('--limit', type=int, default=10, help='Limit for recommendations')
    
    args = parser.parse_args()
    
    if args.all:
        calculate_all_book_similarities()
    elif args.book:
        calculate_similarities_for_single_book(args.book)
    elif args.recommend:
        recommendations = get_book_recommendations(args.recommend, args.limit)
        print(f"\n📚 Recommendations for book ID {args.recommend}:")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec['book'].title} (similarity: {rec['similarity']:.3f})")
    else:
        print("Use --all, --book ID, or --recommend ID")