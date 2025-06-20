import pandas as pd
import requests
import time
import psycopg2
import json
from typing import Dict, Optional, List
import logging
import os
from datetime import datetime  

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BookCrossingImporter:
    def __init__(self, db_config: Dict):
        self.db_config = db_config
        self.conn = None
        self.open_library_base_url = "https://openlibrary.org"
        self.open_library_covers_url = "https://covers.openlibrary.org/b"
        
    def connect_db(self):
        """Połączenie z bazą danych"""
        logger.info("Connecting to database...")
        self.conn = psycopg2.connect(**self.db_config)
        logger.info("Database connection established")
        
    def load_book_crossing_data(self):
        """Załaduj dane Book-Crossing"""
        logger.info("Loading CSV files...")
        
        books = pd.read_csv('/data/Books.csv', encoding='latin-1', sep=';', on_bad_lines='skip')
        users = pd.read_csv('/data/Users.csv', encoding='latin-1', sep=';', on_bad_lines='skip')
        ratings = pd.read_csv('/data/Ratings.csv', encoding='latin-1', sep=';', on_bad_lines='skip')
        
        logger.info(f"Loaded {len(books)} books, {len(users)} users, {len(ratings)} ratings")
        logger.info(f"Books columns: {list(books.columns)}")
        logger.info(f"Users columns: {list(users.columns)}")
        logger.info(f"Ratings columns: {list(ratings.columns)}")
        
        return books, users, ratings
    
    def get_open_library_info(self, isbn: str, title: str, author: str) -> Dict:
        """Pobierz informacje z Open Library API"""
        try:
            if isbn and isbn != '0':
                clean_isbn = isbn.replace('-', '').replace(' ', '')
                
                url = f"{self.open_library_base_url}/api/books"
                params = {
                    'bibkeys': f'ISBN:{clean_isbn}',
                    'jscmd': 'data',
                    'format': 'json'
                }
                
                response = requests.get(url, params=params, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    isbn_key = f'ISBN:{clean_isbn}'
                    if isbn_key in data:
                        return self.extract_open_library_info(data[isbn_key], clean_isbn)
            
        except Exception as e:
            logger.warning(f"Error fetching Open Library data for ISBN {isbn}: {e}")
        
        return {}
    
    def extract_open_library_info(self, book_data: Dict, isbn: str) -> Dict:
        """Wyciągnij informacje z odpowiedzi Open Library API"""
        extracted_info = {}
        
        if 'title' in book_data:
            extracted_info['ol_title'] = book_data['title']
        
        if 'authors' in book_data and book_data['authors']:
            authors = [author.get('name', '') for author in book_data['authors']]
            extracted_info['ol_authors'] = authors
        
        if 'number_of_pages' in book_data:
            extracted_info['page_count'] = book_data['number_of_pages']
        
        if isbn:
            extracted_info['image_url_s'] = f"{self.open_library_covers_url}/isbn/{isbn}-S.jpg"
            extracted_info['image_url_m'] = f"{self.open_library_covers_url}/isbn/{isbn}-M.jpg"
            extracted_info['image_url_l'] = f"{self.open_library_covers_url}/isbn/{isbn}-L.jpg"
        
        if 'subjects' in book_data:
            subjects = [subject.get('name', '') for subject in book_data['subjects']]
            extracted_info['categories'] = subjects[:10]
        
        if 'key' in book_data:
            extracted_info['open_library_id'] = book_data['key']
        
        return extracted_info
    
    def import_books(self, books_df: pd.DataFrame, limit=1000):
        """Import książek do ujednoliconej tabeli books"""
        logger.info(f"Starting book import with limit: {limit}")
        
        cursor = self.conn.cursor()
        count = 0
        success_count = 0
        error_count = 0
        current_time = datetime.now()
        
        for idx, book in books_df.iterrows():
            if count >= limit:
                break

            # Elastyczne nazwy kolumn
            title = book.get('Title') or book.get('Book-Title') or book.get('title')
            author = book.get('Author') or book.get('Book-Author') or book.get('author')
            
            if not title or pd.isna(title):
                logger.warning(f"Skipping book without title (ISBN: {book.get('ISBN')})")
                error_count += 1
                continue

            # Open Library data (co 5. książkę zamiast co 20.)
            ol_info = {}
            if idx % 5 == 0:  # Więcej książek z okładkami
                ol_info = self.get_open_library_info(book.get('ISBN', ''), title, author)
                time.sleep(0.3)  # Krótszy sleep
            
            # Przygotuj dane
            isbn = book.get('ISBN', '').replace('-', '').replace(' ', '') if book.get('ISBN') else ''
            publisher = book.get('Publisher') or book.get('publisher')
            year = book.get('Year') or book.get('Year-Of-Publication') or book.get('publication_year')
            
            insert_data = {
                'isbn': book.get('ISBN'),
                'title': title,
                'author': author,
                'publisher': publisher,
                'publication_year': year if pd.notna(year) else None,
                'image_url_s': ol_info.get('image_url_s'),
                'image_url_m': ol_info.get('image_url_m'),
                'image_url_l': ol_info.get('image_url_l'),
                'description': None,
                'categories': ol_info.get('categories'),
                'page_count': ol_info.get('page_count'),
                'language': 'en',
                'average_rating': None,
                'ratings_count': None,
                'open_library_id': ol_info.get('open_library_id'),
                'created_at': current_time,
                'updated_at': current_time
            }
            
            sql = """
                INSERT INTO books (isbn, title, author, publisher, publication_year, 
                                image_url_s, image_url_m, image_url_l, description, 
                                categories, page_count, language, average_rating, 
                                ratings_count, open_library_id, created_at, updated_at)
                VALUES (%(isbn)s, %(title)s, %(author)s, %(publisher)s, %(publication_year)s,
                        %(image_url_s)s, %(image_url_m)s, %(image_url_l)s, %(description)s,
                        %(categories)s, %(page_count)s, %(language)s, %(average_rating)s,
                        %(ratings_count)s, %(open_library_id)s, %(created_at)s, %(updated_at)s)
                ON CONFLICT (isbn) DO NOTHING
                """
            
            try:
                cursor.execute(sql, insert_data)
                count += 1
                success_count += 1
                
                if count % 100 == 0:
                    logger.info(f"Processed {count} books (Success: {success_count}, Errors: {error_count})")
                    self.conn.commit()
                    
            except Exception as e:
                logger.error(f"Error inserting book '{title}': {e}")
                self.conn.rollback()
                error_count += 1
                
        self.conn.commit()
        cursor.close()
        logger.info(f"Book import completed! Success: {success_count}, Errors: {error_count}")

    def import_users(self, users_df: pd.DataFrame, limit=500):
        """Import użytkowników do ujednoliconej tabeli users"""
        logger.info(f"Starting user import with limit: {limit}")
        logger.info(f"User CSV columns: {list(users_df.columns)}")
        
        cursor = self.conn.cursor()
        count = 0
        success_count = 0
        error_count = 0
        
        for idx, user in users_df.iterrows():
            if count >= limit:
                break
                
            # Przetwórz dane użytkownika
            user_id = user.get('User-ID')
            age = user.get('Age') if pd.notna(user.get('Age')) and user.get('Age') != '' else None
            
            # Lokalizacja (jeśli jest)
            city = state = country = None
            if 'Location' in user and pd.notna(user.get('Location')) and user.get('Location'):
                location_parts = str(user.get('Location')).split(',')
                city = location_parts[0].strip() if len(location_parts) > 0 else None
                state = location_parts[1].strip() if len(location_parts) > 1 else None
                country = location_parts[2].strip() if len(location_parts) > 2 else None
            
            sql = """
            INSERT INTO users (original_user_id, age, city, state, country, user_type, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (original_user_id) DO NOTHING
            """
            
            try:
                cursor.execute(sql, (
                    user_id,
                    age,
                    city,
                    state,
                    country,
                    'dataset',  # Typ użytkownika z datasetu
                    datetime.now()
                ))
                count += 1
                success_count += 1
                
                if count % 200 == 0:
                    logger.info(f"Processed {count} users")
                    self.conn.commit()
                    
            except Exception as e:
                logger.error(f"Error inserting user {user_id}: {e}")
                self.conn.rollback()
                error_count += 1
        
        self.conn.commit()
        cursor.close()
        logger.info(f"User import completed! Success: {success_count}, Errors: {error_count}")
    
    def import_ratings(self, ratings_df: pd.DataFrame, limit=50000):
        """Import ocen do ujednoliconej tabeli ratings"""
        logger.info(f"Starting ratings import with limit: {limit}")
        
        cursor = self.conn.cursor()
        count = 0
        success_count = 0
        error_count = 0
        
        # Pobierz mapowania ID
        logger.info("Loading user and book mappings...")
        cursor.execute("SELECT original_user_id, id FROM users WHERE user_type = 'dataset'")
        user_mapping = dict(cursor.fetchall())
        logger.info(f"Loaded {len(user_mapping)} user mappings")
        
        cursor.execute("SELECT isbn, id FROM books WHERE isbn IS NOT NULL")
        book_mapping = dict(cursor.fetchall())
        logger.info(f"Loaded {len(book_mapping)} book mappings")
        
        for idx, rating in ratings_df.iterrows():
            if count >= limit:
                break
                
            user_id = user_mapping.get(rating.get('User-ID'))
            book_id = book_mapping.get(rating.get('ISBN'))
            original_rating = rating.get('Book-Rating')
            
            if user_id and book_id and pd.notna(original_rating):
                # Konwertuj ocenę z 0-10 na 1-5
                if original_rating == 0:
                    normalized_rating = 1.0
                else:
                    normalized_rating = round((original_rating / 2.0) + 0.5, 1)
                
                sql = """
                INSERT INTO ratings (user_id, book_id, rating, original_rating, rating_scale, source_type, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id, book_id) DO NOTHING
                """
                
                try:
                    cursor.execute(sql, (
                        user_id, 
                        book_id, 
                        normalized_rating,
                        original_rating,
                        '0-10',
                        'dataset',
                        datetime.now()
                    ))
                    count += 1
                    success_count += 1
                    
                    if count % 2000 == 0:
                        logger.info(f"Processed {count} ratings")
                        self.conn.commit()
                        
                except Exception as e:
                    logger.error(f"Error inserting rating: {e}")
                    self.conn.rollback()
                    error_count += 1
            else:
                if count % 5000 == 0:
                    logger.debug(f"Skipping rating - missing user_id: {user_id}, book_id: {book_id}")
        
        self.conn.commit()
        cursor.close()
        logger.info(f"Ratings import completed! Success: {success_count}, Errors: {error_count}")

    def run_import(self):
        """Uruchom pełny import do ujednoliconych tabel"""
        logger.info("Starting unified Book-Crossing import...")

        self.connect_db()
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("SELECT COUNT(*) FROM books")
            books_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM users WHERE user_type = 'dataset'")
            users_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM ratings WHERE source_type = 'dataset'")
            ratings_count = cursor.fetchone()[0]
            
            logger.info(f"Current data in database:")
            logger.info(f"  Books: {books_count}")
            logger.info(f"  Dataset Users: {users_count}")
            logger.info(f"  Dataset Ratings: {ratings_count}")
            
        except Exception as e:
            logger.error(f"Error checking database: {e}")
            cursor.close()
            return
            
        cursor.close()

        # POPRAWIONE: Import zawsze, ale z logowaniem co już jest
        logger.info("Loading data files...")
        books, users, ratings = self.load_book_crossing_data()
        
        if books_count == 0:
            logger.info("Starting book import...")
            self.import_books(books, limit=200)
        else:
            logger.info(f"Skipping book import - already have {books_count} books")
        
        if users_count == 0:
            logger.info("Starting user import...")
            self.import_users(users, limit=500)
            # Sprawdź ponownie po imporcie
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users WHERE user_type = 'dataset'")
            users_count = cursor.fetchone()[0]
            cursor.close()
            logger.info(f"After import: {users_count} users in database")
        else:
            logger.info(f"Skipping user import - already have {users_count} users")
        
        if ratings_count == 0:  # Uproszczone - zawsze próbuj jeśli nie ma ocen
            logger.info("Starting ratings import...")
            self.import_ratings(ratings, limit=10000)
        else:
            logger.info(f"Skipping ratings import - already have {ratings_count} ratings")
        
        logger.info("Unified import completed!")
        self.conn.close()

if __name__ == "__main__":
    db_config = {
        'host': os.environ.get('POSTGRES_HOST', 'db'),
        'database': os.environ.get('POSTGRES_DB', 'book_recommendations'),
        'user': os.environ.get('POSTGRES_USER', 'postgres'),
        'password': os.environ.get('POSTGRES_PASSWORD', 'postgres')
    }
    
    importer = BookCrossingImporter(db_config=db_config)
    importer.run_import()