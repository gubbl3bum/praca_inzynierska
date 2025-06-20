-- Książki 
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    isbn VARCHAR(20) UNIQUE,
    title VARCHAR(500),
    author VARCHAR(300),
    publisher VARCHAR(200),
    publication_year INTEGER,
    image_url_s VARCHAR(500),
    image_url_m VARCHAR(500),
    image_url_l VARCHAR(500),
    
    -- Dane z Google Books API
    description TEXT,
    categories TEXT[], -- PostgreSQL array lub JSON dla innych DB
    page_count INTEGER,
    language VARCHAR(10),
    average_rating DECIMAL(3,2),
    ratings_count INTEGER,
    google_books_id VARCHAR(50),
    
    -- Metadane
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Użytkownicy z datasetu (historyczne dane)
CREATE TABLE dataset_users (
    id SERIAL PRIMARY KEY,
    original_user_id INTEGER UNIQUE, -- ID z Book-Crossing
    age INTEGER,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Użytkownicy aplikacji (nowi użytkownicy)
CREATE TABLE app_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    age INTEGER,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    preferences JSONB, -- preferencje gatunków, autorów itp.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Oceny z datasetu (historyczne)
CREATE TABLE dataset_ratings (
    id SERIAL PRIMARY KEY,
    dataset_user_id INTEGER REFERENCES dataset_users(id),
    book_id INTEGER REFERENCES books(id),
    rating INTEGER CHECK (rating >= 0 AND rating <= 10), -- 0 = implicit feedback
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Oceny od użytkowników aplikacji
CREATE TABLE app_ratings (
    id SERIAL PRIMARY KEY,
    app_user_id INTEGER REFERENCES app_users(id),
    book_id INTEGER REFERENCES books(id),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(app_user_id, book_id)
);

-- Recenzje użytkowników aplikacji
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    app_user_id INTEGER REFERENCES app_users(id),
    book_id INTEGER REFERENCES books(id),
    title VARCHAR(200),
    content TEXT NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    helpful_votes INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(app_user_id, book_id)
);

-- Lista życzeń/do przeczytania
CREATE TABLE reading_lists (
    id SERIAL PRIMARY KEY,
    app_user_id INTEGER REFERENCES app_users(id),
    book_id INTEGER REFERENCES books(id),
    list_type VARCHAR(20) CHECK (list_type IN ('want_to_read', 'currently_reading', 'read')),
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(app_user_id, book_id, list_type)
);

-- Rekomendacje (cache)
CREATE TABLE recommendations (
    id SERIAL PRIMARY KEY,
    app_user_id INTEGER REFERENCES app_users(id),
    book_id INTEGER REFERENCES books(id),
    recommendation_type VARCHAR(20) CHECK (recommendation_type IN ('collaborative', 'content_based', 'hybrid')),
    score DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indeksy dla wydajności
CREATE INDEX idx_books_author ON books(author);
CREATE INDEX idx_books_categories ON books USING GIN(categories);
CREATE INDEX idx_dataset_ratings_user ON dataset_ratings(dataset_user_id);
CREATE INDEX idx_dataset_ratings_book ON dataset_ratings(book_id);
CREATE INDEX idx_app_ratings_user ON app_ratings(app_user_id);
CREATE INDEX idx_app_ratings_book ON app_ratings(book_id);
CREATE INDEX idx_reviews_book ON reviews(book_id);
CREATE INDEX idx_reviews_user ON reviews(app_user_id);

-- Dodatkowe indeksy specyficzne dla PostgreSQL
CREATE INDEX idx_recommendations_user_score ON recommendations(app_user_id, score DESC);
CREATE INDEX idx_books_title_gin ON books USING GIN(to_tsvector('english', title));
CREATE INDEX idx_books_description_gin ON books USING GIN(to_tsvector('english', description));

-- Funkcja do automatycznego update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$ language 'plpgsql';

-- Triggery dla auto-update timestamps
CREATE TRIGGER update_books_updated_at BEFORE UPDATE ON books
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reviews_updated_at BEFORE UPDATE ON reviews
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();