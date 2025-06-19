#!/bin/bash

set -e

DATA_DIR="/data"

echo "Preparing Book-Crossing dataset..."

# Sprawdź czy dane już istnieją
if [ -f "$DATA_DIR/Books.csv" ] && [ -f "$DATA_DIR/Users.csv" ] && [ -f "$DATA_DIR/Ratings.csv" ]; then
    echo "All CSV files already exist, skipping preparation."
    ls -la "$DATA_DIR"
    exit 0
fi

# Utwórz katalog jeśli nie istnieje
mkdir -p "$DATA_DIR"
cd "$DATA_DIR"

echo "Files in data directory before processing:"
ls -la "$DATA_DIR" || echo "Directory is empty"

# Sprawdź czy istnieją jakiekolwiek pliki CSV i spróbuj je wykorzystać
if [ -f "Books.csv" ] || [ -f "BX-Books.csv" ]; then
    echo "Found existing books file, using it..."
    
    # Standaryzuj nazwy plików
    [ -f "BX-Books.csv" ] && [ ! -f "Books.csv" ] && mv "BX-Books.csv" "Books.csv"
    [ -f "BX-Users.csv" ] && [ ! -f "Users.csv" ] && mv "BX-Users.csv" "Users.csv"
    [ -f "BX-Book-Ratings.csv" ] && [ ! -f "Ratings.csv" ] && mv "BX-Book-Ratings.csv" "Ratings.csv"
    
else
    # Utwórz przykładowe dane jeśli nie ma żadnych plików
    echo "No existing files found, creating sample data..."
    
    # Utwórz Books.csv z przykładowymi danymi
    cat > Books.csv << 'EOF'
ISBN;Book-Title;Book-Author;Year-Of-Publication;Publisher;Image-URL-S;Image-URL-M;Image-URL-L
9780141439518;Pride and Prejudice;Jane Austen;1813;Penguin Classics;http://images.amazon.com/images/P/0141439513.01.THUMBZZZ.jpg;http://images.amazon.com/images/P/0141439513.01.MZZZZZZZ.jpg;http://images.amazon.com/images/P/0141439513.01.L.jpg
9780061120084;To Kill a Mockingbird;Harper Lee;1960;Harper Perennial;http://images.amazon.com/images/P/0061120081.01.THUMBZZZ.jpg;http://images.amazon.com/images/P/0061120081.01.MZZZZZZZ.jpg;http://images.amazon.com/images/P/0061120081.01.L.jpg
9780451524935;1984;George Orwell;1949;Signet Classics;http://images.amazon.com/images/P/0451524934.01.THUMBZZZ.jpg;http://images.amazon.com/images/P/0451524934.01.MZZZZZZZ.jpg;http://images.amazon.com/images/P/0451524934.01.L.jpg
9780141182636;Great Expectations;Charles Dickens;1861;Penguin Classics;http://images.amazon.com/images/P/0141182637.01.THUMBZZZ.jpg;http://images.amazon.com/images/P/0141182637.01.MZZZZZZZ.jpg;http://images.amazon.com/images/P/0141182637.01.L.jpg
9780547928227;The Hobbit;J.R.R. Tolkien;1937;Houghton Mifflin;http://images.amazon.com/images/P/0547928220.01.THUMBZZZ.jpg;http://images.amazon.com/images/P/0547928220.01.MZZZZZZZ.jpg;http://images.amazon.com/images/P/0547928220.01.L.jpg
9780439708180;Harry Potter and the Sorcerer's Stone;J.K. Rowling;1997;Scholastic;http://images.amazon.com/images/P/0439708184.01.THUMBZZZ.jpg;http://images.amazon.com/images/P/0439708184.01.MZZZZZZZ.jpg;http://images.amazon.com/images/P/0439708184.01.L.jpg
9780316769488;The Catcher in the Rye;J.D. Salinger;1951;Little Brown;http://images.amazon.com/images/P/0316769487.01.THUMBZZZ.jpg;http://images.amazon.com/images/P/0316769487.01.MZZZZZZZ.jpg;http://images.amazon.com/images/P/0316769487.01.L.jpg
9780743273565;The Great Gatsby;F. Scott Fitzgerald;1925;Scribner;http://images.amazon.com/images/P/0743273567.01.THUMBZZZ.jpg;http://images.amazon.com/images/P/0743273567.01.MZZZZZZZ.jpg;http://images.amazon.com/images/P/0743273567.01.L.jpg
9780452284234;One Hundred Years of Solitude;Gabriel Garcia Marquez;1967;Penguin Books;http://images.amazon.com/images/P/0452284236.01.THUMBZZZ.jpg;http://images.amazon.com/images/P/0452284236.01.MZZZZZZZ.jpg;http://images.amazon.com/images/P/0452284236.01.L.jpg
9780140449136;Crime and Punishment;Fyodor Dostoevsky;1866;Penguin Classics;http://images.amazon.com/images/P/0140449132.01.THUMBZZZ.jpg;http://images.amazon.com/images/P/0140449132.01.MZZZZZZZ.jpg;http://images.amazon.com/images/P/0140449132.01.L.jpg
EOF

    # Utwórz Users.csv z przykładowymi danymi
    cat > Users.csv << 'EOF'
User-ID;Location;Age
1;New York, NY, USA;25
2;London, England, UK;30
3;Toronto, ON, Canada;22
4;Sydney, NSW, Australia;28
5;Berlin, Germany;35
6;Paris, France;29
7;Tokyo, Japan;26
8;São Paulo, Brazil;31
9;Mumbai, India;24
10;Cairo, Egypt;33
EOF

    # Utwórz Ratings.csv z przykładowymi danymi
    cat > Ratings.csv << 'EOF'
User-ID;ISBN;Book-Rating
1;9780141439518;8
2;9780061120084;9
3;9780451524935;7
4;9780141182636;6
5;9780547928227;10
6;9780439708180;9
7;9780316769488;5
8;9780743273565;8
9;9780452284234;7
10;9780140449136;6
1;9780061120084;7
2;9780451524935;8
3;9780547928227;9
4;9780439708180;8
5;9780316769488;4
EOF

    echo "Sample data created successfully"
fi

echo "Final file list:"
ls -la "$DATA_DIR"

# Sprawdź czy wszystkie wymagane pliki istnieją
if [ ! -f "Books.csv" ] || [ ! -f "Users.csv" ] || [ ! -f "Ratings.csv" ]; then
    echo "Error: Required CSV files not found after processing"
    echo "Available files:"
    ls -la
    exit 1
fi

echo "All required files are present and ready for import"

# Pokaż pierwsze linie każdego pliku dla weryfikacji
echo "First few lines of Books.csv:"
head -3 Books.csv

echo "First few lines of Users.csv:"
head -3 Users.csv

echo "First few lines of Ratings.csv:"
head -3 Ratings.csv