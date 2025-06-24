import pandas as pd
import nltk
import re
from collections import Counter
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

def ensure_nltk_data():
    """Ensure NLTK data is downloaded"""
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('corpora/stopwords')
    except LookupError:
        print("📥 Downloading NLTK data...")
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        print("✅ NLTK data downloaded successfully")

def clean_author_name(author):
    """Clean and normalize author names"""
    if pd.isna(author) or not author:
        return None
    
    author = str(author).strip()
    
    # Remove "By " prefix if present
    if author.startswith("By "):
        author = author[3:].strip()
    
    # Remove extra whitespace
    author = re.sub(r'\s+', ' ', author)
    
    return author if author else None

def parse_author_name(author_string):
    """
    Parse author name into first and last name
    Handles formats like "Last, First" or "First Last"
    """
    if not author_string:
        return None, None
    
    # Handle "Last, First" format
    if ',' in author_string:
        parts = [part.strip() for part in author_string.split(',', 1)]
        if len(parts) == 2 and parts[0] and parts[1]:
            return parts[1], parts[0]  # first_name, last_name
        else:
            return '', parts[0]  # No first name, just last name
    
    # Handle "First Last" or "First Middle Last" format
    parts = author_string.strip().split()
    if len(parts) >= 2:
        first_name = ' '.join(parts[:-1])  # Everything except last word
        last_name = parts[-1]  # Last word
        return first_name, last_name
    elif len(parts) == 1:
        return '', parts[0]  # Single name goes to last_name
    
    return None, None

def clean_category(category):
    """Clean and normalize category names"""
    if pd.isna(category) or not category:
        return None
    
    category = str(category).strip()
    
    # Remove extra whitespace
    category = re.sub(r'\s+', ' ', category)
    
    # Skip generic categories
    if category.lower() in ['general', 'misc', 'miscellaneous', '']:
        return None
    
    return category if category else None

def extract_keywords(text, top_n=5):
    """
    Extract keywords from text using NLTK
    Improved version with better filtering
    """
    if pd.isna(text) or not text:
        return ""
    
    try:
        ensure_nltk_data()
        
        text = str(text).lower()
        
        # Remove special characters and numbers
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Tokenize
        words = word_tokenize(text)
        
        # Get English stopwords
        stop_words = set(stopwords.words('english'))
        
        # Add custom stopwords for book descriptions
        custom_stopwords = {
            'book', 'novel', 'story', 'author', 'writer', 'tale', 'narrative',
            'chapter', 'page', 'read', 'reading', 'written', 'write', 'tells',
            'follows', 'chronicles', 'explores', 'examines', 'describes'
        }
        stop_words.update(custom_stopwords)
        
        # Filter words
        keywords = [
            word for word in words 
            if (
                word.isalpha() and 
                len(word) > 2 and 
                word not in stop_words and
                len(word) < 15  # Avoid very long words
            )
        ]
        
        # Count and get most common
        most_common = Counter(keywords).most_common(top_n)
        
        # Return as comma-separated string
        return ", ".join([keyword.capitalize() for keyword, count in most_common])
        
    except Exception as e:
        print(f"⚠️  Error extracting keywords: {e}")
        return ""

def clean_price(price_string):
    """Clean and extract price value"""
    if pd.isna(price_string) or not price_string:
        return None
    
    try:
        # Convert to string and clean
        price_str = str(price_string).strip()
        
        # Remove currency symbols and commas
        price_str = re.sub(r'[$£€¥,]', '', price_str)
        
        # Extract first number found
        match = re.search(r'(\d+\.?\d*)', price_str)
        if match:
            return float(match.group(1))
    
    except (ValueError, TypeError):
        pass
    
    return None

def clean_year(year_value):
    """Clean and validate publication year"""
    if pd.isna(year_value) or not year_value:
        return None
    
    try:
        year = int(year_value)
        # Reasonable range for publication years
        if 1000 <= year <= 2030:
            return year
    except (ValueError, TypeError):
        pass
    
    return None

