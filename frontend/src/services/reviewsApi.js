// frontend/src/services/reviewsApi.js
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const reviewsApi = {
  // ============================================================================
  // BOOK REVIEWS
  // ============================================================================
  
  /**
   * Get all reviews for a specific book
   * @param {number} bookId - Book ID
   * @param {object} params - Query parameters (page, page_size, rating)
   * @returns {Promise} Reviews list with statistics
   */
  getBookReviews: async (bookId, params = {}) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/reviews/book/${bookId}/`, {
        params: {
          page: params.page || 1,
          page_size: params.page_size || 10,
          rating: params.rating || null
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching book reviews:', error);
      throw error;
    }
  },

  /**
   * Create a new review for a book
   * @param {number} bookId - Book ID
   * @param {object} reviewData - Review data (rating, review_text)
   * @param {string} token - Auth token
   * @returns {Promise} Created review
   */
  createReview: async (bookId, reviewData, token) => {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/reviews/book/${bookId}/`,
        reviewData,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error creating review:', error);
      throw error;
    }
  },

  // ============================================================================
  // REVIEW MANAGEMENT
  // ============================================================================

  /**
   * Get review details by ID
   * @param {number} reviewId - Review ID
   * @returns {Promise} Review details
   */
  getReview: async (reviewId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/reviews/${reviewId}/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching review:', error);
      throw error;
    }
  },

  /**
   * Update a review
   * @param {number} reviewId - Review ID
   * @param {object} reviewData - Updated review data
   * @param {string} token - Auth token
   * @returns {Promise} Updated review
   */
  updateReview: async (reviewId, reviewData, token) => {
    try {
      const response = await axios.put(
        `${API_BASE_URL}/reviews/${reviewId}/`,
        reviewData,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error updating review:', error);
      throw error;
    }
  },

  /**
   * Delete a review
   * @param {number} reviewId - Review ID
   * @param {string} token - Auth token
   * @returns {Promise} Deletion confirmation
   */
  deleteReview: async (reviewId, token) => {
    try {
      const response = await axios.delete(
        `${API_BASE_URL}/reviews/${reviewId}/`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error deleting review:', error);
      throw error;
    }
  },

  // ============================================================================
  // USER REVIEWS
  // ============================================================================

  /**
   * Get all reviews by current user
   * @param {string} token - Auth token
   * @param {object} params - Query parameters (page, page_size, rating, sort_by)
   * @returns {Promise} User's reviews list
   */
  getUserReviews: async (token, params = {}) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/reviews/my-reviews/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        },
        params: {
          page: params.page || 1,
          page_size: params.page_size || 20,
          rating: params.rating || null,
          sort_by: params.sort_by || '-created_at'
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching user reviews:', error);
      throw error;
    }
  },

  /**
   * Check if user has reviewed a specific book
   * @param {number} bookId - Book ID
   * @param {string} token - Auth token
   * @returns {Promise} Review check result
   */
  checkUserReview: async (bookId, token) => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/reviews/check/${bookId}/`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error checking user review:', error);
      throw error;
    }
  },

  // ============================================================================
  // STATISTICS
  // ============================================================================

  /**
   * Get global review statistics
   * @returns {Promise} Review statistics
   */
  getStatistics: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/reviews/statistics/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching review statistics:', error);
      throw error;
    }
  },

  /**
   * Get highest rated books
   * @param {object} params - Query parameters (min_reviews, limit)
   * @returns {Promise} Highest rated books list
   */
  getHighestRated: async (params = {}) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/reviews/highest-rated/`, {
        params: {
          min_reviews: params.min_reviews || 5,
          limit: params.limit || 20
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching highest rated books:', error);
      throw error;
    }
  }
};

export default reviewsApi;