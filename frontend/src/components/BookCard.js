import React from 'react';
import { Link } from 'react-router-dom';

const BookCard = ({ book }) => {
  // BEZPIECZNE SPRAWDZENIE BOOK OBJECT
  if (!book) {
    return (
      <div className="book-card error">
        <p>Book data not available</p>
      </div>
    );
  }

  // BEZPIECZNE WARTOŚCI Z FALLBACKAMI
  const {
    id = 'unknown',
    title = 'Unknown Title',
    authors = 'Unknown Author',
    price = null,
    publish_year = null,
    average_rating = 0,
    ratings_count = 0,
    description = '',
    cover_image_url = null,
    isbn = null
  } = book;

  // FORMATOWANIE DANYCH
  const displayPrice = price ? `$${price}` : 'Price not available';
  const displayYear = publish_year ? ` (${publish_year})` : '';
  const displayRating = average_rating ? Number(average_rating).toFixed(1) : 'No rating';
  const displayAuthors = Array.isArray(authors) ? authors.join(', ') : authors;
  const shortDescription = description && description.length > 100 
    ? description.substring(0, 100) + '...' 
    : description;

  return (
    <div className="book-card">
      <Link to={`/book/${id}`} className="book-link">
        {/* Book Cover */}
        <div className="book-cover">
          {cover_image_url ? (
            <img 
              src={cover_image_url} 
              alt={`Cover of ${title}`}
              onError={(e) => {
                e.target.style.display = 'none';
                e.target.nextSibling.style.display = 'flex';
              }}
            />
          ) : null}
          <div 
            className="cover-placeholder" 
            style={{ display: cover_image_url ? 'none' : 'flex' }}
          >
            <span>📚</span>
          </div>
        </div>

        {/* Book Info */}
        <div className="book-info">
          <h3 className="book-title">{title}{displayYear}</h3>
          <p className="book-author">{displayAuthors}</p>
          
          {shortDescription && (
            <p className="book-description">{shortDescription}</p>
          )}

          <div className="book-meta">
            <div className="book-rating">
              <span className="rating-stars">⭐</span>
              <span>{displayRating}</span>
              {ratings_count > 0 && (
                <span className="rating-count">({ratings_count})</span>
              )}
            </div>
            
            <div className="book-price">
              {displayPrice}
            </div>
          </div>

          {isbn && (
            <div className="book-isbn">
              ISBN: {isbn}
            </div>
          )}
        </div>
      </Link>
    </div>
  );
};

export default BookCard;