import os
import sys
import django
import pandas as pd
import psycopg2
import re
from django.db import transaction
from decimal import Decimal, InvalidOperation
import nltk
from collections import Counter
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Setup Django 
sys.path.append('/backend')
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from ml_api.models import (
    Book, Author, Publisher, Category, BookAuthor, BookCategory,
    User, UserPreferences, BookReview
)

# TESTOWY LIMIT KSIĄŻEK - USUŃ DLA PEŁNEGO IMPORTU
TEST_BOOK_LIMIT = 1000  # Zmień na None dla pełnego importu

def wait_for_database():
    """Wait for database availability"""
    import time
    
    db_config = {
        'host': os.environ.get('POSTGRES_HOST', 'db'),
        'database': os.environ.get('POSTGRES_DB', 'book_recommendations'),
        'user': os.environ.get('POSTGRES_USER', 'postgres'),
        'password': os.environ.get('POSTGRES_PASSWORD', 'postgres'),
        'port': os.environ.get('POSTGRES_PORT', '5432'),
    }
    
    print("Waiting for database...")
    
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
    """Run Django migrations"""
    import subprocess
    
    print("Running Django migrations...")
    
    try:
        # Create migrations
        result = subprocess.run([
            'python', '/app/manage.py', 'makemigrations', 'ml_api', '--noinput'
        ], capture_output=True, text=True, cwd='/app')
        
        if result.returncode != 0:
            print(f"Makemigrations warning: {result.stderr}")
        else:
            print("Migrations created")
        
        # Execute migrations
        result = subprocess.run([
            'python', '/app/manage.py', 'migrate', '--noinput'
        ], capture_output=True, text=True, cwd='/app')
        
        if result.returncode == 0:
            print("Migrations completed successfully!")
            return True
        else:
            print(f"Migration error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error during migrations: {e}")
        return False

def clean_text(text):
    """Clean text from unnecessary characters"""
    if pd.isna(text) or text == '':
        return None
    
    text = str(text).strip()
    text = re.sub(r'\s+', ' ', text)
    
    return text if text else None

def parse_authors(author_string):
    """Parse author string into list of authors"""
    if not author_string:
        return []
    
    author_string = clean_text(author_string)
    if not author_string:
        return []
    
    # Remove "By " prefix if present
    if author_string.startswith("By "):
        author_string = author_string[3:].strip()
    
    # Split by common separators
    separators = [' and ', ' & ', ';', ' with ']
    authors = [author_string]
    
    for separator in separators:
        if separator in author_string:
            authors = [a.strip() for a in author_string.split(separator)]
            break
    
    parsed_authors = []
    for author in authors:
        if not author:
            continue
            
        # Handle "Last, First" format
        if ',' in author:
            parts = [part.strip() for part in author.split(',', 1)]
            if len(parts) == 2:
                last_name, first_name = parts
                parsed_authors.append({'first_name': first_name, 'last_name': last_name})
            else:
                parsed_authors.append({'first_name': '', 'last_name': author})
        else:
            # Handle "First Last" format or single name
            parts = author.strip().split()
            if len(parts) >= 2:
                first_name = ' '.join(parts[:-1])
                last_name = parts[-1]
                parsed_authors.append({'first_name': first_name, 'last_name': last_name})
            else:
                parsed_authors.append({'first_name': '', 'last_name': author})
    
    return parsed_authors

def parse_categories(category_string):
    """Parse category string into list of categories"""
    if not category_string:
        return []
    
    category_string = clean_text(category_string)
    if not category_string:
        return []
    
    # Split by common separators and clean
    separators = [',', ';', '/', '|']
    categories = [category_string]
    
    for separator in separators:
        if separator in category_string:
            categories = [c.strip() for c in category_string.split(separator)]
            break
    
    # Clean and filter categories
    cleaned_categories = []
    for category in categories:
        category = category.strip()
        if category and category.lower() not in ['general', '', 'misc', 'miscellaneous']:
            cleaned_categories.append(category)
    
    return cleaned_categories

