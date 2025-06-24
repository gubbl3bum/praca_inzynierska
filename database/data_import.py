import os
import sys
import django
import pandas as pd
import psycopg2
import requests
import zipfile
import re
from django.db import transaction
from django.db.models import Count
from decimal import Decimal

# Setup Django 
sys.path.append('/backend')  # Backend is in /backend via volume mount
sys.path.append('/app')      # Scripts are in /app
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from ml_api.models import Book, Author, Publisher, Category, User, Rating

def clean_text(text):
    """Cleans text from unnecessary characters"""
    if pd.isna(text) or text == '':
        return None
    
    text = str(text).strip()
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with single space
    
    return text if text else None

def parse_authors(author_string):
    """Parses author string into a list"""
    if not author_string:
        return []
    
    author_string = clean_text(author_string)
    if not author_string:
        return []
    
    # Different author separators
    separators = [', ', ' and ', ' & ', ';']
    authors = [author_string]
    
    for separator in separators:
        if separator in author_string:
            authors = [a.strip() for a in author_string.split(separator)]
            break
    
    # Remove empty and duplicates
    authors = list(set([a for a in authors if a and a.strip()]))
    
    return authors

def get_or_create_author(name):
    """Gets or creates an author"""
    if not name:
        return None
    
    name = clean_text(name)
    if not name:
        return None
    
    author, created = Author.objects.get_or_create(
        name=name
    )
    
    if created:
        print(f"    Created author: {name}")
    
    return author

def get_or_create_publisher(name):
    """Gets or creates a publisher"""
    if not name:
        return None
    
    name = clean_text(name)
    if not name:
        return None
    
    publisher, created = Publisher.objects.get_or_create(
        name=name
    )
    
    if created:
        print(f"    Created publisher: {name}")
    
    return publisher

def get_or_create_category(name):
    """Gets or creates a category"""
    if not name:
        return None
    
    name = clean_text(name)
    if not name:
        return None
    
    category, created = Category.objects.get_or_create(
        name=name
    )
    
    if created:
        print(f"    Created category: {name}")
    
    return category

def wait_for_database():
    """Waits for database availability"""
    import time
    
    db_config = {
        'host': os.environ.get('POSTGRES_HOST', 'db'),
        'database': os.environ.get('POSTGRES_DB', 'book_recommendations'),
        'user': os.environ.get('POSTGRES_USER', 'postgres'),
        'password': os.environ.get('POSTGRES_PASSWORD', 'postgres'),
        'port': os.environ.get('POSTGRES_PORT', '5432'),
    }
    
    print("🔄 Waiting for database...")
    
    for attempt in range(30):
        try:
            conn = psycopg2.connect(**db_config)
            conn.close()
            print("Database available!")
            return True
        except psycopg2.OperationalError:
            print(f"   Attempt {attempt + 1}/30 - waiting...")
            time.sleep(2)
    
    print("Failed to connect to database!")
    return False

def run_migrations():
    """Runs Django migrations"""
    import subprocess
    
    print("Running Django migrations...")
    
    try:
        # Create migrations - CORRECTED PATH
        result = subprocess.run([
            'python', '/backend/manage.py', 'makemigrations', 'ml_api'
        ], capture_output=True, text=True, cwd='/backend')
        
        if result.returncode != 0:
            print(f" Makemigrations warning: {result.stderr}")
        
        # Execute migrations - CORRECTED PATH
        result = subprocess.run([
            'python', '/backend/manage.py', 'migrate'
        ], capture_output=True, text=True, cwd='/backend')
        
        if result.returncode == 0:
            print("Migrations completed successfully!")
            return True
        else:
            print(f"Migration error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error during migrations: {e}")
        return False

