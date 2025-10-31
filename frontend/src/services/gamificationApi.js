import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const gamificationApi = {
  // ==========================================================================
  // BADGES
  // ==========================================================================
  
  /**
   * Get all available badges
   * @param {object} params - Query parameters (category, rarity, group_by_category)
   * @returns {Promise} Badges list
   */
  getBadges: async (params = {}) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/gamification/badges/`, { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching badges:', error);
      throw error;
    }
  },

  /**
   * Get user's badges with progress
   * @param {string} token - Auth token
   * @param {object} params - Query parameters (completed, category)
   * @returns {Promise} User's badges
   */
  getUserBadges: async (token, params = {}) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/gamification/badges/my/`, {
        headers: { 'Authorization': `Bearer ${token}` },
        params
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching user badges:', error);
      throw error;
    }
  },

  /**
   * Manually check for new badges
   * @param {string} token - Auth token
   * @returns {Promise} Newly earned badges
   */
  checkBadges: async (token) => {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/gamification/badges/check/`,
        {},
        { headers: { 'Authorization': `Bearer ${token}` } }
      );
      return response.data;
    } catch (error) {
      console.error('Error checking badges:', error);
      throw error;
    }
  },

  /**
   * Toggle badge showcase status
   * @param {number} badgeId - Badge ID
   * @param {string} token - Auth token
   * @returns {Promise} Updated showcase status
   */
  toggleShowcase: async (badgeId, token) => {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/gamification/badges/${badgeId}/showcase/`,
        {},
        { headers: { 'Authorization': `Bearer ${token}` } }
      );
      return response.data;
    } catch (error) {
      console.error('Error toggling showcase:', error);
      throw error;
    }
  },

  /**
   * Get next badges user is close to earning
   * @param {string} token - Auth token
   * @param {number} limit - Number of badges to return
   * @returns {Promise} Next badges
   */
  getNextBadges: async (token, limit = 5) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/gamification/badges/next/`, {
        headers: { 'Authorization': `Bearer ${token}` },
        params: { limit }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching next badges:', error);
      throw error;
    }
  },

  /**
   * Get badge categories
   * @returns {Promise} Badge categories with counts
   */
  getCategories: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/gamification/badges/categories/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching categories:', error);
      throw error;
    }
  },

  // ==========================================================================
  // STATISTICS
  // ==========================================================================

  /**
   * Get user statistics
   * @param {string} token - Auth token
   * @returns {Promise} User statistics
   */
  getStatistics: async (token) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/gamification/statistics/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching statistics:', error);
      throw error;
    }
  },

  /**
   * Get complete gamification profile
   * @param {string} token - Auth token
   * @returns {Promise} Complete profile with stats, badges, achievements
   */
  getProfile: async (token) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/gamification/profile/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching gamification profile:', error);
      throw error;
    }
  },

  // ==========================================================================
  // ACHIEVEMENTS
  // ==========================================================================

  /**
   * Get user achievements
   * @param {string} token - Auth token
   * @returns {Promise} User achievements
   */
  getAchievements: async (token) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/gamification/achievements/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching achievements:', error);
      throw error;
    }
  },

  // ==========================================================================
  // LEADERBOARD
  // ==========================================================================

  /**
   * Get leaderboard
   * @param {object} params - Query parameters (period, category, limit)
   * @returns {Promise} Leaderboard data
   */
  getLeaderboard: async (params = {}) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/gamification/leaderboard/`, { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching leaderboard:', error);
      throw error;
    }
  },

  /**
   * Get user's rank
   * @param {string} token - Auth token
   * @returns {Promise} User's rank across leaderboards
   */
  getUserRank: async (token) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/gamification/leaderboard/my-rank/`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching user rank:', error);
      throw error;
    }
  }
};

export default gamificationApi;