def preprocess_books_dataset(input_file, output_file):
    """
    Preprocess the books dataset for normalized schema
    Expected CSV columns: Title, Authors, Description, Category, Publisher, Price Starting With ($), Publish Date (Month), Publish Date (Year)
    """
    
    print(f"🔄 Starting preprocessing of {input_file}")
    print("=" * 60)
    
    try:
        # Load the dataset
        print("📥 Loading dataset...")
        df = pd.read_csv(input_file)
        
        print(f"📊 Loaded {len(df)} records")
        print(f"📋 Columns: {list(df.columns)}")
        
        # Initialize preprocessing statistics
        stats = {
            'original_rows': len(df),
            'processed_rows': 0,
            'authors_processed': 0,
            'categories_processed': 0,
            'keywords_extracted': 0,
            'errors': []
        }
        
        # Process each column
        print("\n🔧 Processing columns...")
        
        # 1. Clean title
        print("   📖 Processing titles...")
        df['Title'] = df['Title'].astype(str).str.strip()
        df = df[df['Title'].notna() & (df['Title'] != '') & (df['Title'] != 'nan')]
        
        # 2. Process authors
        print("   👤 Processing authors...")
        df['Authors_Clean'] = df['Authors'].apply(clean_author_name)
        
        # Split authors into first and last names
        author_names = df['Authors_Clean'].apply(
            lambda x: parse_author_name(x) if x else (None, None)
        )
        df['Author_First_Name'] = author_names.apply(lambda x: x[0] if x[0] else '')
        df['Author_Last_Name'] = author_names.apply(lambda x: x[1] if x[1] else '')
        
        stats['authors_processed'] = df['Authors_Clean'].notna().sum()
        
        # 3. Process categories
        print("   📂 Processing categories...")
        df['Category_Clean'] = df['Category'].apply(clean_category)
        stats['categories_processed'] = df['Category_Clean'].notna().sum()
        
        # 4. Extract keywords from description
        print("   🔍 Extracting keywords from descriptions...")
        df['Keywords'] = df['Description'].apply(extract_keywords)
        stats['keywords_extracted'] = (df['Keywords'] != '').sum()
        
        # 5. Clean publisher
        print("   🏢 Processing publishers...")
        df['Publisher_Clean'] = df['Publisher'].astype(str).str.strip()
        df['Publisher_Clean'] = df['Publisher_Clean'].replace(['nan', ''], None)
        
        # 6. Clean price
        print("   💰 Processing prices...")
        df['Price_Clean'] = df['Price Starting With ($)'].apply(clean_price)
        
        # 7. Clean publication year
        print("   📅 Processing publication years...")
        df['Publish_Year_Clean'] = df['Publish Date (Year)'].apply(clean_year)
        
        # 8. Clean publication month
        print("   📅 Processing publication months...")
        df['Publish_Month_Clean'] = df['Publish Date (Month)'].astype(str).str.strip()
        df['Publish_Month_Clean'] = df['Publish_Month_Clean'].replace(['nan', ''], None)
        
        # 9. Remove rows without essential data
        print("   🧹 Filtering out incomplete records...")
        initial_count = len(df)
        
        # Keep only rows with title and at least one of: author or description
        df = df[
            (df['Title'].notna()) & 
            (df['Title'] != '') &
            (
                (df['Authors_Clean'].notna()) | 
                (df['Description'].notna() & (df['Description'] != ''))
            )
        ]
        
        removed_count = initial_count - len(df)
        print(f"      🗑️  Removed {removed_count} incomplete records")
        
        # 10. Create final cleaned dataset
        print("   ✨ Creating final dataset...")
        
        final_columns = [
            'Title',
            'Authors_Clean',
            'Author_First_Name', 
            'Author_Last_Name',
            'Description',
            'Keywords',
            'Category_Clean',
            'Publisher_Clean',
            'Price_Clean',
            'Publish_Month_Clean',
            'Publish_Year_Clean'
        ]
        
        df_final = df[final_columns].copy()
        
        # Rename columns for clarity
        df_final.columns = [
            'Title',
            'Authors',
            'Author_First_Name',
            'Author_Last_Name', 
            'Description',
            'Keywords',
            'Category',
            'Publisher',
            'Price',
            'Publish_Month',
            'Publish_Year'
        ]
        
        stats['processed_rows'] = len(df_final)
        
        # 11. Save processed dataset
        print(f"💾 Saving processed dataset to {output_file}...")
        df_final.to_csv(output_file, index=False, encoding='utf-8')
        
        # 12. Print summary statistics
        print("\n" + "=" * 60)
        print("📊 PREPROCESSING SUMMARY:")
        print(f"📥 Original rows: {stats['original_rows']}")
        print(f"📤 Processed rows: {stats['processed_rows']}")
        print(f"🗑️  Removed rows: {stats['original_rows'] - stats['processed_rows']}")
        print(f"👤 Authors processed: {stats['authors_processed']}")
        print(f"📂 Categories processed: {stats['categories_processed']}")
        print(f"🔍 Keywords extracted: {stats['keywords_extracted']}")
        
        # Additional statistics
        print(f"\n📈 DATA QUALITY METRICS:")
        print(f"   Titles: {df_final['Title'].notna().sum()}/{len(df_final)} ({df_final['Title'].notna().sum()/len(df_final)*100:.1f}%)")
        print(f"   Authors: {df_final['Authors'].notna().sum()}/{len(df_final)} ({df_final['Authors'].notna().sum()/len(df_final)*100:.1f}%)")
        print(f"   Descriptions: {df_final['Description'].notna().sum()}/{len(df_final)} ({df_final['Description'].notna().sum()/len(df_final)*100:.1f}%)")
        print(f"   Categories: {df_final['Category'].notna().sum()}/{len(df_final)} ({df_final['Category'].notna().sum()/len(df_final)*100:.1f}%)")
        print(f"   Publishers: {df_final['Publisher'].notna().sum()}/{len(df_final)} ({df_final['Publisher'].notna().sum()/len(df_final)*100:.1f}%)")
        print(f"   Years: {df_final['Publish_Year'].notna().sum()}/{len(df_final)} ({df_final['Publish_Year'].notna().sum()/len(df_final)*100:.1f}%)")
        print(f"   Prices: {df_final['Price'].notna().sum()}/{len(df_final)} ({df_final['Price'].notna().sum()/len(df_final)*100:.1f}%)")
        
        # Show sample data
        print(f"\n📋 SAMPLE PROCESSED DATA:")
        print(df_final.head(3).to_string())
        
        print(f"\n✅ Preprocessing completed successfully!")
        print(f"📁 Clean dataset saved as: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"💥 Critical error during preprocessing: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main preprocessing function"""
    
    import os
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    input_files = [
        'BooksDatasetClean.csv',  # Current directory
        'data/BooksDatasetClean.csv',  # Relative to current directory
        os.path.join(script_dir, 'BooksDatasetClean.csv'),  # Same dir as script
        os.path.join(script_dir, 'data', 'BooksDatasetClean.csv'),  # data subdir relative to script
        '/data/BooksDatasetClean.csv',  # Docker volume mount
        'database/data/BooksDatasetClean.csv',  # Relative to project root
        os.path.join(os.path.dirname(script_dir), 'database', 'data', 'BooksDatasetClean.csv'),  # Full relative path
    ]
    
    output_file = os.path.join(script_dir, 'BooksDatasetProcessed.csv')
    
    # Find input file
    input_file = None
    for file_path in input_files:
        try:
            with open(file_path, 'r'):
                input_file = file_path
                break
        except FileNotFoundError:
            continue
    
    if not input_file:
        print("❌ Input file not found. Checked paths:")
        for path in input_files:
            print(f"   - {path}")
        return False
    
    # Run preprocessing
    success = preprocess_books_dataset(input_file, output_file)
    
    if success:
        print(f"\n🎉 Preprocessing completed successfully!")
        print(f"📁 Output file: {output_file}")
        print(f"🚀 Ready for import with normalized_data_import.py")
    else:
        print(f"\n❌ Preprocessing failed!")
        return False
    
    return True

if __name__ == "__main__":
    main()