def import_users_csv(csv_file_path):
    """Imports users from CSV file"""
    
    print(f"\nIMPORTING USERS FROM {csv_file_path}")
    print("=" * 60)
    
    if not os.path.exists(csv_file_path):
        print(f"File not found: {csv_file_path}")
        return False
    
    try:
        # Load CSV
        print(f"Loading data from {csv_file_path}...")
        
        # Try different separators and encodings
        separators = [';', ',', '\t']
        encodings = ['utf-8', 'iso-8859-1', 'cp1252']
        
        df = None
        for sep in separators:
            for enc in encodings:
                try:
                    df = pd.read_csv(csv_file_path, sep=sep, encoding=enc)
                    if len(df.columns) >= 3:  # Must have at least 3 columns
                        print(f"Loaded with separator '{sep}' and encoding '{enc}'")
                        break
                except:
                    continue
            if df is not None and len(df.columns) >= 3:
                break
        
        if df is None or len(df.columns) < 3:
            print("Failed to load CSV file with any separator/encoding")
            return False
        
        print(f"Loaded {len(df)} records")
        print(f"Columns: {list(df.columns)}")
        
        # Column mapping for users
        column_mapping = {}
        for col in df.columns:
            col_lower = col.lower()
            if 'user' in col_lower and ('id' in col_lower or 'no' in col_lower):
                column_mapping['user_id'] = col
            elif 'location' in col_lower or 'city' in col_lower:
                column_mapping['location'] = col
            elif 'age' in col_lower:
                column_mapping['age'] = col
            elif 'name' in col_lower or 'username' in col_lower:
                column_mapping['name'] = col
        
        print(f"Column mapping: {column_mapping}")
        
        # Statistics
        stats = {
            'users_created': 0,
            'users_updated': 0,
            'users_skipped': 0,
            'errors': []
        }
        
        # Import in transaction
        with transaction.atomic():
            
            for index, row in df.iterrows():
                try:
                    # Extract data from mapped columns
                    user_id = row.get(column_mapping.get('user_id'))
                    location = clean_text(row.get(column_mapping.get('location')))
                    age = row.get(column_mapping.get('age'))
                    name = clean_text(row.get(column_mapping.get('name')))
                    
                    if pd.isna(user_id) or user_id == '':
                        if (index + 1) % 10000 == 0:
                            print(f"   ⚠️  Row {index + 1}: Skipped - missing user_id")
                        stats['users_skipped'] += 1
                        continue
                    
                    try:
                        user_id = int(user_id)
                    except (ValueError, TypeError):
                        stats['users_skipped'] += 1
                        continue
                    
                    if (index + 1) % 5000 == 0:
                        print(f"👤 Processing user {index + 1}/{len(df)}: User {user_id}...")
                    
                    # Check if user already exists
                    user = None
                    try:
                        user = User.objects.get(original_user_id=user_id)
                    except User.DoesNotExist:
                        pass
                    
                    # Prepare data for saving
                    user_data = {
                        'original_user_id': user_id,
                        'user_type': 'dataset',  # Users from dataset
                    }
                    
                    # Add age
                    if pd.notna(age) and age != '':
                        try:
                            age_int = int(age)
                            if 10 <= age_int <= 120:  # Reasonable age range
                                user_data['age'] = age_int
                        except (ValueError, TypeError):
                            pass
                    
                    # Parse location (assuming format "City, State, Country")
                    if location:
                        location_parts = [part.strip() for part in location.split(',')]
                        if len(location_parts) >= 1:
                            user_data['city'] = location_parts[0]
                        if len(location_parts) >= 2:
                            user_data['state'] = location_parts[1]
                        if len(location_parts) >= 3:
                            user_data['country'] = location_parts[2]
                    
                    # Add username
                    if name:
                        user_data['username'] = name
                    
                    # Create or update user
                    if user:
                        # Update existing
                        for key, value in user_data.items():
                            if value is not None:
                                setattr(user, key, value)
                        user.save()
                        stats['users_updated'] += 1
                    else:
                        # Create new
                        user = User.objects.create(**user_data)
                        stats['users_created'] += 1
                    
                except Exception as e:
                    error_msg = f"Error in row {index + 1}: {str(e)}"
                    stats['errors'].append(error_msg)
                    if len(stats['errors']) <= 10:  # Show only first 10 errors
                        print(f"   ❌ {error_msg}")
                    continue
        
        # Summary
        print("\n" + "=" * 60)
        print("USER IMPORT SUMMARY:")
        print(f"Users created: {stats['users_created']}")
        print(f"Users updated: {stats['users_updated']}")
        print(f"Users skipped: {stats['users_skipped']}")
        print(f"Errors: {len(stats['errors'])}")
        
        return True
        
    except Exception as e:
        print(f"Critical error during user import: {e}")
        return False

