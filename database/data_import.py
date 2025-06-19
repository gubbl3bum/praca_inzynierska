import pandas as pd
import requests
import time
import psycopg2
import json
from typing import Dict, Optional, List
import logging
import os
from datetime import datetime  

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BookCrossingImporter:
    def __init__(self, db_config: Dict, google_api_key: Optional[str] = None):
        self.db_config = db_config
        self.google_api_key = google_api_key
        self.conn = None
        self.google_books_base_url = "https://www.googleapis.com/books/v1/volumes"
        
    def connect_db(self):
        """Połączenie z bazą danych"""
        self.conn = psycopg2.connect(**self.db_config)
        
    def load_book_crossing_data(self):
        """Załaduj dane Book-Crossing"""
        # Pobierz dane (trzeba je wcześniej pobrać z UCI)
        books = pd.read_csv('/data/Books.csv', encoding='latin-1', sep=';', on_bad_lines='skip')
        users = pd.read_csv('/data/Users.csv', encoding='latin-1', sep=';', on_bad_lines='skip', dtype={'User-ID': str})
        ratings = pd.read_csv('/data/Ratings.csv', encoding='latin-1', sep=';', on_bad_lines='skip')
        
        return books, users, ratings
    
    def get_google_books_info(self, isbn: str, title: str, author: str) -> Dict:
        """Pobierz informacje z Google Books API"""
        try:
            # Próbuj najpierw przez ISBN
            if isbn and isbn != '0':
                url = f"{self.google_books_base_url}?q=isbn:{isbn}"
                if self.google_api_key:
                    url += f"&key={self.google_api_key}"
                
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('totalItems', 0) > 0:
                        return self.extract_book_info(data['items'][0])
            
            # Jeśli ISBN nie zadziałał, spróbuj przez tytuł i autora
            query = f'intitle:"{title}"'
            if author:
                query += f'+inauthor:"{author}"'
            
            url = f"{self.google_books_base_url}?q={query}"
            if self.google_api_key:
                url += f"&key={self.google_api_key}"
            
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data.get('totalItems', 0) > 0:
                    return self.extract_book_info(data['items'][0])
                    
        except Exception as e:
            logger.error(f"Error fetching Google Books data: {e}")
        
        return {}
    
    def extract_book_info(self, book_item: Dict) -> Dict:
        """Wyciągnij informacje z odpowiedzi Google Books"""
        volume_info = book_item.get('volumeInfo', {})
        
        return {
            'google_books_id': book_item.get('id'),
            'description': volume_info.get('description'),
            'categories': volume_info.get('categories', []),
            'page_count': volume_info.get('pageCount'),
            'language': volume_info.get('language'),
            'average_rating': volume_info.get('averageRating'),
            'ratings_count': volume_info.get('ratingsCount')
        }
    
    def import_books(self, books_df: pd.DataFrame, limit=1000):
        """Import książek do bazy z wzbogaceniem o Google Books"""
        cursor = self.conn.cursor()
        count = 0
        current_time = datetime.now()  
        for idx, book in books_df.iterrows():
            # Pomiń książki bez tytułu
            if not book.get('Title') or pd.isna(book.get('Title')):
                logger.warning(f"Pominięto książkę bez tytułu (ISBN: {book.get('ISBN')})")
                continue

            if count >= limit:
                break

            # Pobierz dane z Google Books
            google_info = self.get_google_books_info(
                book.get('ISBN', ''), 
                book.get('Book-Title', ''), 
                book.get('Book-Author', '')
            )
            
            # Przygotuj dane do wstawienia
            insert_data = {
                'isbn': book.get('ISBN'),
                'title': book.get('Title'),
                'author': book.get('Author'),
                'publisher': book.get('Publisher'),
                'publication_year': book.get('Year-Of-Publication') if pd.notna(book.get('Year-Of-Publication')) else None,
                'image_url_s': book.get('Image-URL-S'),
                'image_url_m': book.get('Image-URL-M'),
                'image_url_l': book.get('Image-URL-L'),
                'description': google_info.get('description'),
                'categories': google_info.get('categories'),
                'page_count': google_info.get('page_count'),
                'language': google_info.get('language'),
                'average_rating': google_info.get('average_rating'),
                'ratings_count': google_info.get('ratings_count'),
                'google_books_id': google_info.get('google_books_id'),
                'created_at': current_time,  
                'updated_at': current_time   
            }
            
            # SQL INSERT
            sql = """
                INSERT INTO books (isbn, title, author, publisher, publication_year, 
                                image_url_s, image_url_m, image_url_l, description, 
                                categories, page_count, language, average_rating, 
                                ratings_count, google_books_id, created_at, updated_at)
                VALUES (%(isbn)s, %(title)s, %(author)s, %(publisher)s, %(publication_year)s,
                        %(image_url_s)s, %(image_url_m)s, %(image_url_l)s, %(description)s,
                        %(categories)s, %(page_count)s, %(language)s, %(average_rating)s,
                        %(ratings_count)s, %(google_books_id)s, %(created_at)s, %(updated_at)s)
                ON CONFLICT (isbn) DO NOTHING
                """
            
            cursor.execute(sql, insert_data)
            count += 1
            # Rate limiting dla Google API
            if idx % 10 == 0:
                time.sleep(1)
                logger.info(f"Processed {idx} books")
        self.conn.commit()
        cursor.close()

    def import_users(self, users_df: pd.DataFrame, limit=500):
        """Import użytkowników z datasetu"""
        cursor = self.conn.cursor()
        count = 0
        for _, user in users_df.iterrows():
            if count >= limit:
                break
            location_parts = str(user.get('Location', '')).split(',')
            city = location_parts[0].strip() if len(location_parts) > 0 else None
            state = location_parts[1].strip() if len(location_parts) > 1 else None
            country = location_parts[2].strip() if len(location_parts) > 2 else None
            
            sql = """
            INSERT INTO dataset_users (original_user_id, age, city, state, country)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (original_user_id) DO NOTHING
            """
            
            cursor.execute(sql, (
                user.get('User-ID'),
                user.get('Age') if pd.notna(user.get('Age')) else None,
                city, state, country
            ))
            count += 1
        
        self.conn.commit()
        cursor.close()
    
    def import_ratings(self, ratings_df: pd.DataFrame, limit=50000):
        """Import ocen z datasetu"""
        cursor = self.conn.cursor()
        count = 0
        # Najpierw pobierz mapowanie ID
        cursor.execute("SELECT original_user_id, id FROM dataset_users")
        user_mapping = dict(cursor.fetchall())
        
        cursor.execute("SELECT isbn, id FROM books WHERE isbn IS NOT NULL")
        book_mapping = dict(cursor.fetchall())
        
        for _, rating in ratings_df.iterrows():
            if count >= limit:
                break
            user_id = user_mapping.get(rating.get('User-ID'))
            book_id = book_mapping.get(rating.get('ISBN'))
            
            if user_id and book_id:
                sql = """
                INSERT INTO dataset_ratings (dataset_user_id, book_id, rating)
                VALUES (%s, %s, %s)
                """
                
                cursor.execute(sql, (user_id, book_id, rating.get('Book-Rating')))
                count += 1
        
        self.conn.commit()
        cursor.close()
    
    def run_import(self):
        """Uruchom pełny import tylko jeśli baza jest pusta"""
        logger.info("Starting Book-Crossing import...")

        self.connect_db()
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM books")
        books_count = cursor.fetchone()[0]
        cursor.close()

        if books_count > 0:
            logger.info("Baza już zawiera dane – import pominięty.")
            return

        books, users, ratings = self.load_book_crossing_data()
        
        logger.info("Importing books...")
        self.import_books(books)
        
        logger.info("Importing users...")
        self.import_users(users)
        
        logger.info("Importing ratings...")
        self.import_ratings(ratings)
        
        logger.info("Import completed!")
        self.conn.close()

# Przykład użycia
if __name__ == "__main__":
    db_config = {
        'host': os.environ.get('POSTGRES_HOST', 'db'),
        'database': os.environ.get('POSTGRES_DB', 'book_recommendations'),
        'user': os.environ.get('POSTGRES_USER', 'postgres'),
        'password': os.environ.get('POSTGRES_PASSWORD', 'postgres')
    }
    
    importer = BookCrossingImporter(
        db_config=db_config,
        #google_api_key=os.environ.get("GOOGLE_BOOKS_API_KEY")  # Opcjonalne
    )

    importer.run_import()