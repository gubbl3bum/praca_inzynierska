import React, { useState, useEffect } from 'react';
import BookCard from './BookCard';
import api from '../services/api';

const SimilarBooks = ({ bookId }) => {
  // Tab state
  const [activeTab, setActiveTab] = useState('content'); // 'content', 'users', 'hybrid'
  
  // Content-based recommendations state
  const [contentBooks, setContentBooks] = useState([]);
  const [contentLoading, setContentLoading] = useState(true);
  const [contentError, setContentError] = useState(null);
  const [contentPage, setContentPage] = useState(1);
  const [contentTotal, setContentTotal] = useState(0);
  
  // User-based recommendations state (placeholder)
  const [userBooks, setUserBooks] = useState([]);
  const [userLoading, setUserLoading] = useState(false);
  const [userError, setUserError] = useState(null);
  const [userPage, setUserPage] = useState(1);
  const [userTotal, setUserTotal] = useState(0);
  
  // Hybrid recommendations state (placeholder)
  const [hybridBooks, setHybridBooks] = useState([]);
  const [hybridLoading, setHybridLoading] = useState(false);
  const [hybridError, setHybridError] = useState(null);
  const [hybridPage, setHybridPage] = useState(1);
  const [hybridTotal, setHybridTotal] = useState(0);
  
  // Common state
  const [showDetails, setShowDetails] = useState(false);
  const [booksPerPage] = useState(8);
  const [minSimilarity, setMinSimilarity] = useState(0.1);
  const [sortBy, setSortBy] = useState('similarity');

  const tabs = [
    {
      id: 'content',
      name: 'Similar Books',
      icon: '📚',
      description: 'Based on content similarity',
      implemented: true
    },
    {
      id: 'users',
      name: 'Users Also Liked',
      icon: '👥',
      description: 'Based on user preferences',
      implemented: false
    },
    {
      id: 'hybrid',
      name: 'AI Recommendations',
      icon: '🤖',
      description: 'Combined ML approach',
      implemented: false
    }
  ];

  useEffect(() => {
    if (bookId) {
      if (activeTab === 'content') {
        fetchContentBasedRecommendations();
      } else if (activeTab === 'users') {
        fetchUserBasedRecommendations();
      } else if (activeTab === 'hybrid') {
        fetchHybridRecommendations();
      }
    }
  }, [bookId, activeTab, contentPage, userPage, hybridPage, minSimilarity, sortBy]);

  const fetchContentBasedRecommendations = async () => {
    try {
      setContentLoading(true);
      setContentError(null);
      
      console.log('🔍 Fetching content-based recommendations for ID:', bookId);
      
      const params = {
        limit: booksPerPage * 5,
        min_similarity: minSimilarity,
        details: showDetails ? 'true' : 'false'
      };
      
      const response = await api.books.getSimilarBooks(bookId, params);
      
      if (response.status === 'success') {
        const allBooks = response.recommendations || [];
        
        // Client-side sorting
        let sortedBooks = [...allBooks];
        switch (sortBy) {
          case 'similarity':
            sortedBooks.sort((a, b) => (b.similarity_score || 0) - (a.similarity_score || 0));
            break;
          case 'rating':
            sortedBooks.sort((a, b) => (b.average_rating || 0) - (a.average_rating || 0));
            break;
          case 'title':
            sortedBooks.sort((a, b) => (a.title || '').localeCompare(b.title || ''));
            break;
          default:
            break;
        }
        
        // Client-side pagination
        const startIndex = (contentPage - 1) * booksPerPage;
        const endIndex = startIndex + booksPerPage;
        const paginatedBooks = sortedBooks.slice(startIndex, endIndex);
        
        setContentBooks(paginatedBooks);
        setContentTotal(sortedBooks.length);
        
      } else {
        throw new Error(response.message || 'Failed to fetch content-based recommendations');
      }
      
    } catch (err) {
      console.error('❌ Error fetching content-based recommendations:', err);
      const errorMessage = api.handleError ? api.handleError(err, 'Failed to load recommendations') : err.message;
      setContentError(errorMessage);
      setContentBooks([]);
      setContentTotal(0);
    } finally {
      setContentLoading(false);
    }
  };

  const fetchUserBasedRecommendations = async () => {
    try {
      setUserLoading(true);
      setUserError(null);
      
      console.log('👥 Fetching user-based recommendations (placeholder)');
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Generate placeholder data based on content recommendations
      const placeholderBooks = contentBooks.map(book => ({
        ...book,
        similarity_score: Math.random() * 0.4 + 0.3, // Random similarity 30-70%
        recommendation_reason: 'Users with similar taste also liked this book',
        recommendation_type: 'collaborative_filtering'
      })).slice(0, 6); // Show fewer for placeholder
      
      setUserBooks(placeholderBooks);
      setUserTotal(placeholderBooks.length);
      
    } catch (err) {
      console.error('❌ Error fetching user-based recommendations:', err);
      setUserError('User-based recommendations not implemented yet');
      setUserBooks([]);
      setUserTotal(0);
    } finally {
      setUserLoading(false);
    }
  };

  const fetchHybridRecommendations = async () => {
    try {
      setHybridLoading(true);
      setHybridError(null);
      
      console.log('🤖 Fetching hybrid recommendations (placeholder)');
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Generate placeholder data
      const placeholderBooks = contentBooks.map(book => ({
        ...book,
        similarity_score: Math.random() * 0.6 + 0.4, // Higher similarity for AI
        recommendation_reason: 'AI algorithm considers multiple factors',
        recommendation_type: 'hybrid_ml'
      })).slice(0, 4); // Show even fewer for placeholder
      
      setHybridBooks(placeholderBooks);
      setHybridTotal(placeholderBooks.length);
      
    } catch (err) {
      console.error('❌ Error fetching hybrid recommendations:', err);
      setHybridError('AI recommendations not implemented yet');
      setHybridBooks([]);
      setHybridTotal(0);
    } finally {
      setHybridLoading(false);
    }
  };

  const handleBookClick = (book) => {
    console.log('Clicked recommended book:', book);
    // Navigation jest obsługiwana w BookCard
  };

  const handlePageChange = (newPage, type) => {
    if (type === 'content') {
      setContentPage(newPage);
    } else if (type === 'users') {
      setUserPage(newPage);
    } else if (type === 'hybrid') {
      setHybridPage(newPage);
    }
    
    // Scroll do góry sekcji
    const element = document.getElementById('similar-books-section');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  const getCurrentData = () => {
    switch (activeTab) {
      case 'content':
        return {
          books: contentBooks,
          loading: contentLoading,
          error: contentError,
          page: contentPage,
          total: contentTotal,
          totalPages: Math.ceil(contentTotal / booksPerPage)
        };
      case 'users':
        return {
          books: userBooks,
          loading: userLoading,
          error: userError,
          page: userPage,
          total: userTotal,
          totalPages: Math.ceil(userTotal / booksPerPage)
        };
      case 'hybrid':
        return {
          books: hybridBooks,
          loading: hybridLoading,
          error: hybridError,
          page: hybridPage,
          total: hybridTotal,
          totalPages: Math.ceil(hybridTotal / booksPerPage)
        };
      default:
        return {
          books: [],
          loading: false,
          error: null,
          page: 1,
          total: 0,
          totalPages: 1
        };
    }
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

  const generatePageNumbers = (currentPage, totalPages) => {
    const pages = [];
    const maxVisible = 5;
    const start = Math.max(1, currentPage - Math.floor(maxVisible / 2));
    const end = Math.min(totalPages, start + maxVisible - 1);
    
    for (let i = start; i <= end; i++) {
      pages.push(i);
    }
    
    return pages;
  };

  const currentData = getCurrentData();

  const renderPlaceholderMessage = (type) => {
    const messages = {
      users: {
        icon: '👥',
        title: 'User-Based Recommendations',
        description: 'This feature will show books liked by users with similar reading preferences.',
        features: [
          'Collaborative filtering algorithm',
          'Based on user ratings and reading history',
          'Discovers books you might miss with content-based filtering',
          'Learns from community preferences'
        ],
        status: 'Coming Soon'
      },
      hybrid: {
        icon: '🤖',
        title: 'AI-Powered Recommendations',
        description: 'Advanced machine learning combining multiple recommendation approaches.',
        features: [
          'Deep learning neural networks',
          'Combines content + user + contextual data',
          'Personalized ranking algorithms',
          'Real-time learning from user interactions'
        ],
        status: 'In Development'
      }
    };

    const config = messages[type];
    if (!config) return null;

    return (
      <div className="text-center py-12">
        <div className="text-6xl mb-4">{config.icon}</div>
        <h3 className="text-xl font-semibold text-gray-700 mb-2">
          {config.title}
        </h3>
        <p className="text-gray-600 mb-6 max-w-lg mx-auto">
          {config.description}
        </p>
        
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6 max-w-md mx-auto">
          <h4 className="font-medium text-blue-800 mb-2">Planned Features:</h4>
          <ul className="text-sm text-blue-700 text-left space-y-1">
            {config.features.map((feature, index) => (
              <li key={index} className="flex items-center gap-2">
                <span className="text-blue-500">•</span>
                {feature}
              </li>
            ))}
          </ul>
        </div>
        
        <div className="inline-flex items-center gap-2 bg-yellow-100 text-yellow-800 px-4 py-2 rounded-full text-sm">
          <span className="animate-pulse">⚡</span>
          {config.status}
        </div>
        
        {/* Show placeholder books if available */}
        {currentData.books.length > 0 && (
          <div className="mt-8">
            <p className="text-sm text-gray-500 mb-4">
              Preview with sample data:
            </p>
          </div>
        )}
      </div>
    );
  };

  return (
    <div id="similar-books-section" className="bg-white rounded-xl shadow-lg p-6">
      {/* Header with Tabs */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">
          📚 Book Recommendations
        </h2>
        
        {/* Tab Navigation */}
        <div className="flex flex-wrap gap-2 mb-4">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <span>{tab.icon}</span>
              <span>{tab.name}</span>
              {!tab.implemented && (
                <span className="bg-yellow-400 text-yellow-900 px-1.5 py-0.5 rounded text-xs font-bold">
                  SOON
                </span>
              )}
            </button>
          ))}
        </div>
        
        {/* Tab Description */}
        <p className="text-sm text-gray-600 mb-4">
          {tabs.find(tab => tab.id === activeTab)?.description}
        </p>
      </div>

      {/* Controls - only show for implemented tabs */}
      {activeTab === 'content' && (
        <div className="mb-6 flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between bg-gray-50 p-4 rounded-lg">
          <div className="flex flex-wrap gap-4 items-center">
            {/* Similarity threshold */}
            <div className="flex items-center gap-2">
              <label className="text-sm font-medium text-gray-700">Min Similarity:</label>
              <select
                value={minSimilarity}
                onChange={(e) => {
                  setMinSimilarity(parseFloat(e.target.value));
                  setContentPage(1);
                }}
                className="text-sm border border-gray-300 rounded px-2 py-1"
              >
                <option value={0.05}>5% (Show All)</option>
                <option value={0.1}>10% (Default)</option>
                <option value={0.2}>20% (Good Match)</option>
                <option value={0.3}>30% (Very Similar)</option>
                <option value={0.5}>50% (Highly Similar)</option>
              </select>
            </div>

            {/* Sort by */}
            <div className="flex items-center gap-2">
              <label className="text-sm font-medium text-gray-700">Sort by:</label>
              <select
                value={sortBy}
                onChange={(e) => {
                  setSortBy(e.target.value);
                  setContentPage(1);
                }}
                className="text-sm border border-gray-300 rounded px-2 py-1"
              >
                <option value="similarity">Similarity Score</option>
                <option value="rating">Book Rating</option>
                <option value="title">Title (A-Z)</option>
              </select>
            </div>

            {/* Show details toggle */}
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
          </div>

          {/* Results info */}
          <div className="text-sm text-gray-600">
            Found {currentData.total} book{currentData.total !== 1 ? 's' : ''}
            {currentData.total > 0 && (
              <span className="ml-2">
                (showing {((currentData.page - 1) * booksPerPage) + 1}-{Math.min(currentData.page * booksPerPage, currentData.total)})
              </span>
            )}
          </div>
        </div>
      )}

      {/* Content */}
      {currentData.loading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">
            {activeTab === 'content' ? 'Finding similar books...' : 
             activeTab === 'users' ? 'Analyzing user preferences...' :
             'Training AI models...'}
          </p>
        </div>
      ) : currentData.error ? (
        <div className="text-center py-8">
          <div className="text-4xl mb-2">⚠️</div>
          <p className="text-red-600 mb-4">{currentData.error}</p>
          <button
            onClick={() => {
              if (activeTab === 'content') fetchContentBasedRecommendations();
              else if (activeTab === 'users') fetchUserBasedRecommendations();
              else if (activeTab === 'hybrid') fetchHybridRecommendations();
            }}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
          >
            Try Again
          </button>
        </div>
      ) : currentData.total === 0 ? (
        activeTab === 'content' ? (
          <div className="text-center py-8 text-gray-500">
            <div className="text-4xl mb-2">🔍</div>
            <p className="mb-4">No similar books found.</p>
            <p className="text-sm text-gray-400">
              Try lowering the similarity threshold or check back later.
            </p>
          </div>
        ) : (
          renderPlaceholderMessage(activeTab)
        )
      ) : (
        <>
          {/* Placeholder message for non-implemented tabs with sample data */}
          {activeTab !== 'content' && (
            <div className="mb-6">
              {renderPlaceholderMessage(activeTab)}
            </div>
          )}
          
          {/* Books grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mb-6">
            {currentData.books.map((book) => (
              <div key={`${activeTab}-${book.id}`} className="relative">
                <BookCard
                  book={book}
                  onClick={handleBookClick}
                />
                
                {/* Recommendation type badge */}
                <div 
                  className={`absolute top-2 left-2 ${getSimilarityBadgeColor(book.similarity_score)} text-white px-2 py-1 rounded-full text-xs font-medium shadow-lg z-10`}
                  title={`${activeTab === 'content' ? 'Content similarity' : 
                          activeTab === 'users' ? 'User preference match' : 
                          'AI recommendation score'}: ${(book.similarity_score * 100).toFixed(1)}%`}
                >
                  {activeTab === 'content' ? getSimilarityLabel(book.similarity_score) :
                   activeTab === 'users' ? 'User Match' :
                   'AI Pick'}
                </div>
                
                {/* Score */}
                <div className="absolute top-2 right-2 bg-black bg-opacity-70 text-white px-2 py-1 rounded text-xs font-medium z-10">
                  {(book.similarity_score * 100).toFixed(0)}%
                </div>
                
                {/* Preview badge for non-implemented features */}
                {activeTab !== 'content' && (
                  <div className="absolute bottom-2 left-2 bg-yellow-500 text-yellow-900 px-2 py-1 rounded text-xs font-bold z-10">
                    PREVIEW
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Pagination */}
          {currentData.totalPages > 1 && (
            <div className="flex flex-col sm:flex-row justify-between items-center gap-4 pt-4 border-t border-gray-200">
              
              {/* Page info */}
              <div className="text-sm text-gray-600">
                Page {currentData.page} of {currentData.totalPages}
              </div>

              {/* Pagination controls */}
              <div className="flex items-center gap-2">
                {/* Previous button */}
                <button
                  onClick={() => handlePageChange(currentData.page - 1, activeTab)}
                  disabled={currentData.page === 1}
                  className={`px-3 py-1 rounded text-sm transition-colors ${
                    currentData.page === 1
                      ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  ← Previous
                </button>

                {/* Page numbers */}
                {generatePageNumbers(currentData.page, currentData.totalPages).map(pageNum => (
                  <button
                    key={pageNum}
                    onClick={() => handlePageChange(pageNum, activeTab)}
                    className={`px-3 py-1 rounded text-sm transition-colors ${
                      pageNum === currentData.page
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {pageNum}
                  </button>
                ))}

                {/* Next button */}
                <button
                  onClick={() => handlePageChange(currentData.page + 1, activeTab)}
                  disabled={currentData.page === currentData.totalPages}
                  className={`px-3 py-1 rounded text-sm transition-colors ${
                    currentData.page === currentData.totalPages
                      ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  Next →
                </button>
              </div>
            </div>
          )}
        </>
      )}

      {/* Footer with algorithm info */}
      <div className="mt-6 pt-4 border-t border-gray-200 text-xs text-gray-500 text-center">
        {activeTab === 'content' ? (
          <>
            <p>Content-based recommendations using cosine similarity (categories, keywords, authors, descriptions).</p>
            <p className="mt-1">Algorithm weights: 40% categories, 30% keywords, 20% authors, 10% description themes.</p>
          </>
        ) : activeTab === 'users' ? (
          <p>User-based collaborative filtering will analyze reading patterns of users with similar preferences.</p>
        ) : (
          <p>Hybrid AI recommendations will combine content analysis, user behavior, and advanced ML techniques.</p>
        )}
      </div>
    </div>
  );
};

export default SimilarBooks;