def import_ratings_csv(csv_file_path):
    """Imports ratings from CSV file"""
    
    print(f"\nIMPORTING RATINGS FROM {csv_file_path}")
    print("=" * 60)
    
    if not os.path.exists(csv_file_path):
        print(f"File not found: {csv_file_path}")
        return False
    
    try:
        # Load CSV
        print(f"Loading data from {csv_file_path}...")
        
        # Try different separators and encodings
        separators = [';', ',', '\t']
        encodings = ['utf-8', 'iso-8859-1', 'cp1252']
        
        df = None
        for sep in separators:
            for enc in encodings:
                try:
                    df = pd.read_csv(csv_file_path, sep=sep, encoding=enc)
                    if len(df.columns) >= 3:  # Must have at least 3 columns
                        print(f"Loaded with separator '{sep}' and encoding '{enc}'")
                        break
                except:
                    continue
            if df is not None and len(df.columns) >= 3:
                break
        
        if df is None or len(df.columns) < 3:
            print("Failed to load CSV file with any separator/encoding")
            return False
        
        print(f"Loaded {len(df)} records")
        print(f"Columns: {list(df.columns)}")
        
        # Column mapping for ratings
        column_mapping = {}
        for col in df.columns:
            col_lower = col.lower()
            if 'user' in col_lower and ('id' in col_lower or 'no' in col_lower):
                column_mapping['user_id'] = col
            elif 'isbn' in col_lower:
                column_mapping['isbn'] = col
            elif 'book' in col_lower and 'rating' in col_lower:
                column_mapping['rating'] = col
            elif 'rating' in col_lower and 'book' not in col_lower:
                column_mapping['rating'] = col
        
        print(f"🗺️  Column mapping: {column_mapping}")
        
        # Check if we have required columns
        required_fields = ['user_id', 'isbn', 'rating']
        missing_fields = [field for field in required_fields if field not in column_mapping]
        
        if missing_fields:
            print(f"Missing required columns: {missing_fields}")
            return False
        
        # Statistics
        stats = {
            'ratings_created': 0,
            'ratings_updated': 0,
            'ratings_skipped': 0,
            'users_not_found': 0,
            'books_not_found': 0,
            'errors': []
        }
        
        # Cache for performance
        user_cache = {}
        book_cache = {}
        
        # Import in transaction
        with transaction.atomic():
            
            for index, row in df.iterrows():
                try:
                    # Extract data from mapped columns
                    user_id = row.get(column_mapping.get('user_id'))
                    isbn = clean_text(row.get(column_mapping.get('isbn')))
                    rating_value = row.get(column_mapping.get('rating'))
                    
                    # Check required fields
                    if pd.isna(user_id) or pd.isna(rating_value) or not isbn:
                        stats['ratings_skipped'] += 1
                        continue
                    
                    try:
                        user_id = int(user_id)
                        rating_value = float(rating_value)
                    except (ValueError, TypeError):
                        stats['ratings_skipped'] += 1
                        continue
                    
                    # Check rating range
                    if not (0 <= rating_value <= 10):  # Assuming 0-10 scale
                        stats['ratings_skipped'] += 1
                        continue
                    
                    if (index + 1) % 10000 == 0:
                        print(f"⭐ Processing rating {index + 1}/{len(df)}: User {user_id} -> {isbn} = {rating_value}...")
                    
                    # Find user (with cache)
                    user = None
                    if user_id in user_cache:
                        user = user_cache[user_id]
                    else:
                        try:
                            user = User.objects.get(original_user_id=user_id)
                            user_cache[user_id] = user
                        except User.DoesNotExist:
                            user_cache[user_id] = None
                    
                    if not user:
                        stats['users_not_found'] += 1
                        continue
                    
                    # Find book (with cache)
                    book = None
                    if isbn in book_cache:
                        book = book_cache[isbn]
                    else:
                        try:
                            book = Book.objects.get(isbn=isbn)
                            book_cache[isbn] = book
                        except Book.DoesNotExist:
                            book_cache[isbn] = None
                    
                    if not book:
                        stats['books_not_found'] += 1
                        continue
                    
                    # Check if rating already exists
                    rating_obj = None
                    try:
                        rating_obj = Rating.objects.get(user=user, book=book)
                    except Rating.DoesNotExist:
                        pass
                    
                    # Convert rating to 1-5 scale
                    if rating_value == 0:
                        normalized_rating = Decimal('1.0')  # 0 -> 1
                        rating_scale = '0-10'
                    elif rating_value <= 5:
                        normalized_rating = Decimal(str(rating_value))  # 1-5 -> 1-5
                        rating_scale = '1-5'
                    else:
                        # Scale 6-10 -> convert to 1-5
                        normalized_rating = round(Decimal(rating_value) / 2 + Decimal('0.5'), 1)
                        rating_scale = '0-10'
                    
                    # Prepare data for saving
                    rating_data = {
                        'user': user,
                        'book': book,
                        'rating': normalized_rating,
                        'original_rating': int(rating_value),
                        'rating_scale': rating_scale,
                        'source_type': 'dataset'
                    }
                    
                    # Create or update rating
                    if rating_obj:
                        # Update existing
                        for key, value in rating_data.items():
                            setattr(rating_obj, key, value)
                        rating_obj.save()
                        stats['ratings_updated'] += 1
                    else:
                        # Create new
                        rating_obj = Rating.objects.create(**rating_data)
                        stats['ratings_created'] += 1
                    
                except Exception as e:
                    error_msg = f"Error in row {index + 1}: {str(e)}"
                    stats['errors'].append(error_msg)
                    if len(stats['errors']) <= 10:  # Show only first 10 errors
                        print(f"   ❌ {error_msg}")
                    continue
        
        # Summary
        print("\n" + "=" * 60)
        print("RATING IMPORT SUMMARY:")
        print(f"Ratings created: {stats['ratings_created']}")
        print(f"Ratings updated: {stats['ratings_updated']}")
        print(f"Ratings skipped: {stats['ratings_skipped']}")
        print(f"Users not found: {stats['users_not_found']}")
        print(f"Books not found: {stats['books_not_found']}")
        print(f"Errors: {len(stats['errors'])}")
        
        return True
        
    except Exception as e:
        print(f"Critical error during rating import: {e}")
        return False

