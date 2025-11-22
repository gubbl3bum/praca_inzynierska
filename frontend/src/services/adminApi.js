const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const getAuthHeaders = () => {
  const tokens = localStorage.getItem('wolfread_tokens');
  const token = tokens ? JSON.parse(tokens).access : null;
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  };
};

const adminApi = {
  getDashboardStats: async () => {
    const response = await fetch(`${API_BASE_URL}/admin/dashboard/stats/`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch stats');
    return response.json();
  },

  getSystemHealth: async () => {
    const response = await fetch(`${API_BASE_URL}/admin/system/health/`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch health');
    return response.json();
  },

  recalculateBookSimilarities: async (options = {}) => {
    const response = await fetch(`${API_BASE_URL}/admin/similarities/books/recalculate/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(options)
    });
    if (!response.ok) throw new Error('Failed to recalculate');
    return response.json();
  },

  recalculateUserSimilarities: async (options = {}) => {
    const response = await fetch(`${API_BASE_URL}/admin/similarities/users/recalculate/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(options)
    });
    if (!response.ok) throw new Error('Failed to recalculate');
    return response.json();
  },

  getUsers: async (params = {}) => {
    const queryString = new URLSearchParams(params).toString();
    const url = queryString ? `${API_BASE_URL}/admin/users/?${queryString}` : `${API_BASE_URL}/admin/users/`;
    
    const response = await fetch(url, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch users');
    return response.json();
  },

  toggleUserStatus: async (userId) => {
    const response = await fetch(`${API_BASE_URL}/admin/users/${userId}/toggle-status/`, {
      method: 'POST',
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to toggle user status');
    return response.json();
  }
};

export default adminApi;