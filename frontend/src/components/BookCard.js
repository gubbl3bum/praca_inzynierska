import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AddToListButton from './AddToListButton';

const BookCard = ({ book, onClick }) => {
  const navigate = useNavigate();
  const [imageError, setImageError] = useState(false);
  const [imageLoading, setImageLoading] = useState(true);

  // BEZPIECZNE SPRAWDZENIE BOOK OBJECT
  if (!book) {
    return (
      <div className="bg-white rounded-lg shadow-md p-4 flex flex-col h-full">
        <div className="text-center text-gray-500 py-8">
          <div className="text-4xl mb-2">📚</div>
          <p>Book data not available</p>
        </div>
      </div>
    );
  }

  // BEZPIECZNE WARTOŚCI Z FALLBACKAMI
  const {
    id = 'unknown',
    title = 'Unknown Title',
    authors = 'Unknown Author',
    author = null,
    price = null,
    publish_year = null,
    publication_year = null,
    average_rating = 0,
    ratings_count = 0,
    description = '',
    cover_image_url = null,
    best_cover_medium = null,
    image_url_m = null,
    isbn = null,
    categories = []
  } = book;

  // FORMATOWANIE DANYCH
  const displayPrice = price ? `$${price}` : null;
  const displayYear = publish_year || publication_year;
  const displayYearText = displayYear ? ` (${displayYear})` : '';
  const displayRating = average_rating ? Number(average_rating).toFixed(1) : '0.0';
  
  // Obsługuj różne formaty autorów
  let displayAuthors = 'Unknown Author';
  if (typeof authors === 'string' && authors !== 'Unknown Author') {
    displayAuthors = authors;
  } else if (Array.isArray(authors) && authors.length > 0) {
    displayAuthors = authors.map(a => typeof a === 'string' ? a : a.name || a.full_name || 'Unknown').join(', ');
  } else if (author) {
    displayAuthors = typeof author === 'string' ? author : author.name || author.full_name || 'Unknown Author';
  }

  const shortDescription = description && description.length > 100 
    ? description.substring(0, 100) + '...' 
    : description;

  // 🖼️ POPRAWIONE: Wybór najlepszej okładki z debugowaniem
  const coverUrl = cover_image_url || best_cover_medium || image_url_m;
  
  // Debug - pokaż jaką okładkę próbujemy załadować
  React.useEffect(() => {
    if (coverUrl) {
      console.log(`📖 ${title}: Trying to load cover: ${coverUrl}`);
    }
  }, [coverUrl, title]);

  // Renderowanie gwiazdek dla oceny 0-10
  const renderStars = (rating) => {
    const stars = [];
    const scaledRating = rating / 2; // Konwersja z 0-10 na 0-5
    const fullStars = Math.floor(scaledRating);
    const hasHalfStar = scaledRating % 1 >= 0.5;
    
    for (let i = 0; i < fullStars; i++) {
      stars.push(<span key={i} className="text-yellow-400">★</span>);
    }
    
    if (hasHalfStar) {
      stars.push(<span key="half" className="text-yellow-400">☆</span>);
    }
    
    const remainingStars = 5 - Math.ceil(scaledRating);
    for (let i = 0; i < remainingStars; i++) {
      stars.push(<span key={`empty-${i}`} className="text-gray-300">☆</span>);
    }
    
    return stars;
  };

  // Obsługa kliknięcia
  const handleClick = () => {
    if (onClick) {
      onClick(book);
    }
    
    // Nawigacja do szczegółów książki
    if (id && id !== 'unknown') {
      navigate(`/book/${id}`, { 
        state: { book }
      });
    }
  };

  // 🖼️ Obsługa błędów ładowania obrazka
  const handleImageError = () => {
    console.log(`❌ Failed to load cover for ${title}: ${coverUrl}`);
    setImageError(true);
    setImageLoading(false);
  };

  const handleImageLoad = () => {
    console.log(`✅ Successfully loaded cover for ${title}: ${coverUrl}`);
    setImageError(false);
    setImageLoading(false);
  };

  return (
    <div 
      className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300 cursor-pointer overflow-hidden flex flex-col h-full"
      onClick={handleClick}
    >
      {/* 🖼️ POPRAWIONA SEKCJA OKŁADKI */}
      <div className="relative aspect-[3/4] w-full flex items-center justify-center overflow-hidden">
        {coverUrl && !imageError ? (
          <>
            {/* Obrazek okładki */}
            <img 
              src={coverUrl} 
              alt={`Cover of ${title}`}
              className={`w-full h-full object-cover transition-opacity duration-300 ${
                imageLoading ? 'opacity-0' : 'opacity-100'
              }`}
              onError={handleImageError}
              onLoad={handleImageLoad}
              style={{ 
                display: imageError ? 'none' : 'block'
              }}
            />
            
            {/* Loading placeholder podczas ładowania */}
            {imageLoading && (
              <div className="absolute inset-0 bg-gray-200 flex items-center justify-center">
                <div className="text-gray-400 text-lg">📖</div>
              </div>
            )}
          </>
        ) : (
          /* Placeholder gdy brak okładki lub błąd ładowania */
          <div className="w-full h-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-4xl">
            📚
          </div>
        )}
        
        {/* Rating badge */}
        {average_rating > 0 && (
          <div className="absolute top-2 right-2 bg-black bg-opacity-70 text-white px-2 py-1 rounded text-xs font-medium">
            ⭐ {displayRating}
          </div>
        )}
      </div>

      {/* Book Info */}
      <div className="p-4 flex-1 flex flex-col">
        <h3 className="font-semibold text-gray-800 mb-1 line-clamp-2 flex-shrink-0">
          {title}{displayYearText}
        </h3>
        
        <p className="text-sm text-gray-600 mb-2 line-clamp-1 flex-shrink-0">
          {displayAuthors}
        </p>
        
        {/* Categories */}
        {categories && categories.length > 0 && (
          <div className="mb-2 flex-shrink-0">
            <div className="flex flex-wrap gap-1">
              {categories.slice(0, 2).map((category, index) => (
                <span 
                  key={index}
                  className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full"
                >
                  {category}
                </span>
              ))}
              {categories.length > 2 && (
                <span className="text-xs text-gray-500">+{categories.length - 2}</span>
              )}
            </div>
          </div>
        )}

        {/* Description */}
        {shortDescription && (
          <p className="text-xs text-gray-500 mb-3 line-clamp-2 flex-1">
            {shortDescription}
          </p>
        )}

        {/* Bottom info */}
        <div className="mt-auto">
          {/* Rating */}
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-1">
              <div className="flex text-sm">
                {renderStars(average_rating)}
              </div>
              <span className="text-xs text-gray-600">
                {displayRating}/10
              </span>
            </div>
            
            {ratings_count > 0 && (
              <span className="text-xs text-gray-500">
                ({ratings_count})
              </span>
            )}
          </div>
          
          {/* Price and additional info */}
          <div className="flex items-center justify-between text-xs">
            {displayPrice && (
              <div className="font-medium text-green-600">
                {displayPrice}
              </div>
            )}
            
            {isbn && (
              <div className="text-gray-400 font-mono text-xs">
                {isbn.substring(0, 10)}...
              </div>
            )}
          </div>
          
          {/* 🔍 DEBUG INFO - usuń w produkcji
          {process.env.NODE_ENV === 'development' && coverUrl && (
            <div className="text-xs text-gray-400 mt-1 truncate" title={coverUrl}>
              Cover: {coverUrl.substring(0, 30)}...
            </div>
          )} */}
        </div>
      </div>
      <div className="mt-2">
        <AddToListButton book={book} compact={true} />
      </div>
    </div>
  );
};

export default BookCard;