def import_books_csv(csv_file_path):
    """Imports books from CSV file to normalized database"""
    
    print(f"\nIMPORTING BOOKS FROM {csv_file_path}")
    print("=" * 60)
    
    if not os.path.exists(csv_file_path):
        print(f"File not found: {csv_file_path}")
        return False
    
    try:
        # Load CSV
        print(f"Loading data from {csv_file_path}...")
        
        # Try different separators and encodings
        separators = [';', ',', '\t']
        encodings = ['utf-8', 'iso-8859-1', 'cp1252']
        
        df = None
        for sep in separators:
            for enc in encodings:
                try:
                    df = pd.read_csv(csv_file_path, sep=sep, encoding=enc)
                    if len(df.columns) >= 4:  # Must have at least 4 columns
                        print(f"Loaded with separator '{sep}' and encoding '{enc}'")
                        break
                except:
                    continue
            if df is not None and len(df.columns) >= 4:
                break
        
        if df is None or len(df.columns) < 4:
            print("Failed to load CSV file with any separator/encoding")
            return False
        
        print(f"Loaded {len(df)} records")
        print(f"Columns: {list(df.columns)}")
        
        # Column mapping (flexible names)
        column_mapping = {}
        for col in df.columns:
            col_lower = col.lower()
            if 'isbn' in col_lower:
                column_mapping['isbn'] = col
            elif 'title' in col_lower or 'book' in col_lower:
                column_mapping['title'] = col
            elif 'author' in col_lower:
                column_mapping['author'] = col
            elif 'year' in col_lower or 'date' in col_lower:
                column_mapping['year'] = col
            elif 'publisher' in col_lower:
                column_mapping['publisher'] = col
        
        print(f"🗺️  Column mapping: {column_mapping}")
        
        # Statistics
        stats = {
            'books_created': 0,
            'books_updated': 0,
            'books_skipped': 0,
            'authors_created': 0,
            'publishers_created': 0,
            'errors': []
        }
        
        # Import in transaction
        with transaction.atomic():
            
            for index, row in df.iterrows():
                try:
                    # Extract data from mapped columns
                    isbn = clean_text(row.get(column_mapping.get('isbn')))
                    title = clean_text(row.get(column_mapping.get('title')))
                    author_string = clean_text(row.get(column_mapping.get('author')))
                    publisher_string = clean_text(row.get(column_mapping.get('publisher')))
                    year = row.get(column_mapping.get('year'))
                    
                    if not title:
                        if (index + 1) % 10000 == 0:
                            print(f"     Row {index + 1}: Skipped - missing title")
                        stats['books_skipped'] += 1
                        continue
                    
                    if (index + 1) % 1000 == 0:
                        print(f"📖 Processing book {index + 1}/{len(df)}: {title[:50]}...")
                    
                    # Check if book already exists
                    book = None
                    if isbn:
                        try:
                            book = Book.objects.get(isbn=isbn)
                        except Book.DoesNotExist:
                            pass
                    
                    if not book and title and author_string:
                        # Check by title and first author
                        authors_list = parse_authors(author_string)
                        if authors_list:
                            first_author = authors_list[0]
                            existing_books = Book.objects.filter(
                                title__iexact=title,
                                authors__name__iexact=first_author
                            )
                            if existing_books.exists():
                                book = existing_books.first()
                    
                    # Prepare data for saving
                    book_data = {
                        'title': title,
                        'isbn': isbn,
                    }
                    
                    # Add publication year
                    if pd.notna(year) and year != '':
                        try:
                            year_int = int(year)
                            if 1000 <= year_int <= 2030:  # Reasonable year range
                                book_data['publication_year'] = year_int
                        except (ValueError, TypeError):
                            pass
                    
                    # Create or update book
                    if book:
                        # Update existing
                        for key, value in book_data.items():
                            if value is not None:
                                setattr(book, key, value)
                        book.save()
                        stats['books_updated'] += 1
                    else:
                        # Create new
                        book = Book.objects.create(**book_data)
                        stats['books_created'] += 1
                    
                    # Add authors
                    if author_string:
                        authors_list = parse_authors(author_string)
                        book_authors = []
                        
                        for author_name in authors_list:
                            author = get_or_create_author(author_name)
                            if author:
                                book_authors.append(author)
                        
                        if book_authors:
                            book.authors.set(book_authors)
                    
                    # Add publisher
                    if publisher_string:
                        publisher = get_or_create_publisher(publisher_string)
                        if publisher:
                            book.publisher = publisher
                            book.save()
                    
                except Exception as e:
                    error_msg = f"Error in row {index + 1}: {str(e)}"
                    stats['errors'].append(error_msg)
                    if len(stats['errors']) <= 10:  # Show only first 10 errors
                        print(f"    {error_msg}")
                    continue
        
        # Summary
        print("\n" + "=" * 60)
        print("BOOK IMPORT SUMMARY:")
        print(f"Books created: {stats['books_created']}")
        print(f"Books updated: {stats['books_updated']}")
        print(f"Books skipped: {stats['books_skipped']}")
        print(f"Authors in database: {Author.objects.count()}")
        print(f"Publishers in database: {Publisher.objects.count()}")
        print(f"Errors: {len(stats['errors'])}")
        
        return True
        
    except Exception as e:
        print(f"Critical error during book import: {e}")
        return False