def extract_keywords(text, top_n=5):
    """Extract keywords from text using NLTK"""
    if not text or pd.isna(text):
        return ""
    
    try:
        # Initialize NLTK data if not already done
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            print("Downloading NLTK data...")
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
        
        stop_words = set(stopwords.words('english'))
        words = word_tokenize(text.lower())
        keywords = [word for word in words if word.isalnum() and word not in stop_words and len(word) > 2]
        most_common = Counter(keywords).most_common(top_n)
        return ", ".join([keyword for keyword, _ in most_common])
    except Exception as e:
        print(f"Error extracting keywords: {e}")
        return ""

def parse_price(price_string):
    """Parse price string to decimal"""
    if not price_string or pd.isna(price_string):
        return None
    
    try:
        # Remove all characters except digits, dots and commas
        price_str = str(price_string).strip()
        price_str = re.sub(r'[^\d.,]', '', price_str)
        
        # Replace comma with dot if it's at the end (European format)
        if ',' in price_str and '.' not in price_str:
            price_str = price_str.replace(',', '.')
        elif ',' in price_str and '.' in price_str:
            # If both are present, remove comma (probably thousands separator)
            price_str = price_str.replace(',', '')
        
        if price_str:
            return Decimal(price_str)
    except (ValueError, TypeError, InvalidOperation):
        pass
    
    return None

def get_or_create_author(first_name, last_name):
    """Get or create author with proper name handling"""
    if not last_name:
        return None
    
    first_name = clean_text(first_name) or ""
    last_name = clean_text(last_name)
    
    if not last_name:
        return None
    
    # Try to find existing author
    try:
        if first_name:
            author, created = Author.objects.get_or_create(
                first_name=first_name,
                last_name=last_name
            )
        else:
            author, created = Author.objects.get_or_create(
                last_name=last_name,
                defaults={'first_name': ''}
            )
        
        return author
    except Exception as e:
        print(f"Error creating author {first_name} {last_name}: {e}")
        return None

def get_or_create_publisher(name):
    """Get or create publisher"""
    if not name:
        return None
    
    name = clean_text(name)
    if not name:
        return None
    
    try:
        publisher, created = Publisher.objects.get_or_create(name=name)
        return publisher
    except Exception as e:
        print(f"Error creating publisher {name}: {e}")
        return None

def get_or_create_category(name):
    """Get or create category"""
    if not name:
        return None
    
    name = clean_text(name)
    if not name:
        return None
    
    try:
        category, created = Category.objects.get_or_create(name=name)
        return category
    except Exception as e:
        print(f"Error creating category {name}: {e}")
        return None

