import React from 'react';
import { useNavigate } from 'react-router-dom';

const BookCard = ({ book, onClick }) => {
  const navigate = useNavigate();

  // DEFENSIVE: Sprawdź czy book istnieje
  if (!book) {
    console.error('BookCard: book prop is undefined');
    return (
      <div className="bg-gray-200 rounded-xl h-96 flex items-center justify-center">
        <span className="text-gray-500">Brak danych książki</span>
      </div>
    );
  }

  // Użyj prawdziwego ratingu z bazy danych z fallback (0-10 scale)
  const rating = book.average_rating || 0;
  const ratingsCount = book.ratings_count || 0;
  
  // Debug: sprawdź co zawiera book
  console.log('BookCard book data:', book);
  
  // Funkcja do renderowania gwiazdek dla skali 0-10
  const renderStars = (rating) => {
    const stars = [];
    // Konwertuj ocenę 0-10 na skalę 0-5 gwiazdek
    const scaledRating = rating / 2;
    const fullStars = Math.floor(scaledRating);
    const hasHalfStar = scaledRating % 1 >= 0.5;
    
    // Pełne gwiazdki
    for (let i = 0; i < fullStars; i++) {
      stars.push(<span key={i} className="text-yellow-400 text-base">★</span>);
    }
    
    // Półgwiazdka
    if (hasHalfStar) {
      stars.push(<span key="half" className="text-yellow-400 text-base">☆</span>);
    }
    
    // Puste gwiazdki
    const remainingStars = 5 - Math.ceil(scaledRating);
    for (let i = 0; i < remainingStars; i++) {
      stars.push(<span key={`empty-${i}`} className="text-gray-300 text-base">☆</span>);
    }
    
    return stars;
  };

  // Lepsze URL dla okładki z fallback
  const getCoverUrl = () => {
    return book.best_cover_medium || 
           book.cover_url || 
           book.image_url_m || 
           book.open_library_cover_medium ||
           null;
  };

  const coverUrl = getCoverUrl();
  
  // Funkcja do skracania tekstu
  const truncateText = (text, maxLength) => {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  // Funkcja obsługi kliknięcia z nawigacją
  const handleClick = () => {
    // Wywołaj callback onClick jeśli istnieje (zachowaj obecną funkcjonalność)
    if (onClick) {
      onClick(book);
    }
    
    // Nawiguj do strony szczegółów książki
    navigate(`/book/${book.id}`, {
      state: {
        book: book // Przekaż całe dane książki
      }
    });
  };
  
  return (
    <div 
      className="bg-white rounded-xl shadow-lg hover:shadow-xl overflow-hidden transition-all duration-300 cursor-pointer hover:-translate-y-1 flex flex-col h-96"
      onClick={handleClick}
    >
      {/* Container dla okładki - pełna widoczność */}
      <div className="w-full h-60 relative overflow-hidden bg-gray-100 flex items-center justify-center">
        {coverUrl ? (
          <img 
            src={coverUrl} 
            alt={book.title || 'Book cover'}
            className="max-w-full max-h-full w-auto h-auto object-contain transition-transform duration-300 hover:scale-105"
            onError={(e) => {
              e.target.style.display = 'none';
              e.target.nextSibling.style.display = 'flex';
            }}
          />
        ) : null}
        
        {/* Placeholder dla brakujących okładek */}
        <div 
          className="w-full h-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-5xl font-bold"
          style={{ display: coverUrl ? 'none' : 'flex' }}
        >
          📚
        </div>
      </div>
      
      {/* Zawartość karty */}
      <div className="p-4 flex flex-col justify-between flex-1">
        <div>
          <h3 
            className="text-base font-semibold text-gray-800 mb-2 leading-tight"
            style={{
              display: '-webkit-box',
              WebkitLineClamp: 2,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden'
            }}
          >
            {book.title || 'Brak tytułu'}
          </h3>
          <p className="text-sm text-gray-600 mb-3 overflow-hidden">
            {truncateText(book.author || 'Nieznany autor', 40)}
          </p>
        </div>
        
        <div className="mt-auto">
          {/* Rating z prawdziwymi danymi (skala 0-10) */}
          <div className="flex items-center gap-2 mb-2">
            <div className="flex gap-0.5">
              {renderStars(rating)}
            </div>
            <span className="text-sm text-gray-600 font-medium">
              {rating > 0 ? `${rating.toFixed(1)}/10` : '(0.0/10)'}
              {ratingsCount > 0 && ` (${ratingsCount})`}
            </span>
          </div>
          
          <div className="text-xs text-gray-500 leading-relaxed">
            {book.isbn && <div>ISBN: {truncateText(book.isbn, 15)}</div>}
            {book.publication_year && <div>Rok: {book.publication_year}</div>}
            {book.id && <div>ID: {book.id}</div>}
          </div>
        </div>
      </div>
    </div>
  );
};

export default BookCard;