import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FaStar, FaStarHalfAlt, FaRegStar, FaExternalLinkAlt } from 'react-icons/fa';
import { openLibraryUtils } from '../services/api';

function BookCard({ 
  id, 
  title, 
  author, 
  cover, 
  description, 
  rating, 
  category, 
  isbn,
  openLibraryId,
  bestCoverMedium,
  openLibraryUrl 
}) {
  const navigate = useNavigate();
  const [coverUrl, setCoverUrl] = useState(cover);
  const [coverError, setCoverError] = useState(false);

  useEffect(() => {
    // Determine best cover URL to use
    const determineBestCover = async () => {
      // Priority order for cover sources
      const coverSources = [
        bestCoverMedium,  // From API with Open Library integration
        cover,            // Original cover prop
        isbn ? openLibraryUtils.getCoverUrls(isbn)?.medium : null  // Generate from ISBN
      ].filter(Boolean);

      // Try each cover source until we find one that works
      for (const url of coverSources) {
        try {
          const exists = await openLibraryUtils.checkCoverExists(url);
          if (exists) {
            setCoverUrl(url);
            setCoverError(false);
            return;
          }
        } catch {
          // Continue to next source
        }
      }
      
      // If no working cover found
      setCoverError(true);
    };

    if (isbn || cover || bestCoverMedium) {
      determineBestCover();
    } else {
      setCoverError(true);
    }
  }, [cover, isbn, bestCoverMedium]);

  const handleClick = () => {
    // Navigate to the book details page with state
    navigate(`/book/${id}`, {
      state: { 
        id,
        title, 
        author, 
        cover: coverUrl, 
        description, 
        rating, 
        category,
        isbn,
        openLibraryId,
        openLibraryUrl
      }
    });
  };

  const handleImageError = () => {
    setCoverError(true);
  };

  const renderStars = (rating) => {
    const stars = [];
    const r = parseFloat(rating);
    for (let i = 1; i <= 5; i++) {
      if (i <= Math.floor(r)) {
        stars.push(<FaStar key={i} className="text-yellow-400 inline" />);
      } else if (i - 0.5 <= r) {
        stars.push(<FaStarHalfAlt key={i} className="text-yellow-400 inline" />);
      } else {
        stars.push(<FaRegStar key={i} className="text-yellow-400 inline" />);
      }
    }
    return stars;
  };

  const handleOpenLibraryClick = (e) => {
    e.stopPropagation(); // Prevent card click
    if (openLibraryUrl) {
      window.open(openLibraryUrl, '_blank');
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-md hover:shadow-xl transform hover:-translate-y-1 transition-all duration-300 p-4 cursor-pointer group relative">
      {/* Open Library link button */}
      {openLibraryUrl && (
        <button
          onClick={handleOpenLibraryClick}
          className="absolute top-2 right-2 z-10 bg-blue-600 hover:bg-blue-700 text-white p-2 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-300"
          title="View on Open Library"
        >
          <FaExternalLinkAlt size={12} />
        </button>
      )}

      <div onClick={handleClick}>
        <div className="bg-gray-100 h-40 mb-4 flex items-center justify-center rounded overflow-hidden">
          {!coverError && coverUrl ? (
            <img
              src={coverUrl}
              alt={title}
              className="w-full h-full object-cover rounded transition-transform duration-300 group-hover:scale-105"
              onError={handleImageError}
            />
          ) : (
            <div className="text-center text-gray-400">
              <div className="text-2xl mb-1">📚</div>
              <span className="text-xs">No cover</span>
              {isbn && (
                <div className="text-xs mt-1 text-gray-500">
                  ISBN: {isbn}
                </div>
              )}
            </div>
          )}
        </div>

        <h3 className="text-lg font-semibold text-gray-800 group-hover:text-blue-600 transition-colors duration-300 line-clamp-2">
          {title}
        </h3>
        
        <p className="text-sm text-gray-500 mb-1">{author}</p>
        
        {rating && (
          <div className="flex items-center gap-1 mb-2">
            <div className="flex gap-1">{renderStars(rating)}</div>
            <span className="text-sm text-gray-600">({rating})</span>
          </div>
        )}
        
        {description && (
          <p className="text-xs text-gray-600 mb-2 line-clamp-2">{description}</p>
        )}
        
        {category && (
          <span className="inline-block px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded-full">
            {Array.isArray(category) ? category[0] : category}
          </span>
        )}

        {/* Debug info in development */}
        {process.env.NODE_ENV === 'development' && (
          <div className="mt-2 text-xs text-gray-400 border-t pt-2">
            <div>ID: {id}</div>
            {isbn && <div>ISBN: {isbn}</div>}
            {openLibraryId && <div>OL ID: {openLibraryId}</div>}
          </div>
        )}
      </div>
    </div>
  );
}

export default BookCard;