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
    sort: '-created_at' // default to newest
  });
  const [pagination, setPagination] = useState({
    page: 1,
    totalPages: 1,
    totalBooks: 0,
    hasNext: false,
    hasPrevious: false
  });

  // Sort options
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
      
      setBooks(response.results || response.books || response);
      
      // Set pagination if API returns this information
      if (response.results) {
        setPagination({
          page,
          totalPages: Math.ceil(response.count / 20),
          totalBooks: response.count,
          hasNext: !!response.next,
          hasPrevious: !!response.previous
        });
      } else {
        // Fallback if API doesn't return pagination
        setPagination(prev => ({ ...prev, page }));
      }

      setError(null);
    } catch (error) {
      console.error('Error fetching books:', error);
      setError('Failed to load book catalog');
      setBooks([]);
    } finally {
      setLoading(false);
    }
  };

  // Load books when filters change
  useEffect(() => {
    fetchBooks(1);
    setPagination(prev => ({ ...prev, page: 1 }));
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
    // TODO: Navigate to book details
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">Book Catalog</h1>
          <p className="text-gray-600">
            Browse and filter our collection {pagination.totalBooks > 0 && `of ${pagination.totalBooks} books`}
          </p>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4 text-gray-800">Filters</h2>
          
          {/* Search */}
          <form onSubmit={handleSearch} className="mb-6">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1">
                <input
                  type="text"
                  placeholder="Search books, authors..."
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
                <option value="4.5">4.5+ ⭐</option>
                <option value="4.0">4.0+ ⭐</option>
                <option value="3.5">3.5+ ⭐</option>
                <option value="3.0">3.0+ ⭐</option>
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
              <h3 className="text-lg font-semibold mb-2">Error Occurred</h3>
              <p className="mb-4">{error}</p>
              <button
                onClick={() => fetchBooks(pagination.page)}
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
            <div className="mb-6 flex justify-between items-center">
              <p className="text-gray-600">
                {books.length > 0 ? (
                  <>
                    Found {pagination.totalBooks > 0 ? pagination.totalBooks : books.length} books
                    {pagination.totalPages > 1 && (
                      <> (page {pagination.page} of {pagination.totalPages})</>
                    )}
                  </>
                ) : (
                  'No results found'
                )}
              </p>
            </div>

            {/* Book list */}
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
                  Try changing your filters or search terms
                </p>
                <button
                  onClick={resetFilters}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg"
                >
                  Clear Filters
                </button>
              </div>
            )}

            {/* Pagination */}
            {pagination.totalPages > 1 && (
              <div className="flex justify-center items-center gap-2 py-8">
                <button
                  onClick={() => handlePageChange(pagination.page - 1)}
                  disabled={!pagination.hasPrevious}
                  className={`px-4 py-2 rounded-lg ${
                    pagination.hasPrevious
                      ? 'bg-blue-600 hover:bg-blue-700 text-white'
                      : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  }`}
                >
                  ← Previous
                </button>

                {/* Page numbers */}
                {Array.from({ length: Math.min(5, pagination.totalPages) }, (_, i) => {
                  const pageNum = Math.max(1, pagination.page - 2) + i;
                  if (pageNum > pagination.totalPages) return null;
                  
                  return (
                    <button
                      key={pageNum}
                      onClick={() => handlePageChange(pageNum)}
                      className={`px-4 py-2 rounded-lg ${
                        pageNum === pagination.page
                          ? 'bg-blue-600 text-white'
                          : 'bg-white text-gray-700 hover:bg-gray-100'
                      }`}
                    >
                      {pageNum}
                    </button>
                  );
                })}

                <button
                  onClick={() => handlePageChange(pagination.page + 1)}
                  disabled={!pagination.hasNext}
                  className={`px-4 py-2 rounded-lg ${
                    pagination.hasNext
                      ? 'bg-blue-600 hover:bg-blue-700 text-white'
                      : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  }`}
                >
                  Next →
                </button>
              </div>
            )}
          </>
        )}

      </div>
    </div>
  );
};

export default Catalog;