def update_book_ratings():
    """Updates average book ratings based on ratings table"""
    
    print("\n📊 UPDATING AVERAGE BOOK RATINGS")
    print("=" * 60)
    
    try:
        from django.db.models import Avg, Count
        
        # Calculate average ratings for all books with ratings
        books_with_ratings = Book.objects.annotate(
            avg_rating=Avg('ratings__rating'),
            rating_count=Count('ratings')
        ).filter(rating_count__gt=0)
        
        updated_books = 0
        
        for book in books_with_ratings:
            # Update denormalized fields
            book.average_rating = round(book.avg_rating, 2)
            book.ratings_count = book.rating_count
            book.save(update_fields=['average_rating', 'ratings_count'])
            updated_books += 1
            
            if updated_books % 1000 == 0:
                print(f"   Updated {updated_books} books...")
        
        print(f"Updated ratings for {updated_books} books")
        return True
        
    except Exception as e:
        print(f"Error during rating updates: {e}")
        return False

def analyze_import_results():
    """Analyzes import results"""
    
    print("\n" + "=" * 60)
    print("IMPORT RESULTS ANALYSIS:")
    print("=" * 60)
    
    try:
        # Basic statistics
        total_books = Book.objects.count()
        total_authors = Author.objects.count()
        total_publishers = Publisher.objects.count()
        total_categories = Category.objects.count()
        total_users = User.objects.count()
        total_ratings = Rating.objects.count()
        
        print(f"Total books: {total_books}")
        print(f"Total authors: {total_authors}")
        print(f"Total publishers: {total_publishers}")
        print(f"Total categories: {total_categories}")
        print(f"Total users: {total_users}")
        print(f"Total ratings: {total_ratings}")
        
        if total_authors > 0:
            # Top authors
            print(f"\nTOP 10 AUTHORS (by book count):")
            top_authors = Author.objects.annotate(
                book_count=Count('books')
            ).order_by('-book_count')[:10]
            
            for i, author in enumerate(top_authors, 1):
                print(f"   {i}. {author.name} ({author.book_count} books)")
        
        if total_publishers > 0:
            # Top publishers
            print(f"\nTOP 10 PUBLISHERS (by book count):")
            top_publishers = Publisher.objects.annotate(
                book_count=Count('books')
            ).order_by('-book_count')[:10]
            
            for i, publisher in enumerate(top_publishers, 1):
                print(f"   {i}. {publisher.name} ({publisher.book_count} books)")
        
        if total_ratings > 0:
            # Rating statistics
            from django.db.models import Avg, Max, Min
            rating_stats = Rating.objects.aggregate(
                avg_rating=Avg('rating'),
                min_rating=Min('rating'),
                max_rating=Max('rating')
            )
            
            print(f"\nRATING STATISTICS:")
            print(f"   Average rating: {rating_stats['avg_rating']:.2f}/5.0")
            print(f"   Minimum rating: {rating_stats['min_rating']}")
            print(f"   Maximum rating: {rating_stats['max_rating']}")
            
            # Top rated books
            print(f"\nTOP 10 HIGHEST RATED BOOKS:")
            top_rated_books = Book.objects.filter(
                ratings_count__gte=5  # minimum 5 ratings
            ).order_by('-average_rating', '-ratings_count')[:10]
            
            for i, book in enumerate(top_rated_books, 1):
                author_name = book.primary_author.name if book.primary_author else "Unknown"
                print(f"   {i}. {book.title} by {author_name} ({book.average_rating}/5.0, {book.ratings_count} ratings)")
        
        if total_users > 0:
            # User statistics
            dataset_users = User.objects.filter(user_type='dataset').count()
            app_users = User.objects.filter(user_type='app').count()
            
            print(f"\nUSER STATISTICS:")
            print(f"   From dataset: {dataset_users}")
            print(f"   From app: {app_users}")
            
            # Top countries
            top_countries = User.objects.exclude(country__isnull=True).exclude(country='').values('country').annotate(
                user_count=Count('id')
            ).order_by('-user_count')[:10]
            
            if top_countries:
                print(f"\nTOP 10 USER COUNTRIES:")
                for i, country_data in enumerate(top_countries, 1):
                    print(f"   {i}. {country_data['country']}: {country_data['user_count']} users")
        
        # Books without authors/publishers/ratings
        books_without_authors = Book.objects.filter(authors__isnull=True).count()
        books_without_publishers = Book.objects.filter(publisher__isnull=True).count()
        books_without_ratings = Book.objects.filter(ratings__isnull=True).count()
        
        print(f"\n DATA TO IMPROVE:")
        print(f"   Books without authors: {books_without_authors}")
        print(f"   Books without publishers: {books_without_publishers}")
        print(f"   Books without ratings: {books_without_ratings}")
        
        return True
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        return False

