-- Książki - wzbogacone o dane z Open Library API
CREATE TABLE IF NOT EXISTS books (
    id BIGSERIAL PRIMARY KEY,
    isbn VARCHAR(20) UNIQUE,
    title VARCHAR(500) NOT NULL,
    author VARCHAR(300),
    publisher VARCHAR(200),
    publication_year INTEGER,
    image_url_s VARCHAR(500),
    image_url_m VARCHAR(500),
    image_url_l VARCHAR(500),
    
    -- Dane z Open Library API
    description TEXT,
    categories TEXT[],
    page_count INTEGER,
    language VARCHAR(10) DEFAULT 'en',
    average_rating DECIMAL(3,2),
    ratings_count INTEGER DEFAULT 0,
    open_library_id VARCHAR(100),
    
    -- Metadane
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- UJEDNOLICONA tabela użytkowników (historyczni + nowi)
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    
    -- Dla użytkowników z datasetu
    original_user_id INTEGER UNIQUE, -- ID z Book-Crossing (tylko dla historycznych)
    
    -- Dla użytkowników aplikacji
    username VARCHAR(50) UNIQUE,     -- tylko dla nowych użytkowników
    email VARCHAR(100) UNIQUE,       -- tylko dla nowych użytkowników  
    password_hash VARCHAR(255),      -- tylko dla nowych użytkowników
    
    -- Wspólne dane
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    age INTEGER,
    city VARCHAR(100),
    state VARCHAR(100), 
    country VARCHAR(100),
    
    -- Typ użytkownika
    user_type VARCHAR(20) CHECK (user_type IN ('dataset', 'app')) NOT NULL,
    
    -- Metadane
    preferences JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

-- UJEDNOLICONA tabela ocen (wszystkie oceny w jednym miejscu)
CREATE TABLE IF NOT EXISTS ratings (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    book_id INTEGER REFERENCES books(id) ON DELETE CASCADE,
    
    -- Znormalizowana ocena (zawsze 1-5)
    rating DECIMAL(2,1) CHECK (rating >= 1.0 AND rating <= 5.0),
    
    -- Oryginalna ocena (dla historii)
    original_rating INTEGER,           -- Oryginalna wartość z datasetu (0-10)
    rating_scale VARCHAR(10),          -- '0-10' lub '1-5'
    
    -- Typ źródła oceny
    source_type VARCHAR(20) CHECK (source_type IN ('dataset', 'app')) NOT NULL,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, book_id)
);

-- Recenzje użytkowników aplikacji (tylko nowi użytkownicy mogą pisać recenzje)
CREATE TABLE IF NOT EXISTS reviews (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    book_id INTEGER REFERENCES books(id) ON DELETE CASCADE,
    title VARCHAR(200),
    content TEXT NOT NULL,
    helpful_votes INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, book_id)
);

-- Lista życzeń/do przeczytania
CREATE TABLE IF NOT EXISTS reading_lists (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    book_id INTEGER REFERENCES books(id) ON DELETE CASCADE,
    list_type VARCHAR(20) CHECK (list_type IN ('want_to_read', 'currently_reading', 'read')),
    added_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, book_id, list_type)
);