def import_books_csv(csv_file_path):
    """Import books from CSV file to normalized database"""
    
    print(f"\nIMPORTING BOOKS FROM {csv_file_path}")
    if TEST_BOOK_LIMIT:
        print(f"TESTOWY LIMIT: {TEST_BOOK_LIMIT} books")
    print("=" * 60)
    
    if not os.path.exists(csv_file_path):
        print(f"File not found: {csv_file_path}")
        return False
    
    try:
        print(f"Loading data from {csv_file_path}...")
        
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        df = None
        
        for encoding in encodings:
            try:
                df = pd.read_csv(csv_file_path, encoding=encoding)
                print(f"Loaded with {encoding} encoding")
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            print("Failed to load CSV file with any encoding")
            return False
        
        # OGRANICZENIE TESTOWE
        if TEST_BOOK_LIMIT and len(df) > TEST_BOOK_LIMIT:
            df = df.head(TEST_BOOK_LIMIT)
            print(f"Limited to {TEST_BOOK_LIMIT} books for testing")
        
        print(f"Processing {len(df)} records")
        print(f"Columns: {list(df.columns)}")
        
        # Column mapping (flexible)
        column_mapping = {
            'title': ['Title', 'title', 'book_title'],
            'authors': ['Authors', 'authors', 'author'],
            'description': ['Description', 'description', 'summary'],
            'category': ['Category', 'category', 'categories', 'genre'],
            'publisher': ['Publisher', 'publisher'],
            'price': ['Price', 'price', 'Price Starting With ($)'],
            'publish_month': ['Publish_Month', 'publish_month', 'Publish Date (Month)'],
            'publish_year': ['Publish_Year', 'publish_year', 'Publish Date (Year)'],
        }
        
        # Find appropriate columns
        cols = {}
        for field, possible_names in column_mapping.items():
            for name in possible_names:
                if name in df.columns:
                    cols[field] = name
                    break
        
        print(f"Mapped columns: {cols}")
        
        # Check required columns
        if 'title' not in cols:
            print("No title column found")
            return False
        
        stats = {
            'books_created': 0,
            'books_updated': 0,
            'books_skipped': 0,
            'authors_created': 0,
            'publishers_created': 0,
            'categories_created': 0,
            'errors': []
        }
        
        # Cache for performance
        author_cache = {}
        publisher_cache = {}
        category_cache = {}
        
        print("Starting book import...")
        
        with transaction.atomic():
            for index, row in df.iterrows():
                try:
                    # Show progress
                    if (index + 1) % 100 == 0:
                        print(f"Processed {index + 1}/{len(df)} books...")
                    
                    # Extract basic data
                    title = clean_text(row.get(cols['title']))
                    authors_string = clean_text(row.get(cols.get('authors')))
                    description = clean_text(row.get(cols.get('description')))
                    category_string = clean_text(row.get(cols.get('category')))
                    publisher_string = clean_text(row.get(cols.get('publisher')))
                    
                    # Parse price
                    price = None
                    if 'price' in cols:
                        price_value = row.get(cols['price'])
                        if pd.notna(price_value) and str(price_value).strip():
                            price = parse_price(str(price_value))
                    
                    # Parse month and year
                    publish_month = None
                    if 'publish_month' in cols:
                        month_value = row.get(cols['publish_month'])
                        if pd.notna(month_value) and str(month_value).strip():
                            publish_month = clean_text(str(month_value))
                    
                    publish_year = None
                    if 'publish_year' in cols:
                        year_value = row.get(cols['publish_year'])
                        if pd.notna(year_value) and str(year_value).strip():
                            try:
                                year_candidate = int(float(str(year_value)))
                                if 1000 <= year_candidate <= 2030:
                                    publish_year = year_candidate
                            except (ValueError, TypeError):
                                pass
                    
                    if not title:
                        stats['books_skipped'] += 1
                        continue
                    
                    # Check if book already exists
                    book = None
                    try:
                        book = Book.objects.get(title__iexact=title)
                    except Book.DoesNotExist:
                        pass
                    except Book.MultipleObjectsReturned:
                        book = Book.objects.filter(title__iexact=title).first()
                    
                    # Extract keywords from description
                    keywords = extract_keywords(description) if description else ""
                    
                    # Prepare book data
                    book_data = {
                        'title': title,
                        'description': description,
                        'keywords': keywords,
                        'price': price,
                        'publish_month': publish_month,
                        'publish_year': publish_year,
                    }
                    
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
                    
                    # Process publisher
                    if publisher_string:
                        if publisher_string in publisher_cache:
                            publisher = publisher_cache[publisher_string]
                        else:
                            publisher = get_or_create_publisher(publisher_string)
                            publisher_cache[publisher_string] = publisher
                            if publisher:
                                stats['publishers_created'] += 1
                        
                        if publisher:
                            book.publisher = publisher
                            book.save()
                    
                    # Process authors
                    if authors_string:
                        parsed_authors = parse_authors(authors_string)
                        book_authors = []
                        
                        for author_data in parsed_authors:
                            first_name = author_data.get('first_name', '')
                            last_name = author_data.get('last_name', '')
                            
                            author_key = f"{first_name}|{last_name}"
                            
                            if author_key in author_cache:
                                author = author_cache[author_key]
                            else:
                                author = get_or_create_author(first_name, last_name)
                                author_cache[author_key] = author
                                if author:
                                    stats['authors_created'] += 1
                            
                            if author:
                                book_authors.append(author)
                        
                        if book_authors:
                            # Clear existing relationships and add new ones
                            book.authors.clear()
                            for author in book_authors:
                                BookAuthor.objects.get_or_create(book=book, author=author)
                    
                    # Process categories
                    if category_string:
                        parsed_categories = parse_categories(category_string)
                        book_categories = []
                        
                        for category_name in parsed_categories:
                            if category_name in category_cache:
                                category = category_cache[category_name]
                            else:
                                category = get_or_create_category(category_name)
                                category_cache[category_name] = category
                                if category:
                                    stats['categories_created'] += 1
                            
                            if category:
                                book_categories.append(category)
                        
                        if book_categories:
                            # Clear existing relationships and add new ones
                            book.categories.clear()
                            for category in book_categories:
                                BookCategory.objects.get_or_create(book=book, category=category)
                    
                except Exception as e:
                    error_msg = f"Error in row {index + 1}: {str(e)}"
                    stats['errors'].append(error_msg)
                    if len(stats['errors']) <= 10:
                        print(f"    {error_msg}")
                    continue
        
        # Summary
        print("\n" + "=" * 60)
        print("BOOK IMPORT SUMMARY:")
        print(f"Books created: {stats['books_created']}")
        print(f"Books updated: {stats['books_updated']}")
        print(f"Books skipped: {stats['books_skipped']}")
        print(f"Authors created: {stats['authors_created']}")
        print(f"Publishers created: {stats['publishers_created']}")
        print(f"Categories created: {stats['categories_created']}")
        print(f"Errors: {len(stats['errors'])}")
        
        return True
        
    except Exception as e:
        print(f"Critical error during book import: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_admin_user():
    """Create administrative user"""
    
    print("\nCREATING ADMIN USER")
    print("=" * 40)
    
    try:
        # Check if the admin already exists
        if User.objects.filter(username='admin').exists():
            print("Admin user already exists")
            return True
        
        # Create superuser
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@wolfread.com',
            password='admin123',  # TODO: change in production
            first_name='Admin',
            last_name='User'
        )
        
        print(f"Admin user created: {admin_user.username}")
        print(f"Email: {admin_user.email}")
        print("Password: admin123")
        print("CHANGE PASSWORD IN PRODUCTION!")
        
        return True
        
    except Exception as e:
        print(f"Error creating admin user: {e}")
        return False

