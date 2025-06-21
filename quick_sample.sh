#!/bin/bash
# quick_sample.sh - Szybkie utworzenie próbek i restart importu

echo "🎯 TWORZENIE PRÓBEK DANYCH I RESTART"
echo "======================================"

# 1. Zatrzymaj obecny import
echo "⏹️  Zatrzymuję data-importer..."
docker-compose kill data-importer

# 2. Utwórz próbki danych
echo "📊 Tworzę próbki danych..."
docker-compose run --rm data-importer python -c "
import pandas as pd
import os

print('📚 Tworzę próbkę 1000 książek...')
df = pd.read_csv('/data/Books.csv', sep=';', encoding='utf-8', nrows=1000)
df.to_csv('/data/Books_sample.csv', sep=';', encoding='utf-8', index=False)
print(f'✅ Zapisano {len(df)} książek do Books_sample.csv')

# Pobierz listę ISBN
valid_isbns = df['ISBN'].tolist() if 'ISBN' in df.columns else []

print('👥 Tworzę próbkę 5000 użytkowników...')
try:
    df_users = pd.read_csv('/data/Users.csv', sep=';', encoding='utf-8', nrows=5000)
    df_users.to_csv('/data/Users_sample.csv', sep=';', encoding='utf-8', index=False)
    print(f'✅ Zapisano {len(df_users)} użytkowników do Users_sample.csv')
    
    # Pobierz listę User-ID
    user_col = None
    for col in df_users.columns:
        if 'user' in col.lower() and 'id' in col.lower():
            user_col = col
            break
    valid_users = df_users[user_col].tolist() if user_col else []
    
except Exception as e:
    print(f'⚠️  Błąd z użytkownikami: {e}')
    valid_users = []

print('⭐ Filtruję oceny...')
try:
    # Wczytaj oceny po kawałkach i filtruj
    filtered_ratings = []
    chunk_count = 0
    
    for chunk in pd.read_csv('/data/Ratings.csv', sep=';', encoding='utf-8', chunksize=10000):
        chunk_count += 1
        
        # Znajdź kolumny
        isbn_col = rating_col = user_col = None
        for col in chunk.columns:
            if 'isbn' in col.lower(): isbn_col = col
            elif 'rating' in col.lower(): rating_col = col
            elif 'user' in col.lower() and 'id' in col.lower(): user_col = col
        
        if isbn_col and user_col:
            # Filtruj tylko książki i użytkowników z próbek
            chunk_filtered = chunk[
                chunk[isbn_col].isin(valid_isbns) & 
                chunk[user_col].isin(valid_users)
            ]
            
            if len(chunk_filtered) > 0:
                filtered_ratings.append(chunk_filtered)
            
            print(f'   Przetworzono chunk {chunk_count}, znaleziono {sum(len(c) for c in filtered_ratings)} ocen...')
            
            # Przerwij po 20k ocen
            if sum(len(c) for c in filtered_ratings) >= 20000:
                break
        
        # Przerwij po 100 chunkach (1M rekordów)
        if chunk_count >= 100:
            break
    
    if filtered_ratings:
        result_df = pd.concat(filtered_ratings, ignore_index=True)
        result_df.to_csv('/data/Ratings_sample.csv', sep=';', encoding='utf-8', index=False)
        print(f'✅ Zapisano {len(result_df)} ocen do Ratings_sample.csv')
    else:
        print('⚠️  Nie znaleziono pasujących ocen')
        
except Exception as e:
    print(f'⚠️  Błąd z ocenami: {e}')

print('🎉 Próbki gotowe!')
"

# 3. Przełącz na próbki (backup oryginałów)
echo "🔄 Przełączam na próbki danych..."
docker-compose exec data-importer sh -c "
cd /data
mv Books.csv Books_full.csv 2>/dev/null || true
mv Users.csv Users_full.csv 2>/dev/null || true  
mv Ratings.csv Ratings_full.csv 2>/dev/null || true

mv Books_sample.csv Books.csv 2>/dev/null || true
mv Users_sample.csv Users.csv 2>/dev/null || true
mv Ratings_sample.csv Ratings.csv 2>/dev/null || true

echo '📁 Obecne pliki:'
ls -lh *.csv
"

# 4. Wyczyść bazę
echo "🗑️  Czyszczę bazę danych..."
docker-compose exec db psql -U postgres -d book_recommendations -c "
TRUNCATE TABLE ratings, books_authors, books_categories, books, authors, publishers, categories, users RESTART IDENTITY CASCADE;
"

# 5. Uruchom import ponownie
echo "🚀 Uruchamiam import z próbkami..."
docker-compose up data-importer --no-deps

echo "✅ Import z próbkami uruchomiony!"
echo "📊 Sprawdź postęp: docker-compose logs -f data-importer"