-- Rekomendacje (cache)
CREATE TABLE IF NOT EXISTS recommendations (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    book_id INTEGER REFERENCES books(id) ON DELETE CASCADE,
    recommendation_type VARCHAR(20) CHECK (recommendation_type IN ('collaborative', 'content_based', 'hybrid')),
    score DECIMAL(5,4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indeksy dla wydajności
CREATE INDEX IF NOT EXISTS idx_books_author ON books(author);
CREATE INDEX IF NOT EXISTS idx_books_title ON books(title);
CREATE INDEX IF NOT EXISTS idx_books_isbn ON books(isbn);
CREATE INDEX IF NOT EXISTS idx_books_open_library_id ON books(open_library_id);
CREATE INDEX IF NOT EXISTS idx_books_categories ON books USING GIN(categories);

CREATE INDEX IF NOT EXISTS idx_users_type ON users(user_type);
CREATE INDEX IF NOT EXISTS idx_users_original_id ON users(original_user_id);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

CREATE INDEX IF NOT EXISTS idx_ratings_user ON ratings(user_id);
CREATE INDEX IF NOT EXISTS idx_ratings_book ON ratings(book_id);
CREATE INDEX IF NOT EXISTS idx_ratings_source ON ratings(source_type);
CREATE INDEX IF NOT EXISTS idx_ratings_user_book ON ratings(user_id, book_id);

CREATE INDEX IF NOT EXISTS idx_reviews_book ON reviews(book_id);
CREATE INDEX IF NOT EXISTS idx_reviews_user ON reviews(user_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_user_score ON recommendations(user_id, score DESC);

-- Indeksy pełnotekstowe
CREATE INDEX IF NOT EXISTS idx_books_title_gin ON books USING GIN(to_tsvector('english', title));
CREATE INDEX IF NOT EXISTS idx_books_description_gin ON books USING GIN(to_tsvector('english', description));

-- Funkcja do automatycznego update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggery dla auto-update timestamps
DROP TRIGGER IF EXISTS update_books_updated_at ON books;
CREATE TRIGGER update_books_updated_at BEFORE UPDATE ON books
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_reviews_updated_at ON reviews;
CREATE TRIGGER update_reviews_updated_at BEFORE UPDATE ON reviews
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Funkcja do konwersji ocen z 0-10 na 1-5
CREATE OR REPLACE FUNCTION normalize_rating(original_rating INTEGER, from_scale VARCHAR DEFAULT '0-10')
RETURNS DECIMAL(2,1) AS $$
BEGIN
    IF from_scale = '0-10' THEN
        -- Konwertuj z 0-10 na 1-5
        IF original_rating = 0 THEN
            RETURN 1.0;  -- 0 w starym systemie = 1 w nowym (najgorsza ocena)
        ELSE
            RETURN ROUND((original_rating::DECIMAL / 2.0) + 0.5, 1);
        END IF;
    ELSE
        -- Już jest w skali 1-5
        RETURN original_rating::DECIMAL;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Funkcje pomocnicze dla Open Library
CREATE OR REPLACE FUNCTION get_open_library_cover_url(isbn_param VARCHAR, size_param VARCHAR DEFAULT 'M')
RETURNS VARCHAR AS $$
BEGIN
    IF isbn_param IS NULL OR isbn_param = '' THEN
        RETURN NULL;
    END IF;
    
    isbn_param := REPLACE(REPLACE(isbn_param, '-', ''), ' ', '');
    RETURN 'https://covers.openlibrary.org/b/isbn/' || isbn_param || '-' || size_param || '.jpg';
END;
$$ LANGUAGE plpgsql;

-- Widoki pomocnicze
CREATE OR REPLACE VIEW books_with_covers AS
SELECT 
    b.*,
    get_open_library_cover_url(b.isbn, 'S') AS ol_cover_small,
    get_open_library_cover_url(b.isbn, 'M') AS ol_cover_medium,
    get_open_library_cover_url(b.isbn, 'L') AS ol_cover_large,
    CASE 
        WHEN b.open_library_id IS NOT NULL THEN 'https://openlibrary.org' || b.open_library_id
        WHEN b.isbn IS NOT NULL THEN 'https://openlibrary.org/isbn/' || REPLACE(REPLACE(b.isbn, '-', ''), ' ', '')
        ELSE NULL
    END AS open_library_url
FROM books b;

-- Widok wszystkich ocen z informacjami o użytkownikach
CREATE OR REPLACE VIEW ratings_with_users AS
SELECT 
    r.*,
    u.user_type,
    u.username,
    u.original_user_id,
    u.age,
    u.city,
    u.country,
    b.title,
    b.author,
    b.isbn
FROM ratings r
JOIN users u ON r.user_id = u.id
JOIN books b ON r.book_id = b.id;

-- Wstaw przykładowe dane jeśli tabela jest pusta
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM books LIMIT 1) THEN
        INSERT INTO books (isbn, title, author, publisher, publication_year, description, categories, language, average_rating, ratings_count) VALUES
        ('9780141439518', 'Pride and Prejudice', 'Jane Austen', 'Penguin Classics', 1813, 'A classic romance novel', ARRAY['Fiction', 'Romance', 'Classic'], 'en', 4.25, 1500),
        ('9780061120084', 'To Kill a Mockingbird', 'Harper Lee', 'Harper Perennial', 1960, 'A gripping tale of racial injustice and childhood innocence', ARRAY['Fiction', 'Classic', 'Coming of Age'], 'en', 4.42, 2100),
        ('9780451524935', '1984', 'George Orwell', 'Signet Classics', 1949, 'A dystopian social science fiction novel', ARRAY['Fiction', 'Dystopian', 'Science Fiction'], 'en', 4.19, 1800),
        ('9780547928227', 'The Hobbit', 'J.R.R. Tolkien', 'Houghton Mifflin', 1937, 'A fantasy adventure about a hobbit on an unexpected journey', ARRAY['Fantasy', 'Adventure', 'Classic'], 'en', 4.27, 1650),
        ('9780439708180', 'Harry Potter and the Sorcerer''s Stone', 'J.K. Rowling', 'Scholastic', 1997, 'The first book in the magical Harry Potter series', ARRAY['Fantasy', 'Young Adult', 'Magic'], 'en', 4.47, 2500);
        
        RAISE NOTICE 'Inserted sample books with Open Library integration';
    END IF;
END
$$;