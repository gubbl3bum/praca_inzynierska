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
  },

  // BOOKS
  getBooks: async (params = {}) => {
    const queryString = new URLSearchParams(params).toString();
    const url = queryString ? `${API_BASE_URL}/admin/books/?${queryString}` : `${API_BASE_URL}/admin/books/`;
    
    const response = await fetch(url, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch books');
    return response.json();
  },

  getBook: async (bookId) => {
    const response = await fetch(`${API_BASE_URL}/admin/books/${bookId}/`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch book');
    return response.json();
  },

  updateBook: async (bookId, data) => {
    const response = await fetch(`${API_BASE_URL}/admin/books/${bookId}/`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Failed to update book');
    return response.json();
  },

  deleteBook: async (bookId) => {
    const response = await fetch(`${API_BASE_URL}/admin/books/${bookId}/`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to delete book');
    return response.json();
  },

  // REVIEWS
  getReviews: async (params = {}) => {
    const queryString = new URLSearchParams(params).toString();
    const url = queryString ? `${API_BASE_URL}/admin/reviews/?${queryString}` : `${API_BASE_URL}/admin/reviews/`;
    
    const response = await fetch(url, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch reviews');
    return response.json();
  },

  deleteReview: async (reviewId) => {
    const response = await fetch(`${API_BASE_URL}/admin/reviews/${reviewId}/`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to delete review');
    return response.json();
  },

  // BADGES
  getBadges: async () => {
    const response = await fetch(`${API_BASE_URL}/admin/badges/`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch badges');
    return response.json();
  },

  getBadge: async (badgeId) => {
    const response = await fetch(`${API_BASE_URL}/admin/badges/${badgeId}/`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch badge');
    return response.json();
  },

  updateBadge: async (badgeId, data) => {
    const response = await fetch(`${API_BASE_URL}/admin/badges/${badgeId}/`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Failed to update badge');
    return response.json();
  },

  deleteBadge: async (badgeId) => {
    const response = await fetch(`${API_BASE_URL}/admin/badges/${badgeId}/`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to delete badge');
    return response.json();
  },

  // CATEGORIES
  getCategories: async () => {
    const response = await fetch(`${API_BASE_URL}/admin/categories/`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch categories');
    return response.json();
  },

  createCategory: async (data) => {
    const response = await fetch(`${API_BASE_URL}/admin/categories/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Failed to create category');
    return response.json();
  },

  updateCategory: async (categoryId, data) => {
    const response = await fetch(`${API_BASE_URL}/admin/categories/${categoryId}/`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Failed to update category');
    return response.json();
  },

  deleteCategory: async (categoryId) => {
    const response = await fetch(`${API_BASE_URL}/admin/categories/${categoryId}/`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to delete category');
    return response.json();
  },
  
  // AUTHORS
  getAuthors: async (params = {}) => {
    const queryString = new URLSearchParams(params).toString();
    const url = queryString ? `${API_BASE_URL}/admin/authors/?${queryString}` : `${API_BASE_URL}/admin/authors/`;
    
    const response = await fetch(url, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch authors');
    return response.json();
  },

  getAuthor: async (authorId) => {
    const response = await fetch(`${API_BASE_URL}/admin/authors/${authorId}/`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch author');
    return response.json();
  },

  createAuthor: async (data) => {
    const response = await fetch(`${API_BASE_URL}/admin/authors/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Failed to create author');
    return response.json();
  },

  updateAuthor: async (authorId, data) => {
    const response = await fetch(`${API_BASE_URL}/admin/authors/${authorId}/`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Failed to update author');
    return response.json();
  },

  deleteAuthor: async (authorId) => {
    const response = await fetch(`${API_BASE_URL}/admin/authors/${authorId}/`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to delete author');
    return response.json();
  },

  // PUBLISHERS
  getPublishers: async (params = {}) => {
    const queryString = new URLSearchParams(params).toString();
    const url = queryString ? `${API_BASE_URL}/admin/publishers/?${queryString}` : `${API_BASE_URL}/admin/publishers/`;
    
    const response = await fetch(url, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch publishers');
    return response.json();
  },

  getPublisher: async (publisherId) => {
    const response = await fetch(`${API_BASE_URL}/admin/publishers/${publisherId}/`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to fetch publisher');
    return response.json();
  },

  createPublisher: async (data) => {
    const response = await fetch(`${API_BASE_URL}/admin/publishers/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Failed to create publisher');
    return response.json();
  },

  updatePublisher: async (publisherId, data) => {
    const response = await fetch(`${API_BASE_URL}/admin/publishers/${publisherId}/`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Failed to update publisher');
    return response.json();
  },

  deletePublisher: async (publisherId) => {
    const response = await fetch(`${API_BASE_URL}/admin/publishers/${publisherId}/`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error('Failed to delete publisher');
    return response.json();
  },
};

export default adminApi;