def main():
    """Main import function"""
    
    print("STARTING COMPLETE DATA IMPORT")
    print("=" * 70)
    
    # 1. Wait for database
    if not wait_for_database():
        sys.exit(1)
    
    # 2. Run migrations
    if not run_migrations():
        print(" Continuing despite migration errors...")
    
    # 3. Import books
    print("\n" + "" * 35)
    print("STAGE 1: BOOK IMPORT")
    print("" * 35)
    
    books_csv_paths = [
        '/data/Books.csv',
        '/data/books.csv', 
        '/app/Books.csv',
        '/app/books.csv'
    ]
    
    books_imported = False
    for csv_path in books_csv_paths:
        if os.path.exists(csv_path):
            print(f"Found book file: {csv_path}")
            if import_books_csv(csv_path):
                books_imported = True
                break
    
    if not books_imported:
        print("No book file found for import")
        print(f"Checked paths: {books_csv_paths}")
        print("Contents of /data:")
        try:
            for f in os.listdir('/data'):
                print(f"     - {f}")
        except:
            print("     No access to /data")
        # Continue despite missing books
    
    # 4. Import users
    print("\n" + "" * 35)
    print("STAGE 2: USER IMPORT")
    print("" * 35)
    
    users_csv_paths = [
        '/data/Users.csv',
        '/data/users.csv',
        '/data/BX-Users.csv',
        '/app/Users.csv',
        '/app/users.csv'
    ]
    
    users_imported = False
    for csv_path in users_csv_paths:
        if os.path.exists(csv_path):
            print(f"Found user file: {csv_path}")
            if import_users_csv(csv_path):
                users_imported = True
                break
    
    if not users_imported:
        print("No user file found - skipping")
        print(f"Checked paths: {users_csv_paths}")
    
    # 5. Import ratings
    print("\n" + "" * 35)
    print("STAGE 3: RATING IMPORT")
    print("" * 35)
    
    ratings_csv_paths = [
        '/data/Ratings.csv',
        '/data/ratings.csv',
        '/data/BX-Book-Ratings.csv',
        '/app/Ratings.csv', 
        '/app/ratings.csv'
    ]
    
    ratings_imported = False
    for csv_path in ratings_csv_paths:
        if os.path.exists(csv_path):
            print(f"Found rating file: {csv_path}")
            if import_ratings_csv(csv_path):
                ratings_imported = True
                break
    
    if not ratings_imported:
        print("No rating file found - skipping")
        print(f"   Checked paths: {ratings_csv_paths}")
    
    # 6. Update average book ratings
    if ratings_imported:
        print("\n" + "" * 35)
        print("STAGE 4: UPDATING AVERAGE RATINGS")
        print("" * 35)
        update_book_ratings()
    
    # 7. Analyze results
    print("\n" + "" * 35)
    print("STAGE 5: RESULTS ANALYSIS")
    print("" * 35)
    analyze_import_results()
    
    print("\nCOMPLETE IMPORT FINISHED SUCCESSFULLY!")
    print("Database ready for use")
    print("Check Django Admin: http://localhost:8000/admin/")
    print("Check API: http://localhost:8000/api/books/")
    print("Check API status: http://localhost:8000/api/status/")

if __name__ == "__main__":
    main()