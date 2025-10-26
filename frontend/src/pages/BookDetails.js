import React, { useState, useEffect } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import api from '../services/api';
import SimilarBooks from '../components/SimilarBooks';
import AddToListButton from '../components/AddToListButton';
import ReviewList from '../components/ReviewList'; // ⭐ NOWY IMPORT

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
        setError(null);
        
        if (location.state?.book) {
          console.log('Using book data from navigation state:', location.state.book);
          const normalizedBook = api.data.normalizeBook(location.state.book);
          setBook(normalizedBook);
          setLoading(false);
          return;
        }
        
        console.log('Fetching book details from API for ID:', id);
        const response = await api.books.getBook(id);
        
        if (response.status === 'success') {
          const normalizedBook = api.data.normalizeBook(response);
          setBook(normalizedBook);
        } else {
          throw new Error(response.message || 'Failed to fetch book details');
        }
        
      } catch (err) {
        console.error('Error fetching book details:', err);
        const errorMessage = api.handleError(err, 'Failed to load book details');
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchBookDetails();
    }
  }, [id, location.state]);

  const renderStars = (rating) => {
    const stars = [];
    const scaledRating = rating / 2;
    const fullStars = Math.floor(scaledRating);
    const hasHalfStar = scaledRating % 1 >= 0.5;
    
    for (let i = 0; i < fullStars; i++) {
      stars.push(<span key={i} className="text-yellow-400 text-xl">★</span>);
    }
    
    if (hasHalfStar) {
      stars.push(<span key="half" className="text-yellow-400 text-xl">☆</span>);
    }
    
    const remainingStars = 5 - Math.ceil(scaledRating);
    for (let i = 0; i < remainingStars; i++) {
      stars.push(<span key={`empty-${i}`} className="text-gray-300 text-xl">☆</span>);
    }
    
    return stars;
  };

  const getBestCoverUrl = (book) => {
    return book?.best_cover_large || 
           book?.image_url_l || 
           book?.best_cover_medium || 
           book?.cover_image_url || 
           book?.image_url_m || 
           null;
  };

  const getAuthorsDisplay = (book) => {
    if (!book) return 'Unknown Author';
    
    if (typeof book.authors === 'string') {
      return book.authors;
    } else if (Array.isArray(book.authors)) {
      return book.authors.map(a => typeof a === 'string' ? a : a.name || a.full_name || 'Unknown').join(', ');
    } else if (book.author) {
      return typeof book.author === 'string' ? book.author : book.author.name || book.author.full_name || 'Unknown Author';
    }
    
    return 'Unknown Author';
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
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg mr-4"
          >
            Go Back
          </button>
          <button
            onClick={() => window.location.reload()}
            className="bg-gray-600 hover:bg-gray-700 text-white px-6 py-2 rounded-lg"
          >
            Try Again
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
  const authorsDisplay = getAuthorsDisplay(book);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto p-8">
        
        <button
          onClick={() => navigate(-1)}
          className="mb-6 flex items-center gap-2 text-blue-600 hover:text-blue-800 transition-colors"
        >
          ← Back to previous page
        </button>

        {/* BOOK INFO SECTION - bez zmian */}
        <div className="bg-white rounded-2xl shadow-lg overflow-visible relative">
          <div className="flex flex-col lg:flex-row">
            
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

            <div className="lg:w-2/3 p-8">
              
              <h1 className="text-4xl font-bold text-gray-800 mb-2">
                {book.title}
              </h1>
              
              <p className="text-xl text-gray-600 mb-4">
                by {authorsDisplay}
              </p>

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
                
                <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                  <div 
                    className="bg-gradient-to-r from-yellow-400 to-orange-500 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${(rating / 10) * 100}%` }}
                  ></div>
                </div>
              </div>

              {book.categories && book.categories.length > 0 && (
                <div className="mb-4">
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">Categories:</h3>
                  <div className="flex flex-wrap gap-2">
                    {book.categories.map((category, index) => (
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

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                {book.publish_year && (
                  <div>
                    <span className="text-gray-600 font-medium">Published:</span>
                    <span className="ml-2">
                      {book.publish_month && `${book.publish_month} `}{book.publish_year}
                    </span>
                  </div>
                )}
                
                {book.publisher && (
                  <div>
                    <span className="text-gray-600 font-medium">Publisher:</span>
                    <span className="ml-2">
                      {typeof book.publisher === 'string' ? book.publisher : book.publisher.name}
                    </span>
                  </div>
                )}
                
                {book.isbn && (
                  <div>
                    <span className="text-gray-600 font-medium">ISBN:</span>
                    <span className="ml-2 font-mono">{book.isbn}</span>
                  </div>
                )}
                
                {book.price && (
                  <div>
                    <span className="text-gray-600 font-medium">Price:</span>
                    <span className="ml-2 text-green-600 font-medium">${book.price}</span>
                  </div>
                )}
              </div>

              {book.keywords && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">Keywords:</h3>
                  <p className="text-gray-700 text-sm italic">{book.keywords}</p>
                </div>
              )}

              {book.description && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">Description:</h3>
                  <p className="text-gray-700 leading-relaxed">
                    {book.description}
                  </p>
                </div>
              )}

              {/* Action buttons */}
              <div className="flex flex-wrap gap-3">
                <AddToListButton book={book} />
                
                <button className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg transition-colors">
                  Mark as Read
                </button>
                
                <button 
                  onClick={() => {
                    // Scroll do sekcji reviews
                    const reviewSection = document.getElementById('reviews-section');
                    if (reviewSection) {
                      reviewSection.scrollIntoView({ behavior: 'smooth' });
                    }
                  }}
                  className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 rounded-lg transition-colors"
                >
                  Write Review
                </button>
              </div>

              {(book.created_at || book.updated_at) && (
                <div className="mt-6 pt-6 border-t border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-800 mb-2">Book Information:</h3>
                  <div className="text-sm text-gray-500 space-y-1">
                    {book.created_at && (
                      <div>Added to catalog: {new Date(book.created_at).toLocaleDateString()}</div>
                    )}
                    {book.updated_at && (
                      <div>Last updated: {new Date(book.updated_at).toLocaleDateString()}</div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* ⭐ NOWA SEKCJA - REVIEWS */}
        <div id="reviews-section" className="mt-8 bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">Reviews & Ratings</h2>
          <ReviewList bookId={book.id} />
        </div>

        {/* SIMILAR BOOKS - bez zmian */}
        <div className="mt-8">
          <SimilarBooks bookId={book.id}/>
        </div>

      </div>
    </div>
  );
};

export default BookDetails;