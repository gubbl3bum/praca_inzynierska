import React, { useState, useEffect } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import api from '../services/api';

const BookDetails = () => {
  const { id } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  
  const [book, setBook] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchBookDetails = async () => {
      try {
        setLoading(true);
        
        // Jeśli mamy dane książki w state (przekazane z BookCard), użyj ich
        if (location.state?.book) {
          setBook(location.state.book);
          setLoading(false);
          return;
        }
        
        // W przeciwnym razie pobierz z API
        const bookData = await api.books.getBook(id);
        setBook(bookData);
        setError(null);
      } catch (err) {
        console.error('Error fetching book details:', err);
        setError('Failed to load book details');
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchBookDetails();
    }
  }, [id, location.state]);

  // Funkcja do renderowania gwiazdek dla skali 0-10
  const renderStars = (rating) => {
    const stars = [];
    // Konwertuj ocenę 0-10 na skalę 0-5 gwiazdek
    const scaledRating = rating / 2;
    const fullStars = Math.floor(scaledRating);
    const hasHalfStar = scaledRating % 1 >= 0.5;
    
    // Pełne gwiazdki
    for (let i = 0; i < fullStars; i++) {
      stars.push(<span key={i} className="text-yellow-400 text-xl">★</span>);
    }
    
    // Półgwiazdka
    if (hasHalfStar) {
      stars.push(<span key="half" className="text-yellow-400 text-xl">☆</span>);
    }
    
    // Puste gwiazdki
    const remainingStars = 5 - Math.ceil(scaledRating);
    for (let i = 0; i < remainingStars; i++) {
      stars.push(<span key={`empty-${i}`} className="text-gray-300 text-xl">☆</span>);
    }
    
    return stars;
  };

  // Funkcja do pobierania najlepszej okładki
  const getBestCoverUrl = (book) => {
    return book?.best_cover_large || 
           book?.image_url_l || 
           book?.best_cover_medium || 
           book?.cover_url || 
           book?.image_url_m || 
           book?.open_library_cover_large ||
           book?.open_library_cover_medium ||
           null;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading book details...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">📚</div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Book Not Found</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => navigate(-1)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  if (!book) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center text-gray-500 py-12">
          <div className="text-6xl mb-4">📚</div>
          <p>Book details not available.</p>
          <button
            onClick={() => navigate(-1)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg mt-4"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  const coverUrl = getBestCoverUrl(book);
  const rating = book.average_rating || 0;
  const ratingsCount = book.ratings_count || 0;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto p-8">
        
        {/* Back button */}
        <button
          onClick={() => navigate(-1)}
          className="mb-6 flex items-center gap-2 text-blue-600 hover:text-blue-800 transition-colors"
        >
          ← Back to previous page
        </button>

        {/* Main content */}
        <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
          <div className="flex flex-col lg:flex-row">
            
            {/* Book cover */}
            <div className="lg:w-1/3 p-8">
              <div className="aspect-[3/4] w-full max-w-md mx-auto bg-gray-200 rounded-lg overflow-hidden shadow-md">
                {coverUrl ? (
                  <img 
                    src={coverUrl} 
                    alt={book.title} 
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.target.style.display = 'none';
                      e.target.nextSibling.style.display = 'flex';
                    }}
                  />
                ) : null}
                <div 
                  className="w-full h-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-6xl"
                  style={{ display: coverUrl ? 'none' : 'flex' }}
                >
                  📚
                </div>
              </div>
            </div>

            {/* Book information */}
            <div className="lg:w-2/3 p-8">
              
              {/* Title and author */}
              <h1 className="text-4xl font-bold text-gray-800 mb-2">
                {book.title}
              </h1>
              
              <p className="text-xl text-gray-600 mb-4">
                by {book.author || (book.authors && book.authors.length > 0 
                  ? book.authors.map(a => a.name || a).join(', ') 
                  : 'Unknown Author')}
              </p>

              {/* Rating section - ZAKTUALIZOWANA dla skali 0-10 */}
              <div className="mb-6">
                <div className="flex items-center gap-3 mb-2">
                  <div className="flex gap-1">
                    {renderStars(rating)}
                  </div>
                  <span className="text-2xl font-bold text-gray-800">
                    {rating.toFixed(1)}/10
                  </span>
                  {ratingsCount > 0 && (
                    <span className="text-gray-600">
                      ({ratingsCount.toLocaleString()} ratings)
                    </span>
                  )}
                </div>
                
                {/* Rating bar visualization */}
                <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                  <div 
                    className="bg-gradient-to-r from-yellow-400 to-orange-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${(rating / 10) * 100}%` }}
                  ></div>
                </div>
              </div>

              {/* Categories */}
              {(book.categories || book.category_names) && (
                <div className="mb-4">
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">Categories:</h3>
                  <div className="flex flex-wrap gap-2">
                    {(book.category_names || book.categories || []).map((category, index) => (
                      <span 
                        key={index}
                        className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium"
                      >
                        {category}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Publication info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                {book.publication_year && (
                  <div>
                    <span className="text-gray-600 font-medium">Published:</span>
                    <span className="ml-2">{book.publication_year}</span>
                  </div>
                )}
                
                {book.publisher && (
                  <div>
                    <span className="text-gray-600 font-medium">Publisher:</span>
                    <span className="ml-2">{book.publisher.name || book.publisher}</span>
                  </div>
                )}
                
                {book.isbn && (
                  <div>
                    <span className="text-gray-600 font-medium">ISBN:</span>
                    <span className="ml-2 font-mono">{book.isbn}</span>
                  </div>
                )}
                
                {book.page_count && (
                  <div>
                    <span className="text-gray-600 font-medium">Pages:</span>
                    <span className="ml-2">{book.page_count}</span>
                  </div>
                )}
                
                {book.language && (
                  <div>
                    <span className="text-gray-600 font-medium">Language:</span>
                    <span className="ml-2">{book.language}</span>
                  </div>
                )}
              </div>

              {/* Description */}
              {book.description && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">Description:</h3>
                  <p className="text-gray-700 leading-relaxed">
                    {book.description}
                  </p>
                </div>
              )}

              {/* Open Library link */}
              {book.open_library_url && (
                <div className="mb-6">
                  <a
                    href={book.open_library_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors"
                  >
                    📖 View on Open Library
                  </a>
                </div>
              )}

              {/* Action buttons */}
              <div className="flex flex-wrap gap-3">
                <button className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors">
                  Add to Reading List
                </button>
                <button className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg transition-colors">
                  Mark as Read
                </button>
                <button className="bg-yellow-600 hover:bg-yellow-700 text-white px-6 py-2 rounded-lg transition-colors">
                  Add to Favorites
                </button>
                <button className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 rounded-lg transition-colors">
                  Write Review
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Additional sections could go here */}
        <div className="mt-8 bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Reviews & Ratings</h2>
          <p className="text-gray-600">
            Reviews section coming soon...
          </p>
        </div>

      </div>
    </div>
  );
};

export default BookDetails;