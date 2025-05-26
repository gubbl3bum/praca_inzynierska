#!/bin/bash

set -e

DATA_DIR="/data"
BOOK_CROSSING_URL="http://www2.informatik.uni-freiburg.de/~cziegler/BX/BX-CSV-Dump.zip"

echo "Downloading Book-Crossing dataset..."

# Sprawdź czy dane już istnieją (oba warianty nazw)
if [ -f "$DATA_DIR/Books.csv" ] || [ -f "$DATA_DIR/BX-Books.csv" ]; then
    echo "Book-Crossing data already exists, skipping download."
    ls -la "$DATA_DIR"
    exit 0
fi

# Utwórz katalog jeśli nie istnieje
mkdir -p "$DATA_DIR"

# Pobierz i rozpakuj dane
cd "$DATA_DIR"
echo "Downloading from $BOOK_CROSSING_URL..."
wget -O book-crossing.zip "$BOOK_CROSSING_URL"

echo "Extracting archive..."
unzip -o book-crossing.zip

# Usuń archiwum
rm book-crossing.zip

echo "Files after extraction:"
ls -la "$DATA_DIR"

# Sprawdź jakie pliki zostały utworzone i ewentualnie zmień nazwy
if [ -f "BX-Books.csv" ] && [ ! -f "Books.csv" ]; then
    echo "Renaming BX-Books.csv to Books.csv"
    mv "BX-Books.csv" "Books.csv"
fi

if [ -f "BX-Users.csv" ] && [ ! -f "Users.csv" ]; then
    echo "Renaming BX-Users.csv to Users.csv"  
    mv "BX-Users.csv" "Users.csv"
fi

if [ -f "BX-Book-Ratings.csv" ] && [ ! -f "Ratings.csv" ]; then
    echo "Renaming BX-Book-Ratings.csv to Ratings.csv"
    mv "BX-Book-Ratings.csv" "Ratings.csv"
fi

echo "Final file list:"
ls -la "$DATA_DIR"

# Sprawdź czy wszystkie wymagane pliki istnieją
if [ ! -f "Books.csv" ] || [ ! -f "Users.csv" ] || [ ! -f "Ratings.csv" ]; then
    echo "Error: Required CSV files not found after extraction and renaming"
    echo "Available files:"
    ls -la
    exit 1
fi

echo "All required files are present and properly named"