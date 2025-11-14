import os
import sys
import subprocess
import time

def wait_for_database():
    """Wait for database to be available"""
    print("⏳ Waiting for database...")
    
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            result = subprocess.run([
                'nc', '-z', 'db', '5432'
            ], capture_output=True)
            
            if result.returncode == 0:
                print("✅ Database ready!")
                return True
                
        except:
            pass
            
        print(f"   Attempt {attempt + 1}/{max_attempts}...")
        time.sleep(2)
    
    print("❌ Cannot connect to database!")
    return False

def run_migrations():
    """Run Django migrations"""
    print("\n📦 Running Django migrations...")
    
    try:
        # Makemigrations
        subprocess.run([
            'python', 'manage.py', 'makemigrations', 'ml_api', '--noinput'
        ], check=False)
        
        # Migrate
        result = subprocess.run([
            'python', 'manage.py', 'migrate', '--noinput'
        ], check=True)
        
        print("✅ Migrations completed!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Migration error: {e}")
        return False

def check_if_data_exists():
    """Check if database has data"""
    print("\n🔍 Checking if database has data...")
    
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
                print(f"📚 Found {count} books in database")
                return count > 0
                
    except Exception as e:
        print(f"⚠️  Error checking data: {e}")
        
    return False

def check_if_badges_exist():
    """Check if badges are initialized"""
    print("\n🏅 Checking if badges exist...")
    
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
                print(f"🎖️  Found {count} badges in database")
                return count > 0
                
    except Exception as e:
        print(f"⚠️  Error checking badges: {e}")
        
    return False

def initialize_badges():
    """Initialize badges in database"""
    print("\n🎖️  Initializing badges...")
    
    try:
        result = subprocess.run([
            'python', 'manage.py', 'init_badges'
        ], check=True, capture_output=True, text=True)
        
        print(result.stdout)
        print("✅ Badges initialized!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Badge initialization failed: {e}")
        print(f"   Output: {e.stdout if hasattr(e, 'stdout') else 'N/A'}")
        print(f"   Error: {e.stderr if hasattr(e, 'stderr') else 'N/A'}")
        return False
    except FileNotFoundError:
        print("⚠️  init_badges command not found - skipping")
        return False

def run_data_import():
    """Import data from CSV"""
    print("\n📥 Running data import...")
    
    try:
        result = subprocess.run([
            'python', 'database/normalized_data_import.py'
        ], check=True)
        
        print("✅ Data import completed!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Data import failed: {e}")
        return False

def initialize_user_preferences():
    """Initialize random user preferences for ALL users"""
    print("\n🎲 Initializing user preferences for all users...")
    
    try:
        result = subprocess.run([
            'python', 'init_user_preferences.py'
        ], check=True, capture_output=True, text=True)
        print(result.stdout)
        print("✅ User preferences initialized!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️  User preferences initialization failed: {e}")
        if hasattr(e, 'stdout'):
            print(e.stdout)
        if hasattr(e, 'stderr'):
            print(e.stderr)
        return False
    except FileNotFoundError:
        print("⚠️  init_user_preferences.py not found - skipping")
        return False

def create_sample_reviews():
    """Create sample reviews for users"""
    print("\n⭐ Creating sample reviews...")
    
    try:
        result = subprocess.run([
            'python', 'create_sample_reviews.py'
        ], check=True, capture_output=True, text=True)
        print(result.stdout)
        print("✅ Sample reviews created!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Sample reviews creation failed: {e}")
        return False
    except FileNotFoundError:
        print("⚠️  create_sample_reviews.py not found - skipping")
        return False

def calculate_user_similarities():
    """Calculate user similarities"""
    print("\n👥 Calculating user similarities...")
    
    try:
        result = subprocess.run([
            'python', 'manage.py', 'calculate_user_similarities', '--all'
        ], check=True, capture_output=True, text=True)
        print(result.stdout)
        print("✅ User similarities calculated!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Similarity calculation failed: {e}")
        if hasattr(e, 'stdout'):
            print(e.stdout)
        if hasattr(e, 'stderr'):
            print(e.stderr)
        return False
    except FileNotFoundError:
        print("⚠️  calculate_user_similarities command not found - skipping")
        return False

def start_django_server():
    """Start Django development server"""
    print("\n🚀 Starting Django server...")
    
    try:
        # Use exec to transfer control to Django server process
        os.execvp('python', ['python', 'manage.py', 'runserver', '0.0.0.0:8000'])
    except Exception as e:
        print(f"❌ Cannot start server: {e}")
        sys.exit(1)

def main():
    """Main function"""
    print("=" * 60)
    print("🐺 WolfRead - Startup Script")
    print("=" * 60)
    
    # Step 1: Wait for database
    if not wait_for_database():
        sys.exit(1)
    
    # Step 2: Run migrations
    if not run_migrations():
        print("Migrations failed, but continuing...")
    
    # Step 3: Check if data import is needed
    if check_if_data_exists():
        print("\nDatabase already has data - skipping import")
    else:
        print("\nDatabase is empty - starting full initialization...")
        
        # Step 4: Import data
        if run_data_import():
            # Step 5: Initialize user preferences (for existing users from CSV)
            initialize_user_preferences()
            
            # Step 6: Create sample reviews (so users have activity)
            create_sample_reviews()
            
            # Step 7: Calculate similarities (now users have data)
            calculate_user_similarities()
            
            print("\nFull initialization completed!")
        else:
            print("Import failed, but starting server anyway...")
    
    # Step 8: Initialize badges if needed
    print("\n" + "=" * 60)
    if check_if_badges_exist():
        print("✅ Badges already initialized - skipping")
    else:
        print("🏅 Badges not found - initializing...")
        if initialize_badges():
            print("✅ Badge system ready!")
        else:
            print("⚠️  Badge initialization failed - continuing without badges")
    
    # Step 9: Start Django server
    print("=" * 60)
    print("✨ Initialization complete! Starting server...\n")
    start_django_server()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)