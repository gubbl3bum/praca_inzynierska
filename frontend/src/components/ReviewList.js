import React, { useState, useEffect } from 'react';
import { useAuth } from '../services/AuthContext';
import api from '../services/api';
import ReviewForm from './ReviewForm';

const ReviewList = ({ bookId }) => {
  const { isAuthenticated, user } = useAuth();
  const [reviews, setReviews] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [ratingFilter, setRatingFilter] = useState(null);
  const [userReview, setUserReview] = useState(null);
  const [showReviewForm, setShowReviewForm] = useState(false);
  const [editingReview, setEditingReview] = useState(null);

  useEffect(() => {
    fetchReviews();
  }, [bookId, page, ratingFilter]);

  useEffect(() => {
    if (isAuthenticated) {
      checkUserReview();
    }
  }, [bookId, isAuthenticated]);

  const fetchReviews = async () => {
    try {
      setLoading(true);
      setError(null);

      const params = {
        page: page,
        page_size: 10
      };

      if (ratingFilter) {
        params.rating = ratingFilter;
      }

      const response = await api.reviews.getBookReviews(bookId, params);

      if (response.status === 'success') {
        setReviews(response.reviews || []);
        setStatistics(response.statistics || null);
        setTotalPages(response.pagination?.total_pages || 1);
      }
    } catch (err) {
      console.error('Error fetching reviews:', err);
      setError(api.handleError(err, 'Failed to load reviews'));
    } finally {
      setLoading(false);
    }
  };

  const checkUserReview = async () => {
    try {
      const token = localStorage.getItem('wolfread_tokens');
      const tokens = token ? JSON.parse(token) : null;
      
      if (!tokens?.access) return;

      const response = await api.reviews.checkUserReview(bookId, tokens.access);
      
      if (response.status === 'success' && response.has_reviewed) {
        setUserReview(response.review);
      } else {
        setUserReview(null);
      }
    } catch (err) {
      console.error('Error checking user review:', err);
    }
  };

  const handleReviewSuccess = (review) => {
    if (review === null) {
      // Review deleted
      setUserReview(null);
      setEditingReview(null);
    } else {
      // Review created or updated
      setUserReview(review);
      setEditingReview(null);
    }
    
    setShowReviewForm(false);
    fetchReviews(); // Refresh list
  };

  const renderStars = (rating) => {
    const stars = [];
    for (let i = 1; i <= 10; i++) {
      stars.push(
        <span 
          key={i} 
          className={`text-lg ${i <= rating ? 'text-yellow-400' : 'text-gray-300'}`}
        >
          ★
        </span>
      );
    }
    return stars;
  };

  const getRatingColor = (rating) => {
    if (rating <= 4) return 'text-red-600';
    if (rating <= 6) return 'text-orange-600';
    if (rating <= 8) return 'text-yellow-600';
    return 'text-green-600';
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };

  const renderRatingDistribution = () => {
    if (!statistics?.rating_distribution) return null;

    const distribution = statistics.rating_distribution;
    const maxCount = Math.max(...Object.values(distribution));

    return (
      <div className="space-y-2">
        {[10, 9, 8, 7, 6, 5, 4, 3, 2, 1].map(rating => {
          const count = distribution[rating] || 0;
          const percentage = maxCount > 0 ? (count / maxCount) * 100 : 0;

          return (
            <div key={rating} className="flex items-center gap-2">
              <button
                onClick={() => setRatingFilter(ratingFilter === rating ? null : rating)}
                className={`w-8 text-sm font-medium ${
                  ratingFilter === rating ? 'text-blue-600' : 'text-gray-600 hover:text-blue-600'
                }`}
              >
                {rating}★
              </button>
              
              <div className="flex-1 bg-gray-200 rounded-full h-4 relative overflow-hidden">
                <div 
                  className="bg-yellow-400 h-full transition-all duration-300"
                  style={{ width: `${percentage}%` }}
                ></div>
              </div>
              
              <span className="text-sm text-gray-600 w-8 text-right">{count}</span>
            </div>
          );
        })}
      </div>
    );
  };

  if (loading && reviews.length === 0) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
        <p className="text-gray-600">Loading reviews...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Statistics Overview */}
      {statistics && (
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Average Rating */}
            <div className="text-center">
              <div className="text-4xl font-bold text-gray-800 mb-1">
                {statistics.average_rating.toFixed(1)}
              </div>
              <div className="flex justify-center gap-1 mb-1">
                {renderStars(Math.round(statistics.average_rating))}
              </div>
              <div className="text-sm text-gray-600">Average Rating</div>
            </div>

            {/* Total Reviews */}
            <div className="text-center">
              <div className="text-4xl font-bold text-gray-800 mb-1">
                {statistics.total_reviews}
              </div>
              <div className="text-sm text-gray-600">Total Reviews</div>
            </div>

            {/* Highest Rating */}
            <div className="text-center">
              <div className="text-4xl font-bold text-green-600 mb-1">
                {statistics.max_rating}
              </div>
              <div className="text-sm text-gray-600">Highest Rating</div>
            </div>

            {/* Lowest Rating */}
            <div className="text-center">
              <div className="text-4xl font-bold text-red-600 mb-1">
                {statistics.min_rating}
              </div>
              <div className="text-sm text-gray-600">Lowest Rating</div>
            </div>
          </div>

          {/* Rating Distribution */}
          <div className="mt-6 pt-6 border-t border-gray-200">
            <h4 className="font-semibold text-gray-800 mb-3">Rating Distribution</h4>
            {renderRatingDistribution()}
            {ratingFilter && (
              <button
                onClick={() => setRatingFilter(null)}
                className="mt-3 text-sm text-blue-600 hover:text-blue-800"
              >
                Clear filter
              </button>
            )}
          </div>
        </div>
      )}

      {/* User's Review Section */}
      {isAuthenticated && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          {userReview && !editingReview ? (
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-800">Your Review</h3>
                <button
                  onClick={() => setEditingReview(userReview)}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm"
                >
                  Edit Review
                </button>
              </div>
              
              <div className="bg-white rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <div className="flex gap-1">
                    {renderStars(userReview.rating)}
                  </div>
                  <span className={`font-semibold ${getRatingColor(userReview.rating)}`}>
                    {userReview.rating}/10
                  </span>
                </div>
                
                {userReview.review_text && (
                  <p className="text-gray-700 mt-3">{userReview.review_text}</p>
                )}
                
                <div className="text-xs text-gray-500 mt-3">
                  Posted on {formatDate(userReview.created_at)}
                  {userReview.updated_at !== userReview.created_at && (
                    <span> (edited {formatDate(userReview.updated_at)})</span>
                  )}
                </div>
              </div>
            </div>
          ) : editingReview ? (
            <ReviewForm
              book={{ id: bookId }}
              existingReview={editingReview}
              onSuccess={handleReviewSuccess}
              onCancel={() => setEditingReview(null)}
            />
          ) : showReviewForm ? (
            <ReviewForm
              book={{ id: bookId }}
              onSuccess={handleReviewSuccess}
              onCancel={() => setShowReviewForm(false)}
            />
          ) : (
            <div className="text-center">
              <p className="text-gray-700 mb-4">You haven't reviewed this book yet</p>
              <button
                onClick={() => setShowReviewForm(true)}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg"
              >
                Write a Review
              </button>
            </div>
          )}
        </div>
      )}

      {/* Reviews List */}
      <div>
        <h3 className="text-xl font-semibold text-gray-800 mb-4">
          All Reviews {ratingFilter && `(${ratingFilter}★)`}
        </h3>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800 mb-4">
            {error}
          </div>
        )}

        {reviews.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <div className="text-4xl mb-2">📝</div>
            <p className="mb-4">
              {ratingFilter 
                ? `No reviews with ${ratingFilter}★ rating`
                : 'No reviews yet. Be the first to review this book!'}
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {reviews.map((review) => (
              <div 
                key={review.id} 
                className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <div className="font-semibold text-gray-800">
                      {review.user?.username || 'Anonymous'}
                    </div>
                    <div className="text-xs text-gray-500">
                      {formatDate(review.created_at)}
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <div className="flex gap-1">
                      {renderStars(review.rating)}
                    </div>
                    <span className={`font-bold text-lg ${getRatingColor(review.rating)}`}>
                      {review.rating}/10
                    </span>
                  </div>
                </div>

                {review.review_text && (
                  <p className="text-gray-700 leading-relaxed">
                    {review.review_text}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex justify-center items-center gap-2 mt-6">
            <button
              onClick={() => setPage(page - 1)}
              disabled={page === 1}
              className="px-4 py-2 bg-gray-200 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-300"
            >
              Previous
            </button>
            
            <span className="text-gray-600">
              Page {page} of {totalPages}
            </span>
            
            <button
              onClick={() => setPage(page + 1)}
              disabled={page === totalPages}
              className="px-4 py-2 bg-gray-200 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-300"
            >
              Next
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ReviewList;