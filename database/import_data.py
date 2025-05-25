#!/bin/bash
# database/download_data.sh

set -e

DATA_DIR="/data"
BOOK_CROSSING_URL="http://www2.informatik.uni-freiburg.de/~cziegler/BX/BX-CSV-Dump.zip"

echo "Downloading Book-Crossing dataset..."

# Sprawdź czy dane już istnieją
if [ -f "$DATA_DIR/Books.csv" ] && [ -f "$DATA_DIR/Users.csv" ] && [ -f "$DATA_DIR/Ratings.csv" ]; then
    echo "Book-Crossing data already exists, skipping download."
    exit 0
fi

# Utwórz katalog jeśli nie istnieje
mkdir -p "$DATA_DIR"

# Pobierz i rozpakuj dane
cd "$DATA_DIR"
wget -O book-crossing.zip "$BOOK_CROSSING_URL"
unzip -o book-crossing.zip
rm book-crossing.zip

echo "Book-Crossing dataset downloaded and extracted to $DATA_DIR"

# Sprawdź czy pliki zostały pobrane
if [ ! -f "BX-Books.csv" ] || [ ! -f "BX-Users.csv" ] || [ ! -f "BX-Book-Ratings.csv" ]; then
    echo "Error: Required CSV files not found after extraction"
    exit 1
fi

echo "All required files are present"