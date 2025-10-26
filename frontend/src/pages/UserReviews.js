import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../services/AuthContext';
import api from '../services/api';
import BookCard from '../components/BookCard';
import ReviewForm from '../components/ReviewForm';

const UserReviews = () => {
  const navigate = useNavigate();
  const { isAuthenticated, user } = useAuth();
  const [reviews, setReviews] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [sortBy, setSortBy] = useState('-created_at');
  const [ratingFilter, setRatingFilter] = useState(null);
  const [editingReview, setEditingReview] = useState(null);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    fetchUserReviews();
  }, [isAuthenticated, page, sortBy, ratingFilter]);

  const fetchUserReviews = async () => {
    try {
      setLoading(true);
      setError(null);

      const token = localStorage.getItem('wolfread_tokens');
      const tokens = token ? JSON.parse(token) : null;
      
      if (!tokens?.access) {
        navigate('/login');
        return;
      }

      const params = {
        page: page,
        page_size: 12,
        sort_by: sortBy
      };

      if (ratingFilter) {
        params.rating = ratingFilter;
      }

      const response = await api.reviews.getUserReviews(tokens.access, params);

      if (response.status === 'success') {
        setReviews(response.reviews || []);
        setStatistics(response.user_statistics || null);
        setTotalPages(response.pagination?.total_pages || 1);
      }
    } catch (err) {
      console.error('Error fetching user reviews:', err);
      setError(api.handleError(err, 'Failed to load your reviews'));
    } finally {
      setLoading(false);
    }
  };

  const handleReviewUpdate = (updatedReview) => {
    if (updatedReview === null) {
      // Review deleted
      setReviews(reviews.filter(r => r.id !== editingReview.id));
    } else {
      // Review updated
      setReviews(reviews.map(r => 
        r.id === updatedReview.id ? updatedReview : r
      ));
    }
    setEditingReview(null);
    fetchUserReviews(); // Refresh to update statistics
  };

  const renderStars = (rating) => {
    const stars = [];
    for (let i = 1; i <= 10; i++) {
      stars.push(
        <span 
          key={i} 
          className={`text-xl ${i <= rating ? 'text-yellow-400' : 'text-gray-300'}`}
        >
          ★
        </span>
      );
    }
    return stars;
  };

  const getRatingColor = (rating) => {
    if (rating <= 4) return 'bg-red-100 text-red-800';
    if (rating <= 6) return 'bg-orange-100 text-orange-800';
    if (rating <= 8) return 'bg-yellow-100 text-yellow-800';
    return 'bg-green-100 text-green-800';
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">🔒</div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Login Required</h2>
          <p className="text-gray-600 mb-4">Please log in to view your reviews</p>
          <Link 
            to="/login"
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg inline-block"
          >
            Log In
          </Link>
        </div>
      </div>
    );
  }

  if (loading && reviews.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your reviews...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            My Reviews
          </h1>
          <p className="text-gray-600">
            Manage and track all your book reviews
          </p>
        </div>

        {/* Statistics */}
        {statistics && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Your Statistics</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600 mb-1">
                  {statistics.total_reviews}
                </div>
                <div className="text-sm text-gray-600">Total Reviews</div>
              </div>
              
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-600 mb-1">
                  {statistics.average_rating.toFixed(1)}
                </div>
                <div className="text-sm text-gray-600">Average Rating</div>
              </div>
              
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600 mb-1">
                  {statistics.highest_rating}
                </div>
                <div className="text-sm text-gray-600">Highest Given</div>
              </div>
              
              <div className="text-center">
                <div className="text-3xl font-bold text-red-600 mb-1">
                  {statistics.lowest_rating}
                </div>
                <div className="text-sm text-gray-600">Lowest Given</div>
              </div>
            </div>
          </div>
        )}

        {/* Filters and Sorting */}
        <div className="bg-white rounded-lg shadow-md p-4 mb-6 flex flex-col sm:flex-row gap-4 items-center justify-between">
          <div className="flex flex-wrap gap-4 items-center">
            {/* Sort by */}
            <div className="flex items-center gap-2">
              <label className="text-sm font-medium text-gray-700">Sort by:</label>
              <select
                value={sortBy}
                onChange={(e) => {
                  setSortBy(e.target.value);
                  setPage(1);
                }}
                className="px-3 py-1 border border-gray-300 rounded text-sm"
              >
                <option value="-created_at">Newest First</option>
                <option value="created_at">Oldest First</option>
                <option value="-rating">Highest Rating</option>
                <option value="rating">Lowest Rating</option>
                <option value="book__title">Book Title (A-Z)</option>
              </select>
            </div>

            {/* Rating Filter */}
            <div className="flex items-center gap-2">
              <label className="text-sm font-medium text-gray-700">Filter:</label>
              <select
                value={ratingFilter || ''}
                onChange={(e) => {
                  setRatingFilter(e.target.value ? parseInt(e.target.value) : null);
                  setPage(1);
                }}
                className="px-3 py-1 border border-gray-300 rounded text-sm"
              >
                <option value="">All Ratings</option>
                {[10, 9, 8, 7, 6, 5, 4, 3, 2, 1].map(rating => (
                  <option key={rating} value={rating}>{rating}★</option>
                ))}
              </select>
            </div>
          </div>

          <div className="text-sm text-gray-600">
            {reviews.length > 0 && (
              <>Showing {((page - 1) * 12) + 1}-{Math.min(page * 12, statistics?.total_reviews || 0)} of {statistics?.total_reviews || 0}</>
            )}
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800 mb-6">
            {error}
          </div>
        )}

        {/* Edit Form Modal */}
        {editingReview && (
          <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6">
              <ReviewForm
                book={editingReview.book}
                existingReview={editingReview}
                onSuccess={handleReviewUpdate}
                onCancel={() => setEditingReview(null)}
              />
            </div>
          </div>
        )}

        {/* Reviews Grid */}
        {reviews.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg shadow-md">
            <div className="text-6xl mb-4">📝</div>
            <h3 className="text-xl font-semibold text-gray-800 mb-2">No Reviews Yet</h3>
            <p className="text-gray-600 mb-6">
              {ratingFilter 
                ? `You haven't given any ${ratingFilter}★ ratings yet`
                : "You haven't reviewed any books yet. Start exploring!"}
            </p>
            <Link
              to="/"
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg inline-block"
            >
              Browse Books
            </Link>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
              {reviews.map((review) => (
                <div 
                  key={review.id} 
                  className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow"
                >
                  {/* Book Preview */}
                  <div 
                    className="cursor-pointer"
                    onClick={() => navigate(`/book/${review.book.id}`)}
                  >
                    <BookCard book={review.book} />
                  </div>

                  {/* Review Info */}
                  <div className="p-4 border-t border-gray-200">
                    {/* Rating */}
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex gap-1">
                        {renderStars(review.rating)}
                      </div>
                      <span className={`px-2 py-1 rounded text-sm font-semibold ${getRatingColor(review.rating)}`}>
                        {review.rating}/10
                      </span>
                    </div>

                    {/* Review Text */}
                    {review.review_text && (
                      <p className="text-gray-700 text-sm mb-3 line-clamp-3">
                        {review.review_text}
                      </p>
                    )}

                    {/* Date */}
                    <div className="text-xs text-gray-500 mb-3">
                      {formatDate(review.created_at)}
                      {review.updated_at !== review.created_at && ' (edited)'}
                    </div>

                    {/* Actions */}
                    <button
                      onClick={() => setEditingReview(review)}
                      className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded text-sm font-medium transition-colors"
                    >
                      Edit Review
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex justify-center items-center gap-2">
                <button
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="px-4 py-2 bg-white rounded-lg shadow disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                >
                  Previous
                </button>
                
                <span className="text-gray-600 px-4">
                  Page {page} of {totalPages}
                </span>
                
                <button
                  onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  className="px-4 py-2 bg-white rounded-lg shadow disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default UserReviews;