def analyze_import_results():
    """Analyze import results and show statistics"""
    
    print("\n" + "=" * 60)
    print("IMPORT RESULTS ANALYSIS")
    print("=" * 60)
    
    try:
        # Basic counts
        total_books = Book.objects.count()
        total_authors = Author.objects.count()
        total_publishers = Publisher.objects.count()
        total_categories = Category.objects.count()
        total_users = User.objects.count()
        total_reviews = BookReview.objects.count()
        
        print(f"Total books: {total_books}")
        print(f"Total authors: {total_authors}")
        print(f"Total publishers: {total_publishers}")
        print(f"Total categories: {total_categories}")
        print(f"Total users: {total_users}")
        print(f"Total reviews: {total_reviews}")
        
        # Sample data check
        if total_books > 0:
            sample_book = Book.objects.first()
            print(f"\nSAMPLE BOOK:")
            print(f"   Title: {sample_book.title}")
            print(f"   Price: {sample_book.price}")
            print(f"   Date: {sample_book.publish_month} {sample_book.publish_year}")
            print(f"   Authors: {sample_book.author_names}")
        
        if total_authors > 0:
            print(f"\nTOP 10 AUTHORS (by book count):")
            from django.db.models import Count
            top_authors = Author.objects.annotate(
                book_count=Count('books')
            ).order_by('-book_count')[:10]
            
            for i, author in enumerate(top_authors, 1):
                print(f"   {i}. {author.full_name} ({author.book_count} books)")
        
        if total_categories > 0:
            print(f"\nTOP 10 CATEGORIES (by book count):")
            top_categories = Category.objects.annotate(
                book_count=Count('books')
            ).order_by('-book_count')[:10]
            
            for i, category in enumerate(top_categories, 1):
                print(f"   {i}. {category.name} ({category.book_count} books)")
        
        if total_reviews > 0:
            from django.db.models import Avg
            avg_rating = BookReview.objects.aggregate(avg=Avg('rating'))['avg']
            
            print(f"\nRATING STATISTICS:")
            print(f"   Average rating: {avg_rating:.2f}/10")
            
            # Top rated books
            print(f"\nTOP 5 HIGHEST RATED BOOKS:")
            top_books = Book.objects.filter(
                reviews__isnull=False
            ).annotate(
                avg_rating=Avg('reviews__rating'),
                review_count=Count('reviews')
            ).filter(review_count__gte=1).order_by('-avg_rating', '-review_count')[:5]
            
            for i, book in enumerate(top_books, 1):
                author_names = book.author_names or "Unknown"
                print(f"   {i}. {book.title} by {author_names} ({book.avg_rating:.1f}/10, {book.review_count} reviews)")
        
        return True
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        return False

