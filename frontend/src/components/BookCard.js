import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AddToListButton from './AddToListButton';

const BookCard = ({ book, onClick }) => {
  const navigate = useNavigate();
  const [imageError, setImageError] = useState(false);
  const [imageLoading, setImageLoading] = useState(true);

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

  const displayPrice = price ? `$${price}` : null;
  const displayYear = publish_year || publication_year;
  const displayYearText = displayYear ? ` (${displayYear})` : '';
  const displayRating = average_rating ? Number(average_rating).toFixed(1) : '0.0';
  
  // POPRAWKA: Bezpieczne przetwarzanie authors
  let displayAuthors = 'Unknown Author';
  
  if (typeof authors === 'string' && authors !== 'Unknown Author') {
    displayAuthors = authors;
  } else if (Array.isArray(authors) && authors.length > 0) {
    // Jeśli to tablica obiektów
    displayAuthors = authors.map(a => {
      if (typeof a === 'string') return a;
      if (typeof a === 'object' && a !== null) {
        return a.name || a.full_name || a.first_name + ' ' + a.last_name || 'Unknown';
      }
      return 'Unknown';
    }).filter(Boolean).join(', ');
  } else if (typeof authors === 'object' && authors !== null) {
    // Jeśli to pojedynczy obiekt
    displayAuthors = authors.name || authors.full_name || 
                     (authors.first_name && authors.last_name 
                       ? `${authors.first_name} ${authors.last_name}` 
                       : 'Unknown Author');
  } else if (author) {
    // Fallback na pole author
    if (typeof author === 'string') {
      displayAuthors = author;
    } else if (typeof author === 'object' && author !== null) {
      displayAuthors = author.name || author.full_name || 
                      (author.first_name && author.last_name 
                        ? `${author.first_name} ${author.last_name}` 
                        : 'Unknown Author');
    }
  }

  const shortDescription = description && description.length > 100 
    ? description.substring(0, 100) + '...' 
    : description;

  const coverUrl = cover_image_url || best_cover_medium || image_url_m;

  const renderStars = (rating) => {
    const stars = [];
    const scaledRating = rating / 2;
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

  const handleClick = () => {
    if (onClick) {
      onClick(book);
    }
    
    if (id && id !== 'unknown') {
      navigate(`/book/${id}`, { 
        state: { book }
      });
    }
  };

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

  // POPRAWKA: Bezpieczne przetwarzanie categories
  const displayCategories = Array.isArray(categories) 
    ? categories.map(cat => {
        if (typeof cat === 'string') return cat;
        if (typeof cat === 'object' && cat !== null) {
          return cat.name || 'Unknown';
        }
        return null;
      }).filter(Boolean)
    : [];

  return (
    <div 
      className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300 cursor-pointer flex flex-col h-full relative"
      style={{ overflow: 'visible' }}
    >
      <div className="absolute top-2 left-2" style={{ zIndex: 9999 }} onClick={(e) => e.stopPropagation()}>
        <AddToListButton book={book} compact={true} />
      </div>

      {/* Cover image - zachowujemy overflow-hidden tylko dla obrazka */}
      <div className="relative aspect-[3/4] w-full flex items-center justify-center overflow-hidden rounded-t-lg" onClick={handleClick}>
        {coverUrl && !imageError ? (
          <>
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
            
            {imageLoading && (
              <div className="absolute inset-0 bg-gray-200 flex items-center justify-center">
                <div className="text-gray-400 text-lg">📖</div>
              </div>
            )}
          </>
        ) : (
          <div className="w-full h-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-4xl">
            📚
          </div>
        )}
        
        {average_rating > 0 && (
          <div className="absolute top-2 right-2 bg-black bg-opacity-70 text-white px-2 py-1 rounded text-xs font-medium">
            ⭐ {displayRating}
          </div>
        )}
      </div>

      {/* Book Info */}
      <div className="p-4 flex-1 flex flex-col" onClick={handleClick}>
        <h3 className="font-semibold text-gray-800 mb-1 line-clamp-2 flex-shrink-0">
          {title}{displayYearText}
        </h3>
        
        <p className="text-sm text-gray-600 mb-2 line-clamp-1 flex-shrink-0">
          {displayAuthors}
        </p>
        
        {displayCategories.length > 0 && (
          <div className="mb-2 flex-shrink-0">
            <div className="flex flex-wrap gap-1">
              {displayCategories.slice(0, 2).map((category, index) => (
                <span 
                  key={index}
                  className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full"
                >
                  {category}
                </span>
              ))}
              {displayCategories.length > 2 && (
                <span className="text-xs text-gray-500">+{displayCategories.length - 2}</span>
              )}
            </div>
          </div>
        )}

        {shortDescription && (
          <p className="text-xs text-gray-500 mb-3 line-clamp-2 flex-1">
            {shortDescription}
          </p>
        )}

        <div className="mt-auto">
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
        </div>
      </div>
    </div>
  );
};

export default BookCard;