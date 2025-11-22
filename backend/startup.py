import os
import sys
import subprocess
import time

def wait_for_database():
    """Wait for database to be available"""
    print("Waiting for database...")
    
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            result = subprocess.run([
                'nc', '-z', 'db', '5432'
            ], capture_output=True)
            
            if result.returncode == 0:
                print("Database ready!")
                return True
                
        except:
            pass
            
        print(f"   Attempt {attempt + 1}/{max_attempts}...")
        time.sleep(2)
    
    print("Cannot connect to database!")
    return False

def run_migrations():
    """Run Django migrations"""
    print("\nRunning Django migrations...")
    
    try:
        # Makemigrations
        subprocess.run([
            'python', 'manage.py', 'makemigrations', 'ml_api', '--noinput'
        ], check=False)
        
        # Migrate
        result = subprocess.run([
            'python', 'manage.py', 'migrate', '--noinput'
        ], check=True)
        
        print("Migrations completed!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f" Migration error: {e}")
        return False

def check_if_data_exists():
    """Check if database has data"""
    print("\nChecking if database has data...")
    
    try:
        result = subprocess.run([
            'python', '-c', '''
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from ml_api.models import Book
count = Book.objects.count()
print(f"BOOKS_COUNT:{count}")
'''
        ], capture_output=True, text=True, check=True)
        
        # Extract book count from output
        for line in result.stdout.split('\n'):
            if line.startswith('BOOKS_COUNT:'):
                count = int(line.split(':')[1])
                print(f"Found {count} books in database")
                return count > 0
                
    except Exception as e:
        print(f"Error checking data: {e}")
        
    return False

def check_if_users_exist():
    """Check if users with reviews exist"""
    print("\nChecking if users exist...")
    
    try:
        result = subprocess.run([
            'python', '-c', '''
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from ml_api.models import User, BookReview
user_count = User.objects.count()
review_count = BookReview.objects.count()
users_with_reviews = User.objects.filter(reviews__isnull=False).distinct().count()
print(f"USER_COUNT:{user_count}")
print(f"REVIEW_COUNT:{review_count}")
print(f"USERS_WITH_REVIEWS:{users_with_reviews}")
'''
        ], capture_output=True, text=True, check=True)
        
        user_count = 0
        review_count = 0
        users_with_reviews = 0
        
        for line in result.stdout.split('\n'):
            if line.startswith('USER_COUNT:'):
                user_count = int(line.split(':')[1])
            elif line.startswith('REVIEW_COUNT:'):
                review_count = int(line.split(':')[1])
            elif line.startswith('USERS_WITH_REVIEWS:'):
                users_with_reviews = int(line.split(':')[1])
        
        print(f"Found {user_count} users ({users_with_reviews} with reviews)")
        print(f"Found {review_count} reviews")
        
        # Consider having users if we have at least 50 users with reviews
        return users_with_reviews >= 50
                
    except Exception as e:
        print(f"Error checking users: {e}")
        
    return False

def check_if_badges_exist():
    """Check if badges are initialized"""
    print("\nChecking if badges exist...")
    
    try:
        result = subprocess.run([
            'python', '-c', '''
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()
from ml_api.models import Badge
count = Badge.objects.count()
print(f"BADGES_COUNT:{count}")
'''
        ], capture_output=True, text=True, check=True)
        
        # Extract badge count from output
        for line in result.stdout.split('\n'):
            if line.startswith('BADGES_COUNT:'):
                count = int(line.split(':')[1])
                print(f"Found {count} badges in database")
                return count > 0
                
    except Exception as e:
        print(f"Error checking badges: {e}")
        
    return False

def initialize_badges():
    """Initialize badges in database"""
    print("\nInitializing badges...")
    
    try:
        result = subprocess.run([
            'python', 'manage.py', 'init_badges'
        ], check=True)
        
        print("Badges initialized!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Badge initialization failed: {e}")
        return False
    except FileNotFoundError:
        print("init_badges command not found - skipping")
        return False

def run_data_import():
    """Import data from CSV"""
    print("\nRunning data import...")
    
    try:
        result = subprocess.run([
            'python', 'database/normalized_data_import.py'
        ], check=True)
        
        print("Data import completed!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Data import failed: {e}")
        return False

def generate_rich_users():
    """Generate rich user profiles with many reviews"""
    print("\n=== Generating rich user profiles ===")
    
    try:
        result = subprocess.run([
            'python', 'generate_rich_users.py',
            '--heavy', '15',
            '--specialists', '20', 
            '--critics', '15',
            '--enthusiasts', '20',
            '--casual', '30'
        ], check=True)
        
        print("=== Rich user profiles generated! ===")
        return True
    except subprocess.CalledProcessError as e:
        print(f"User generation failed: {e}")
        return False
    except FileNotFoundError:
        print("generate_rich_users.py not found - skipping")
        return False

def calculate_similarities():
    """Calculate book similarities"""
    print("\n=== Calculating book similarities ===")
    
    try:
        result = subprocess.run([
            'python', 'init_similarities.py', '--auto', '--all'
        ], check=True)
        
        print("=== Book similarities calculated! ===")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Similarity calculation failed: {e}")
        return False
    except FileNotFoundError:
        print("init_similarities.py not found - skipping")
        return False

def calculate_user_similarities():
    """Calculate user similarities for collaborative filtering"""
    print("\n=== Calculating user similarities ===")
    
    try:
        result = subprocess.run([
            'python', 'manage.py', 'calculate_user_similarities', '--all'
        ], check=True)
        
        print("=== User similarities calculated! ===")
        return True
    except subprocess.CalledProcessError as e:
        print(f"User similarity calculation failed: {e}")
        return False
    except FileNotFoundError:
        print("calculate_user_similarities command not found - skipping")
        return False

def start_django_server():
    """Start Django development server"""
    print("\n" + "=" * 60)
    print("Starting Django server...")
    print("=" * 60)
    
    try:
        # Use exec to transfer control to Django server process
        os.execvp('python', ['python', 'manage.py', 'runserver', '0.0.0.0:8000'])
    except Exception as e:
        print(f"Cannot start server: {e}")
        sys.exit(1)

def main():
    """Main function"""
    print("=" * 60)
    print("WolfRead - Startup Script")
    print("=" * 60)
    
    # Step 1: Wait for database
    if not wait_for_database():
        sys.exit(1)
    
    # Step 2: Run migrations
    if not run_migrations():
        print("Migrations failed, but continuing...")
    
    # Step 3: Check if data import is needed
    has_books = check_if_data_exists()
    has_users = check_if_users_exist()
    
    if has_books and has_users:
        print("\n" + "=" * 60)
        print("Database already fully initialized - skipping setup")
        print("=" * 60)
    elif has_books and not has_users:
        print("\n" + "=" * 60)
        print("Books exist but users missing - generating users...")
        print("=" * 60)
        
        # Generate rich users
        if generate_rich_users():
            print("\nUser generation completed!")
            
            # Calculate similarities
            print("\nCalculating similarities for new users...")
            calculate_user_similarities()
        else:
            print("User generation failed")
    elif not has_books:
        print("\n" + "=" * 60)
        print("Database is empty - starting full initialization...")
        print("=" * 60)
        
        # Step 4: Import data (books + basic users from CSV)
        if run_data_import():
            # Step 5: Generate additional rich users
            print("\n" + "=" * 60)
            print("Generating additional users for collaborative filtering...")
            print("=" * 60)
            
            if generate_rich_users():
                print("\nRich user profiles created!")
                
                # Step 6: Calculate book similarities
                print("\n" + "=" * 60)
                print("Calculating book similarities...")
                print("=" * 60)
                calculate_similarities()
                
                # Step 7: Calculate user similarities
                print("\n" + "=" * 60)
                print("Calculating user similarities...")
                print("=" * 60)
                calculate_user_similarities()
            else:
                print("User generation failed - continuing anyway")
            
            print("\nFull initialization completed!")
        else:
            print("Import failed, but starting server anyway...")
    
    # Step 8: Initialize badges if needed
    print("\n" + "=" * 60)
    if check_if_badges_exist():
        print("Badges already initialized - skipping")
    else:
        print("Badges not found - initializing...")
        if initialize_badges():
            print("Badge system ready!")
        else:
            print("Badge initialization failed - continuing without badges")
    
    # Step 9: Start Django server
    print("=" * 60)
    print("Initialization complete! Starting server...")
    print("=" * 60)
    start_django_server()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)