def main():
    """Main import function - ONLY BOOKS AND ADMIN"""
    
    print("STARTING NORMALIZED DATA IMPORT")
    if TEST_BOOK_LIMIT:
        print(f"TEST MODE: limited to {TEST_BOOK_LIMIT} books")
    print("=" * 70)
    
    # Check if data already exists
    try:
        existing_books = Book.objects.count()
        existing_users = User.objects.count()
        
        print(f"Current database status:")
        print(f"   Books: {existing_books}")
        print(f"   Users: {existing_users}")
        
        if existing_books > 0:
            print(f"Database already contains {existing_books} books")
            print("Showing current statistics")
            analyze_import_results()
            return True
            
    except Exception as e:
        print(f"Error checking existing data: {e}")
        print("Continuing with full import...")
    
    # 1. Wait for database
    if not wait_for_database():
        print("Database not available - exiting")
        sys.exit(1)
    
    # 2. Run migrations
    print("\n" + "STAGE 1: DATABASE MIGRATIONS")
    
    if not run_migrations():
        print("Migration errors detected, but continuing...")
    
    # 3. Import books
    print("\n" + "STAGE 2: BOOK IMPORT")
    
    # Search for CSV files in various locations
    csv_search_paths = [
        '/app/database/BooksDatasetProcessed.csv',
        '/app/database/BooksDatasetClean.csv',
        '/app/BooksDatasetProcessed.csv',
        '/app/BooksDatasetClean.csv',
        '/data/BooksDatasetProcessed.csv',
        '/data/BooksDatasetClean.csv',
        'database/BooksDatasetProcessed.csv',
        'database/BooksDatasetClean.csv',
        'BooksDatasetProcessed.csv',
        'BooksDatasetClean.csv',
    ]
    
    books_imported = False
    found_file = None
    
    for csv_path in csv_search_paths:
        if os.path.exists(csv_path):
            found_file = csv_path
            print(f"Found book file: {csv_path}")
            
            # Try to import
            if import_books_csv(csv_path):
                books_imported = True
                break
            else:
                print(f"Failed to import from {csv_path}")
    
    if not books_imported:
        print("No book file found for import or import failed")
        print(f"Searched paths:")
        for path in csv_search_paths:
            exists = "EXISTS" if os.path.exists(path) else "NOT FOUND"
            print(f"     {exists}: {path}")
        
        return False
    
    # 4. Create admin user
    print("\n" + "STAGE 3: ADMIN USER CREATION")
    
    try:
        if not create_admin_user():
            print("Admin user creation failed, but continuing...")
    except Exception as e:
        print(f"Admin user creation error: {e}")
    
    # 5. Analyze results
    print("\n" + "STAGE 4: RESULTS ANALYSIS")
    
    try:
        analyze_import_results()
    except Exception as e:
        print(f"Analysis error: {e}")
    
    # Final summary
    print("\n" + "=" * 70)
    print("NORMALIZED IMPORT COMPLETED!")
    print("Database ready with books and admin user")
    
    if TEST_BOOK_LIMIT:
        print(f"\nWARNING: Test mode - imported only {TEST_BOOK_LIMIT} books")
        print("To import all books:")
        print("   1. Change TEST_BOOK_LIMIT = None in the file")
        print("   2. Run import again")
    
    print("\nNOTE: Users and reviews will be generated separately")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\nImport completed successfully!")
            sys.exit(0)
        else:
            print("\nImport failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nImport interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)