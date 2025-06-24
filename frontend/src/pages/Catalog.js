import React, { useState, useEffect } from 'react';
import BookCard from '../components/BookCard';
import api from '../services/api';

const Catalog = () => {
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    search: '',
    category: '',
    author: '',
    year_from: '',
    year_to: '',
    rating_min: '',
    sort: '-created_at'
  });
  
  const [pagination, setPagination] = useState({
    currentPage: 1,
    totalPages: 1,
    totalItems: 0,
    hasNext: false,
    hasPrevious: false,
    pageSize: 20
  });

  const sortOptions = [
    { value: '-created_at', label: 'Newest First' },
    { value: 'created_at', label: 'Oldest First' },
    { value: '-average_rating', label: 'Highest Rated' },
    { value: 'average_rating', label: 'Lowest Rated' },
    { value: 'title', label: 'Title A-Z' },
    { value: '-title', label: 'Title Z-A' },
    { value: 'author', label: 'Author A-Z' },
    { value: '-author', label: 'Author Z-A' }
  ];

  // Fetch books from API
  const fetchBooks = async (page = 1) => {
    try {
      setLoading(true);
      setError(null);
      
      // Prepare parameters
      const params = {
        page,
        page_size: 20,
        ...filters
      };

      // Remove empty filters
      Object.keys(params).forEach(key => {
        if (params[key] === '' || params[key] === null || params[key] === undefined) {
          delete params[key];
        }
      });

      console.log('Fetching books with params:', params);
      const response = await api.books.getBooks(params);
      
      console.log('API response:', response);
      
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
        throw new Error(response.message || 'Failed to fetch books');
      }

    } catch (error) {
      console.error('Error fetching books:', error);
      const errorMessage = api.handleError(error, 'Failed to load book catalog');
      setError(errorMessage);
      setBooks([]);
      setPagination(prev => ({ ...prev, currentPage: page }));
    } finally {
      setLoading(false);
    }
  };

  // Load books when filters change
  useEffect(() => {
    fetchBooks(1);
    setPagination(prev => ({ ...prev, currentPage: 1 }));
  }, [filters]);

  // Handle filter changes
  const handleFilterChange = (name, value) => {
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Handle search
  const handleSearch = (e) => {
    e.preventDefault();
    fetchBooks(1);
  };

  // Handle page change
  const handlePageChange = (newPage) => {
    console.log('Changing to page:', newPage);
    fetchBooks(newPage);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Reset filters
  const resetFilters = () => {
    setFilters({
      search: '',
      category: '',
      author: '',
      year_from: '',
      year_to: '',
      rating_min: '',
      sort: '-created_at'
    });
  };

  const handleBookClick = (book) => {
    console.log('Clicked book:', book);
    // Navigation jest obsługiwana w BookCard
  };

  // Generate page numbers for pagination
  const generatePageNumbers = () => {
    return api.pagination.generatePageNumbers(pagination.currentPage, pagination.totalPages, 5);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">Book Catalog</h1>
          <p className="text-gray-600">
            Browse and filter our collection 
            {pagination.totalItems > 0 && ` of ${pagination.totalItems.toLocaleString()} books`}
          </p>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4 text-gray-800">Filters & Search</h2>
          
          {/* Search */}
          <form onSubmit={handleSearch} className="mb-6">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1">
                <input
                  type="text"
                  placeholder="Search books, authors, descriptions..."
                  value={filters.search}
                  onChange={(e) => handleFilterChange('search', e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <button
                type="submit"
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                🔍 Search
              </button>
            </div>
          </form>

          {/* Other filters */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
            
            {/* Category */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Category
              </label>
              <input
                type="text"
                placeholder="e.g. Fantasy, Sci-Fi"
                value={filters.category}
                onChange={(e) => handleFilterChange('category', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Author */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Author
              </label>
              <input
                type="text"
                placeholder="Author name"
                value={filters.author}
                onChange={(e) => handleFilterChange('author', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Year from */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Year From
              </label>
              <input
                type="number"
                placeholder="1950"
                min="1900"
                max="2024"
                value={filters.year_from}
                onChange={(e) => handleFilterChange('year_from', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Year to */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Year To
              </label>
              <input
                type="number"
                placeholder="2024"
                min="1900"
                max="2024"
                value={filters.year_to}
                onChange={(e) => handleFilterChange('year_to', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
              />
            </div>

          </div>

          {/* Rating and sorting */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            
            {/* Minimum rating */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Min. Rating
              </label>
              <select
                value={filters.rating_min}
                onChange={(e) => handleFilterChange('rating_min', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Ratings</option>
                <option value="9.0">9.0+ ⭐ (Excellent)</option>
                <option value="8.0">8.0+ ⭐ (Very Good)</option>
                <option value="7.0">7.0+ ⭐ (Good)</option>
                <option value="6.0">6.0+ ⭐ (Above Average)</option>
                <option value="5.0">5.0+ ⭐ (Average)</option>
                <option value="4.0">4.0+ ⭐ (Below Average)</option>
              </select>
            </div>

            {/* Sort */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Sort By
              </label>
              <select
                value={filters.sort}
                onChange={(e) => handleFilterChange('sort', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
              >
                {sortOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Reset */}
            <div className="flex items-end">
              <button
                onClick={resetFilters}
                className="w-full px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 transition-colors"
              >
                🔄 Reset Filters
              </button>
            </div>

          </div>
        </div>

        {/* Loading */}
        {loading && (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading books...</p>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-8">
            <div className="text-red-800 text-center">
              <div className="text-4xl mb-2">⚠️</div>
              <h3 className="text-lg font-semibold mb-2">Error Loading Books</h3>
              <p className="mb-4">{error}</p>
              <button
                onClick={() => fetchBooks(pagination.currentPage)}
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
                      Showing {((pagination.currentPage - 1) * pagination.pageSize) + 1}-{Math.min(pagination.currentPage * pagination.pageSize, pagination.totalItems)} of {pagination.totalItems.toLocaleString()} books
                      {pagination.totalPages > 1 && (
                        <> (page {pagination.currentPage} of {pagination.totalPages})</>
                      )}
                    </>
                  ) : (
                    'No results found'
                  )}
                </p>
                
                {/* Active filters display */}
                {(filters.search || filters.category || filters.author || filters.year_from || filters.year_to || filters.rating_min) && (
                  <div className="mt-2 flex flex-wrap gap-2">
                    <span className="text-sm text-gray-500">Active filters:</span>
                    {filters.search && (
                      <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
                        Search: "{filters.search}"
                      </span>
                    )}
                    {filters.category && (
                      <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-sm">
                        Category: {filters.category}
                      </span>
                    )}
                    {filters.author && (
                      <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded text-sm">
                        Author: {filters.author}
                      </span>
                    )}
                    {(filters.year_from || filters.year_to) && (
                      <span className="bg-orange-100 text-orange-800 px-2 py-1 rounded text-sm">
                        Year: {filters.year_from || '?'}-{filters.year_to || '?'}
                      </span>
                    )}
                    {filters.rating_min && (
                      <span className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded text-sm">
                        Min Rating: {filters.rating_min}+
                      </span>
                    )}
                  </div>
                )}
              </div>
              
              {/* Performance info */}
              <div className="text-xs text-gray-400">
                Page: {pagination.currentPage} | 
                Has Next: {pagination.hasNext ? 'Yes' : 'No'} | 
                Has Prev: {pagination.hasPrevious ? 'Yes' : 'No'}
              </div>
            </div>

            {/* Book grid */}
            {books.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6 mb-8">
                {books
                  .filter(book => book && book.id)
                  .map((book) => (
                    <BookCard
                      key={book.id}
                      book={book}
                      onClick={handleBookClick}
                    />
                  ))
                }
              </div>
            ) : (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">📚</div>
                <h3 className="text-xl font-semibold text-gray-700 mb-2">
                  No Books Found
                </h3>
                <p className="text-gray-500 mb-4">
                  {filters.search || filters.category || filters.author || filters.year_from || filters.year_to || filters.rating_min 
                    ? 'Try adjusting your filters or search terms'
                    : 'No books are available in the catalog at the moment'
                  }
                </p>
                <div className="flex flex-wrap justify-center gap-4">
                  <button
                    onClick={resetFilters}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg"
                  >
                    Clear All Filters
                  </button>
                  <button
                    onClick={() => fetchBooks(1)}
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

                {/* First page */}
                {pagination.currentPage > 3 && (
                  <>
                    <button
                      onClick={() => handlePageChange(1)}
                      className="px-4 py-2 rounded-lg bg-white text-gray-700 hover:bg-gray-100 border border-gray-300"
                    >
                      1
                    </button>
                    {pagination.currentPage > 4 && (
                      <span className="px-2 text-gray-500">...</span>
                    )}
                  </>
                )}

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

                {/* Last page */}
                {pagination.currentPage < pagination.totalPages - 2 && (
                  <>
                    {pagination.currentPage < pagination.totalPages - 3 && (
                      <span className="px-2 text-gray-500">...</span>
                    )}
                    <button
                      onClick={() => handlePageChange(pagination.totalPages)}
                      className="px-4 py-2 rounded-lg bg-white text-gray-700 hover:bg-gray-100 border border-gray-300"
                    >
                      {pagination.totalPages}
                    </button>
                  </>
                )}

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

            {/* Quick stats */}
            {books.length > 0 && (
              <div className="mt-8 bg-gradient-to-r from-blue-600 to-purple-700 rounded-lg p-6 text-white">
                <h3 className="text-lg font-semibold mb-4">📊 Catalog Statistics</h3>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold">
                      {pagination.totalItems.toLocaleString()}
                    </div>
                    <div className="text-blue-100 text-sm">Total Books</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold">
                      {books.length > 0 ? (books.reduce((sum, book) => sum + (book.average_rating || 0), 0) / books.length).toFixed(1) : '0.0'}
                    </div>
                    <div className="text-blue-100 text-sm">Avg Rating (This Page)</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold">
                      {books.reduce((sum, book) => sum + (book.ratings_count || 0), 0).toLocaleString()}
                    </div>
                    <div className="text-blue-100 text-sm">Total Reviews (This Page)</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold">
                      {new Set(books.flatMap(book => book.categories || [])).size}
                    </div>
                    <div className="text-blue-100 text-sm">Categories (This Page)</div>
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

export default Catalog;