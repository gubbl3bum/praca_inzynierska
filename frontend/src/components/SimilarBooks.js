import React, { useState, useEffect } from 'react';
import BookCard from './BookCard';
import api from '../services/api';

const SimilarBooks = ({ bookId, limit = 8 }) => {
  const [similarBooks, setSimilarBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    if (bookId) {
      fetchSimilarBooks();
    }
  }, [bookId, limit]);

  const fetchSimilarBooks = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = {
        limit: limit,
        min_similarity: 0.1,
        details: showDetails ? 'true' : 'false'
      };
      
      const response = await api.books.getSimilarBooks(bookId, params);
      
      if (response.status === 'success') {
        setSimilarBooks(response.recommendations || []);
      } else {
        throw new Error(response.message || 'Failed to fetch similar books');
      }
      
    } catch (err) {
      console.error('Error fetching similar books:', err);
      const errorMessage = api.handleError(err, 'Failed to load similar books');
      setError(errorMessage);
      setSimilarBooks([]);
    } finally {
      setLoading(false);
    }
  };

  const handleBookClick = (book) => {
    console.log('Clicked similar book:', book);
    // Navigation jest obsługiwana w BookCard
  };

  const getSimilarityBadgeColor = (score) => {
    if (score >= 0.8) return 'bg-green-500';
    if (score >= 0.6) return 'bg-yellow-500';
    if (score >= 0.4) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const getSimilarityLabel = (score) => {
    if (score >= 0.8) return 'Very Similar';
    if (score >= 0.6) return 'Similar';
    if (score >= 0.4) return 'Somewhat Similar';
    return 'Loosely Related';
  };

  const renderSimilarityDetails = (book) => {
    if (!book.similarity_details) return null;
    
    const details = book.similarity_details;
    
    return (
      <div className="mt-2 text-xs text-gray-600">
        <div className="flex flex-wrap gap-1 mb-1">
          {details.category_similarity > 0.3 && (
            <span className="bg-blue-100 text-blue-800 px-1 py-0.5 rounded">
              Categories: {(details.category_similarity * 100).toFixed(0)}%
            </span>
          )}
          {details.keyword_similarity > 0.2 && (
            <span className="bg-green-100 text-green-800 px-1 py-0.5 rounded">
              Keywords: {(details.keyword_similarity * 100).toFixed(0)}%
            </span>
          )}
          {details.author_similarity > 0.5 && (
            <span className="bg-purple-100 text-purple-800 px-1 py-0.5 rounded">
              Author: {(details.author_similarity * 100).toFixed(0)}%
            </span>
          )}
        </div>
        <div className="text-gray-500 italic">
          {details.reason}
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Similar Books</h2>
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Finding similar books...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Similar Books</h2>
        <div className="text-center py-8">
          <div className="text-4xl mb-2">⚠️</div>
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={fetchSimilarBooks}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (similarBooks.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Similar Books</h2>
        <div className="text-center py-8 text-gray-500">
          <div className="text-4xl mb-2">🔍</div>
          <p className="mb-4">No similar books found at the moment.</p>
          <p className="text-sm text-gray-400">
            This might be because similarities haven't been calculated yet, or this book is quite unique!
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">
          📚 Similar Books
        </h2>
        
        <div className="flex gap-2">
          <button
            onClick={() => setShowDetails(!showDetails)}
            className={`px-3 py-1 rounded text-sm transition-colors ${
              showDetails
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {showDetails ? 'Hide Details' : 'Show Details'}
          </button>
          
          <button
            onClick={fetchSimilarBooks}
            className="px-3 py-1 bg-gray-100 text-gray-700 hover:bg-gray-200 rounded text-sm"
          >
            🔄 Refresh
          </button>
        </div>
      </div>

      {/* Results count */}
      <div className="mb-4 text-sm text-gray-600">
        Found {similarBooks.length} similar book{similarBooks.length !== 1 ? 's' : ''}
        {similarBooks.length > 0 && (
          <span className="ml-2">
            (avg similarity: {(similarBooks.reduce((sum, book) => sum + book.similarity_score, 0) / similarBooks.length).toFixed(3)})
          </span>
        )}
      </div>

      {/* Books grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {similarBooks.map((book) => (
          <div key={book.id} className="relative">
            <BookCard
              book={book}
              onClick={handleBookClick}
            />
            
            {/* Similarity badge */}
            <div 
              className={`absolute top-2 left-2 ${getSimilarityBadgeColor(book.similarity_score)} text-white px-2 py-1 rounded-full text-xs font-medium shadow-lg z-10`}
              title={`Similarity: ${(book.similarity_score * 100).toFixed(1)}%`}
            >
              {getSimilarityLabel(book.similarity_score)}
            </div>
            
            {/* Similarity score */}
            <div className="absolute top-2 right-2 bg-black bg-opacity-70 text-white px-2 py-1 rounded text-xs font-medium z-10">
              {(book.similarity_score * 100).toFixed(0)}%
            </div>
            
            {/* Detailed similarity info */}
            {showDetails && book.similarity_details && (
              <div className="mt-2 p-2 bg-gray-50 rounded text-xs">
                <div className="font-medium text-gray-700 mb-1">
                  Why similar:
                </div>
                {renderSimilarityDetails(book)}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Footer with algorithm info */}
      <div className="mt-6 pt-4 border-t border-gray-200 text-xs text-gray-500 text-center">
        <p>
          Recommendations based on cosine similarity using categories, keywords, authors, and descriptions.
        </p>
        {showDetails && (
          <p className="mt-1">
            Similarity calculated using: 40% categories, 30% keywords, 20% authors, 10% description themes.
          </p>
        )}
      </div>
    </div>
  );
};

export default SimilarBooks;