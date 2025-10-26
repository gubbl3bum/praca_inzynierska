import React, { useState, useEffect } from 'react';
import { useAuth } from '../services/AuthContext';
import api from '../services/api';

const ReviewForm = ({ book, existingReview = null, onSuccess, onCancel }) => {
  const { isAuthenticated } = useAuth();
  const [rating, setRating] = useState(existingReview?.rating || 0);
  const [hoverRating, setHoverRating] = useState(0);
  const [reviewText, setReviewText] = useState(existingReview?.review_text || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const isEditMode = !!existingReview;

  useEffect(() => {
    if (existingReview) {
      setRating(existingReview.rating);
      setReviewText(existingReview.review_text || '');
    }
  }, [existingReview]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!rating) {
      setError('Please select a rating');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const token = localStorage.getItem('wolfread_tokens');
      const tokens = token ? JSON.parse(token) : null;
      
      if (!tokens?.access) {
        setError('Please log in to submit a review');
        return;
      }

      const reviewData = {
        rating: rating,
        review_text: reviewText.trim()
      };

      let response;
      if (isEditMode) {
        // Update existing review
        response = await api.reviews.updateReview(
          existingReview.id,
          reviewData,
          tokens.access
        );
      } else {
        // Create new review
        response = await api.reviews.createReview(
          book.id,
          reviewData,
          tokens.access
        );
      }

      if (response.status === 'success') {
        setSuccess(true);
        setError(null);
        
        // Callback po sukcesie
        if (onSuccess) {
          onSuccess(response.review);
        }
        
        // Reset form if creating new review
        if (!isEditMode) {
          setRating(0);
          setReviewText('');
        }
      }
    } catch (err) {
      console.error('Error submitting review:', err);
      const errorMessage = api.handleError(err, 'Failed to submit review');
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this review?')) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('wolfread_tokens');
      const tokens = token ? JSON.parse(token) : null;
      
      if (!tokens?.access) {
        setError('Please log in to delete a review');
        return;
      }

      const response = await api.reviews.deleteReview(
        existingReview.id,
        tokens.access
      );

      if (response.status === 'success') {
        if (onSuccess) {
          onSuccess(null); // null = deleted
        }
      }
    } catch (err) {
      console.error('Error deleting review:', err);
      const errorMessage = api.handleError(err, 'Failed to delete review');
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const renderStarRating = () => {
    const stars = [];
    const displayRating = hoverRating || rating;

    for (let i = 1; i <= 10; i++) {
      stars.push(
        <button
          key={i}
          type="button"
          onClick={() => setRating(i)}
          onMouseEnter={() => setHoverRating(i)}
          onMouseLeave={() => setHoverRating(0)}
          className={`text-2xl transition-all ${
            i <= displayRating 
              ? 'text-yellow-400 scale-110' 
              : 'text-gray-300 hover:text-yellow-200'
          }`}
        >
          ★
        </button>
      );
    }

    return stars;
  };

  const getRatingLabel = (rating) => {
    if (rating === 0) return 'Select a rating';
    if (rating <= 2) return 'Poor';
    if (rating <= 4) return 'Below Average';
    if (rating <= 6) return 'Average';
    if (rating <= 8) return 'Good';
    return 'Excellent';
  };

  const getRatingColor = (rating) => {
    if (rating === 0) return 'text-gray-500';
    if (rating <= 4) return 'text-red-600';
    if (rating <= 6) return 'text-orange-600';
    if (rating <= 8) return 'text-yellow-600';
    return 'text-green-600';
  };

  if (!isAuthenticated) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
        <div className="text-4xl mb-2">🔒</div>
        <p className="text-gray-700 mb-4">
          Please log in to write a review for this book
        </p>
        <button
          onClick={() => window.location.href = '/login'}
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg"
        >
          Log In
        </button>
      </div>
    );
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6">
      <h3 className="text-xl font-semibold text-gray-800 mb-4">
        {isEditMode ? 'Edit Your Review' : 'Write a Review'}
      </h3>

      {success && (
        <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg text-green-800">
          ✅ Review {isEditMode ? 'updated' : 'submitted'} successfully!
        </div>
      )}

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-800">
          ❌ {error}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        {/* Rating */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Your Rating *
          </label>
          
          <div className="flex items-center gap-1 mb-2">
            {renderStarRating()}
          </div>
          
          <div className="flex items-center justify-between">
            <span className={`text-lg font-semibold ${getRatingColor(rating || hoverRating)}`}>
              {(hoverRating || rating) ? `${hoverRating || rating}/10` : '0/10'} 
              {' - '}
              {getRatingLabel(hoverRating || rating)}
            </span>
            
            {rating > 0 && (
              <button
                type="button"
                onClick={() => setRating(0)}
                className="text-xs text-gray-500 hover:text-gray-700"
              >
                Clear rating
              </button>
            )}
          </div>
        </div>

        {/* Review Text */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Your Review (Optional)
          </label>
          <textarea
            value={reviewText}
            onChange={(e) => setReviewText(e.target.value)}
            placeholder="Share your thoughts about this book... (optional)"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            rows={6}
            maxLength={5000}
          />
          <div className="text-xs text-gray-500 mt-1 text-right">
            {reviewText.length} / 5000 characters
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-between">
          <div className="flex gap-2">
            <button
              type="submit"
              disabled={loading || !rating}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <span className="animate-spin">⏳</span>
                  {isEditMode ? 'Updating...' : 'Submitting...'}
                </span>
              ) : (
                <span>{isEditMode ? 'Update Review' : 'Submit Review'}</span>
              )}
            </button>

            {onCancel && (
              <button
                type="button"
                onClick={onCancel}
                disabled={loading}
                className="bg-gray-200 hover:bg-gray-300 text-gray-700 px-6 py-2 rounded-lg disabled:opacity-50 transition-colors"
              >
                Cancel
              </button>
            )}
          </div>

          {isEditMode && (
            <button
              type="button"
              onClick={handleDelete}
              disabled={loading}
              className="bg-red-600 hover:bg-red-700 text-white px-6 py-2 rounded-lg disabled:opacity-50 transition-colors"
            >
              Delete Review
            </button>
          )}
        </div>
      </form>

      {/* Book Info (for context) */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <div className="flex items-center gap-4">
          {book.cover_image_url && (
            <img 
              src={book.cover_image_url} 
              alt={book.title}
              className="w-16 h-24 object-cover rounded"
            />
          )}
          <div>
            <h4 className="font-semibold text-gray-800">{book.title}</h4>
            <p className="text-sm text-gray-600">
              {typeof book.authors === 'string' 
                ? book.authors 
                : book.author || 'Unknown Author'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReviewForm;