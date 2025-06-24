import React, { useState, useEffect } from 'react';
import BookCard from '../components/BookCard';
import api from '../services/api';

const Top100 = () => {
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'
  const [filter, setFilter] = useState('all'); // 'all', 'recent', 'classic'
  
  const [pagination, setPagination] = useState({
    currentPage: 1,
    totalPages: 1,
    totalItems: 0,
    hasNext: false,
    hasPrevious: false,
    pageSize: 20
  });

  // Time filters
  const timeFilters = [
    { value: 'all', label: 'All Time', icon: '🏆' },
    { value: 'recent', label: 'Last 5 Years', icon: '✨' },
    { value: 'classic', label: 'Classics (pre-2000)', icon: '📜' }
  ];

  // Fetch top books with pagination
  const fetchTopBooks = async (page = 1) => {
    try {
      setLoading(true);
      setError(null);
      
      // Prepare API parameters
      const params = {
        page,
        page_size: 20,
        filter: filter // time filter
      };

      console.log('Fetching top books with params:', params);
      
      const response = await api.books.getTopRated(params);
      
      console.log('Top books API response:', response);
      
      if (response.status === 'success' && response.results) {
        // Normalizuj dane książek
        const normalizedBooks = response.results.map(api.data.normalizeBook).filter(Boolean);
        setBooks(normalizedBooks);
        
        // Ustaw paginację
        setPagination({
          currentPage: response.current_page || page,
          totalPages: response.num_pages || 1,
          totalItems: response.count || 0,
          hasNext: response.has_next || false,
          hasPrevious: response.has_previous || false,
          pageSize: response.page_size || 20,
          nextPage: response.next_page,
          previousPage: response.previous_page
        });
      } else {
        throw new Error(response.message || 'Failed to fetch top books');
      }

    } catch (error) {
      console.error('Error fetching top books:', error);
      const errorMessage = api.handleError(error, 'Failed to load book rankings');
      setError(errorMessage);
      setBooks([]);
      setPagination(prev => ({ ...prev, currentPage: page }));
    } finally {
      setLoading(false);
    }
  };

  // Load books when filter changes
  useEffect(() => {
    fetchTopBooks(1);
    setPagination(prev => ({ ...prev, currentPage: 1 }));
  }, [filter]);

  // Handle page change
  const handlePageChange = (newPage) => {
    console.log('Changing to page:', newPage);
    fetchTopBooks(newPage);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Generate page numbers for pagination
  const generatePageNumbers = () => {
    return api.pagination.generatePageNumbers(pagination.currentPage, pagination.totalPages, 5);
  };

  const handleBookClick = (book) => {
    console.log('Clicked book:', book);
    // Navigation jest obsługiwana w BookCard
  };

  const BookListItem = ({ book, position }) => {
    // Calculate real position based on pagination
    const realPosition = (pagination.currentPage - 1) * pagination.pageSize + position;
    
    // Renderowanie gwiazdek dla skali 0-10
    const renderStars = (rating) => {
      const stars = [];
      const scaledRating = rating / 2; // Konwersja z 0-10 na 0-5
      const fullStars = Math.floor(scaledRating);
      const hasHalfStar = scaledRating % 1 >= 0.5;
      
      for (let i = 0; i < fullStars; i++) {
        stars.push(<span key={i} className="text-yellow-400 text-lg">★</span>);
      }
      
      if (hasHalfStar) {
        stars.push(<span key="half" className="text-yellow-400 text-lg">☆</span>);
      }
      
      const remainingStars = 5 - Math.ceil(scaledRating);
      for (let i = 0; i < remainingStars; i++) {
        stars.push(<span key={`empty-${i}`} className="text-gray-300 text-lg">☆</span>);
      }
      
      return stars;
    };
    
    return (
      <div 
        className="bg-white rounded-lg shadow-md p-4 mb-4 flex items-center gap-4 hover:shadow-lg transition-shadow cursor-pointer"
        onClick={() => handleBookClick(book)}
      >
        {/* Position */}
        <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center text-white font-bold text-lg">
          {realPosition}
        </div>

        {/* Cover */}
        <div className="flex-shrink-0 w-16 h-24 bg-gray-200 rounded overflow-hidden">
          {book.best_cover_medium || book.cover_image_url || book.image_url_m ? (
            <img 
              src={book.best_cover_medium || book.cover_image_url || book.image_url_m} 
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
            style={{ display: (book.best_cover_medium || book.cover_image_url || book.image_url_m) ? 'none' : 'flex' }}
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
            by {book.author || book.authors || 'Unknown Author'}
          </p>
          
          {/* Rating */}
          <div className="flex items-center gap-2">
            <div className="flex gap-0.5">
              {renderStars(book.average_rating || 0)}
            </div>
            <span className="text-sm text-gray-600 font-medium">
              {(book.average_rating || 0).toFixed(1)}/10
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
          {book.publish_year && (
            <div className="text-sm text-gray-500 mb-1">
              {book.publish_year}
            </div>
          )}
          {book.categories && book.categories.length > 0 && (
            <div className="text-xs text-gray-400 max-w-24 truncate">
              {book.categories.slice(0, 2).join(', ')}
              {book.categories.length > 2 && '...'}
            </div>
          )}
        </div>
      </div>
    );
  };

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
            {pagination.totalItems > 0 && ` (${pagination.totalItems.toLocaleString()} total)`}
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
              <h3 className="text-lg font-semibold mb-2">Error Loading Rankings</h3>
              <p className="mb-4">{error}</p>
              <button
                onClick={() => fetchTopBooks(pagination.currentPage)}
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
            <div className="mb-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
              <div>
                <p className="text-gray-600">
                  {books.length > 0 ? (
                    <>
                      Top {((pagination.currentPage - 1) * pagination.pageSize) + 1}-{Math.min(pagination.currentPage * pagination.pageSize, pagination.totalItems)} books 
                      {filter === 'recent' && ' from the last 5 years'}
                      {filter === 'classic' && ' from before 2000'}
                      {pagination.totalPages > 1 && (
                        <> (page {pagination.currentPage} of {pagination.totalPages})</>
                      )}
                    </>
                  ) : (
                    'No results found'
                  )}
                </p>
                
                {/* Filter info */}
                <div className="mt-1 text-sm text-gray-500">
                  {filter === 'all' && 'Showing books from all time periods'}
                  {filter === 'recent' && 'Showing books published in the last 5 years (2019-2024)'}
                  {filter === 'classic' && 'Showing books published before 2000'}
                </div>
              </div>
              
              {/* Performance info */}
              <div className="text-xs text-gray-400">
                Page: {pagination.currentPage} | 
                Has Next: {pagination.hasNext ? 'Yes' : 'No'} | 
                Has Prev: {pagination.hasPrevious ? 'Yes' : 'No'}
              </div>
            </div>

            {/* Grid view */}
            {viewMode === 'grid' && books.length > 0 && (
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6 mb-8">
                {books.map((book, index) => {
                  // Calculate real position based on pagination
                  const realPosition = (pagination.currentPage - 1) * pagination.pageSize + index + 1;
                  
                  return (
                    <div key={book.id} className="relative">
                      <BookCard
                        book={book}
                        onClick={handleBookClick}
                      />
                      {/* Position badge */}
                      <div className="absolute -top-2 -left-2 w-8 h-8 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center text-white font-bold text-sm shadow-lg z-10">
                        {realPosition}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {/* List view */}
            {viewMode === 'list' && books.length > 0 && (
              <div className="max-w-4xl mx-auto mb-8">
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
                  {filter === 'recent' && 'No highly rated books found from the last 5 years.'}
                  {filter === 'classic' && 'No highly rated classic books found.'}
                  {filter === 'all' && 'No books with ratings found in the database.'}
                </p>
                <div className="flex flex-wrap justify-center gap-4">
                  <button
                    onClick={() => setFilter('all')}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg"
                  >
                    Show All Time
                  </button>
                  <button
                    onClick={() => fetchTopBooks(1)}
                    className="bg-gray-600 hover:bg-gray-700 text-white px-6 py-2 rounded-lg"
                  >
                    Refresh
                  </button>
                </div>
              </div>
            )}

            {/* Pagination */}
            {pagination.totalPages > 1 && (
              <div className="flex justify-center items-center gap-2 py-8">
                {/* Previous button */}
                <button
                  onClick={() => handlePageChange(pagination.currentPage - 1)}
                  disabled={!pagination.hasPrevious}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    pagination.hasPrevious
                      ? 'bg-blue-600 hover:bg-blue-700 text-white cursor-pointer'
                      : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  }`}
                >
                  ← Previous
                </button>

                {/* Page numbers */}
                {generatePageNumbers().map(pageNum => (
                  <button
                    key={pageNum}
                    onClick={() => handlePageChange(pageNum)}
                    className={`px-4 py-2 rounded-lg transition-colors ${
                      pageNum === pagination.currentPage
                        ? 'bg-blue-600 text-white'
                        : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
                    }`}
                  >
                    {pageNum}
                  </button>
                ))}

                {/* Next button */}
                <button
                  onClick={() => handlePageChange(pagination.currentPage + 1)}
                  disabled={!pagination.hasNext}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    pagination.hasNext
                      ? 'bg-blue-600 hover:bg-blue-700 text-white cursor-pointer'
                      : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  }`}
                >
                  Next →
                </button>
              </div>
            )}

            {/* Statistics at bottom */}
            {books.length > 0 && (
              <div className="mt-12 bg-gradient-to-r from-blue-600 to-purple-700 rounded-lg p-8 text-white text-center">
                <h3 className="text-2xl font-bold mb-4">📊 Ranking Statistics</h3>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                  <div>
                    <div className="text-3xl font-bold">
                      {books.length > 0 ? (books.reduce((sum, book) => sum + (book.average_rating || 0), 0) / books.length).toFixed(1) : '0.0'}⭐
                    </div>
                    <div className="text-blue-100">Average Rating (This Page)</div>
                  </div>
                  <div>
                    <div className="text-3xl font-bold">
                      {books.reduce((sum, book) => sum + (book.ratings_count || 0), 0).toLocaleString()}
                    </div>
                    <div className="text-blue-100">Total Ratings (This Page)</div>
                  </div>
                  <div>
                    <div className="text-3xl font-bold">
                      {pagination.totalItems.toLocaleString()}
                    </div>
                    <div className="text-blue-100">Total Books in Ranking</div>
                  </div>
                  <div>
                    <div className="text-3xl font-bold">
                      {new Set(books.flatMap(book => book.categories || [])).size}
                    </div>
                    <div className="text-blue-100">Categories (This Page)</div>
                  </div>
                </div>
              </div>
            )}
          </>
        )}

      </div>
    </div>
  );
};

export default Top100;