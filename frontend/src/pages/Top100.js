import React, { useState, useEffect } from 'react';
import BookCard from '../components/BookCard';
import api from '../services/api';

const Top100 = () => {
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'
  const [filter, setFilter] = useState('all'); // 'all', 'recent', 'classic'

  // Time filters
  const timeFilters = [
    { value: 'all', label: 'All Time', icon: '🏆' },
    { value: 'recent', label: 'Last 5 Years', icon: '✨' },
    { value: 'classic', label: 'Classics (pre-2000)', icon: '📜' }
  ];

  // Fetch top books
  const fetchTopBooks = async () => {
    try {
      setLoading(true);
      
      // Prepare API parameters
      const params = {
        page_size: 100,
        ordering: '-average_rating,-ratings_count',
        average_rating__gte: 3.0 // minimum 3.0 rating
      };

      // Add time filter
      if (filter === 'recent') {
        params.publication_year__gte = new Date().getFullYear() - 5; // last 5 years
      } else if (filter === 'classic') {
        params.publication_year__lt = 2000; // before 2000
      }

      console.log('Fetching top books with params:', params);
      const response = await api.books.getBooks(params);
      
      // Get books and sort by rating
      let topBooks = response.results || response.books || response;
      
      // Additional client-side sorting
      topBooks = topBooks
        .filter(book => book && book.average_rating && book.average_rating > 0)
        .sort((a, b) => {
          // Sort by average_rating (desc), then by ratings_count (desc)
          if (b.average_rating !== a.average_rating) {
            return b.average_rating - a.average_rating;
          }
          return (b.ratings_count || 0) - (a.ratings_count || 0);
        })
        .slice(0, 100); // Take top 100

      setBooks(topBooks);
      setError(null);
    } catch (error) {
      console.error('Error fetching top books:', error);
      setError('Failed to load book rankings');
      setBooks([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTopBooks();
  }, [filter]);

  const handleBookClick = (book) => {
    console.log('Clicked book:', book);
    // TODO: Navigate to book details
  };

  // Component for list view with positions
  const BookListItem = ({ book, position }) => (
    <div 
      className="bg-white rounded-lg shadow-md p-4 mb-4 flex items-center gap-4 hover:shadow-lg transition-shadow cursor-pointer"
      onClick={() => handleBookClick(book)}
    >
      {/* Position */}
      <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center text-white font-bold text-lg">
        {position}
      </div>

      {/* Cover */}
      <div className="flex-shrink-0 w-16 h-24 bg-gray-200 rounded overflow-hidden">
        {book.best_cover_medium || book.cover_url || book.image_url_m ? (
          <img 
            src={book.best_cover_medium || book.cover_url || book.image_url_m} 
            alt={book.title}
            className="w-full h-full object-cover"
            onError={(e) => {
              e.target.style.display = 'none';
              e.target.nextSibling.style.display = 'flex';
            }}
          />
        ) : null}
        <div 
          className="w-full h-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-sm"
          style={{ display: (book.best_cover_medium || book.cover_url || book.image_url_m) ? 'none' : 'flex' }}
        >
          📚
        </div>
      </div>

      {/* Book information */}
      <div className="flex-1 min-w-0">
        <h3 className="text-lg font-semibold text-gray-800 mb-1 truncate">
          {book.title}
        </h3>
        <p className="text-gray-600 mb-2 truncate">
          {book.author}
        </p>
        
        {/* Rating */}
        <div className="flex items-center gap-2">
          <div className="flex">
            {[...Array(5)].map((_, i) => (
              <span
                key={i}
                className={`text-lg ${
                  i < Math.floor(book.average_rating || 0)
                    ? 'text-yellow-400'
                    : 'text-gray-300'
                }`}
              >
                ★
              </span>
            ))}
          </div>
          <span className="text-sm text-gray-600 font-medium">
            {(book.average_rating || 0).toFixed(1)}
          </span>
          {book.ratings_count > 0 && (
            <span className="text-sm text-gray-500">
              ({book.ratings_count} ratings)
            </span>
          )}
        </div>
      </div>

      {/* Additional info */}
      <div className="flex-shrink-0 text-right">
        {book.publication_year && (
          <div className="text-sm text-gray-500 mb-1">
            {book.publication_year}
          </div>
        )}
        {book.categories && (
          <div className="text-xs text-gray-400 max-w-24 truncate">
            {book.categories}
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            🏆 Top 100 Books
          </h1>
          <p className="text-gray-600 text-lg">
            The highest rated books according to our users
          </p>
        </div>

        {/* Filters and controls */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            
            {/* Time filters */}
            <div className="flex flex-wrap gap-2">
              {timeFilters.map(timeFilter => (
                <button
                  key={timeFilter.value}
                  onClick={() => setFilter(timeFilter.value)}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    filter === timeFilter.value
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {timeFilter.icon} {timeFilter.label}
                </button>
              ))}
            </div>

            {/* View toggle */}
            <div className="flex bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setViewMode('grid')}
                className={`px-4 py-2 rounded-md transition-colors ${
                  viewMode === 'grid'
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                🔲 Grid
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`px-4 py-2 rounded-md transition-colors ${
                  viewMode === 'list'
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                📋 List
              </button>
            </div>
          </div>
        </div>

        {/* Loading */}
        {loading && (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading rankings...</p>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-8">
            <div className="text-red-800 text-center">
              <div className="text-4xl mb-2">⚠️</div>
              <h3 className="text-lg font-semibold mb-2">Error Occurred</h3>
              <p className="mb-4">{error}</p>
              <button
                onClick={fetchTopBooks}
                className="bg-red-600 hover:bg-red-700 text-white px-6 py-2 rounded-lg"
              >
                Try Again
              </button>
            </div>
          </div>
        )}

        {/* Results */}
        {!loading && !error && (
          <>
            {/* Results info */}
            <div className="mb-6 text-center">
              <p className="text-gray-600">
                {books.length > 0 ? (
                  <>
                    Top {books.length} books 
                    {filter === 'recent' && ' from the last 5 years'}
                    {filter === 'classic' && ' from before 2000'}
                  </>
                ) : (
                  'No results found'
                )}
              </p>
            </div>

            {/* Grid view */}
            {viewMode === 'grid' && books.length > 0 && (
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                {books.map((book, index) => (
                  <div key={book.id} className="relative">
                    <BookCard
                      book={book}
                      onClick={handleBookClick}
                    />
                    {/* Position badge */}
                    <div className="absolute -top-2 -left-2 w-8 h-8 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center text-white font-bold text-sm shadow-lg">
                      {index + 1}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* List view */}
            {viewMode === 'list' && books.length > 0 && (
              <div className="max-w-4xl mx-auto">
                {books.map((book, index) => (
                  <BookListItem
                    key={book.id}
                    book={book}
                    position={index + 1}
                  />
                ))}
              </div>
            )}

            {/* No results */}
            {books.length === 0 && (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">🏆</div>
                <h3 className="text-xl font-semibold text-gray-700 mb-2">
                  No Books in Rankings
                </h3>
                <p className="text-gray-500 mb-4">
                  Try changing the time filter
                </p>
                <button
                  onClick={() => setFilter('all')}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg"
                >
                  Show All
                </button>
              </div>
            )}
          </>
        )}

        {/* Statistics at bottom */}
        {!loading && !error && books.length > 0 && (
          <div className="mt-12 bg-gradient-to-r from-blue-600 to-purple-700 rounded-lg p-8 text-white text-center">
            <h3 className="text-2xl font-bold mb-4">📊 Ranking Statistics</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <div className="text-3xl font-bold">
                  {(books.reduce((sum, book) => sum + (book.average_rating || 0), 0) / books.length).toFixed(1)}⭐
                </div>
                <div className="text-blue-100">Average Rating</div>
              </div>
              <div>
                <div className="text-3xl font-bold">
                  {books.reduce((sum, book) => sum + (book.ratings_count || 0), 0).toLocaleString()}
                </div>
                <div className="text-blue-100">Total Ratings</div>
              </div>
              <div>
                <div className="text-3xl font-bold">
                  {Math.max(...books.map(book => book.publication_year || 0).filter(year => year > 0))}
                </div>
                <div className="text-blue-100">Newest Book</div>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};

export default Top100;