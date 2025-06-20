// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Generic API call function
const apiCall = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`API call failed for ${endpoint}:`, error);
    throw error;
  }
};

// Books API functions
export const booksAPI = {
  // Get featured books for home page
  getFeatured: () => apiCall('/books/featured/'),
  
  // Get all books with pagination and filters
  getBooks: (params = {}) => {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = queryString ? `/books/?${queryString}` : '/books/';
    return apiCall(endpoint);
  },
  
  // Get single book details
  getBook: (id) => apiCall(`/books/${id}/`),
  
  // Search books
  searchBooks: (query, params = {}) => {
    const allParams = { q: query, ...params };
    const queryString = new URLSearchParams(allParams).toString();
    return apiCall(`/books/search/?${queryString}`);
  },
  
  // Get Open Library information for a book
  getOpenLibraryInfo: (bookId) => apiCall(`/books/${bookId}/open-library/`),
  
  // Get Open Library covers for ISBN
  getOpenLibraryCovers: (isbn) => apiCall(`/open-library/covers/${isbn}/`),
  
  // Refresh covers for books
  refreshCovers: (limit = 50) => apiCall('/books/refresh-covers/', {
    method: 'POST',
    body: JSON.stringify({ limit })
  })
};

// ML API functions
export const mlAPI = {
  // Make prediction
  predict: (features) => apiCall('/predict/', {
    method: 'POST',
    body: JSON.stringify(features)
  }),
  
  // Get prediction history
  getHistory: () => apiCall('/history/'),
  
  // Get API status
  getStatus: () => apiCall('/status/')
};

// Open Library utilities
export const openLibraryUtils = {
  // Generate cover URLs for different sizes
  getCoverUrls: (isbn) => {
    if (!isbn) return null;
    
    const cleanIsbn = isbn.replace(/[-\s]/g, '');
    const baseUrl = 'https://covers.openlibrary.org/b/isbn';
    
    return {
      small: `${baseUrl}/${cleanIsbn}-S.jpg`,
      medium: `${baseUrl}/${cleanIsbn}-M.jpg`,
      large: `${baseUrl}/${cleanIsbn}-L.jpg`
    };
  },
  
  // Get Open Library book URL
  getBookUrl: (openLibraryId, isbn) => {
    if (openLibraryId) {
      return `https://openlibrary.org${openLibraryId}`;
    } else if (isbn) {
      const cleanIsbn = isbn.replace(/[-\s]/g, '');
      return `https://openlibrary.org/isbn/${cleanIsbn}`;
    }
    return null;
  },
  
  // Check if cover exists
  checkCoverExists: async (url) => {
    try {
      const response = await fetch(url, { method: 'HEAD' });
      return response.ok;
    } catch {
      return false;
    }
  },
  
  // Get best available cover from multiple sources
  getBestCover: async (book) => {
    // Priority: stored URLs first, then Open Library generated URLs
    const candidates = [
      book.image_url_m,
      book.image_url_l,
      book.image_url_s,
      book.best_cover_medium,
      book.best_cover_large,
      book.best_cover_small
    ].filter(Boolean);
    
    for (const url of candidates) {
      if (await openLibraryUtils.checkCoverExists(url)) {
        return url;
      }
    }
    
    return null;
  }
};

// Error handling helper
export const handleApiError = (error, fallbackMessage = 'Something went wrong') => {
  if (error.message.includes('HTTP error')) {
    const status = error.message.match(/status: (\d+)/)?.[1];
    switch (status) {
      case '404':
        return 'Not found';
      case '500':
        return 'Server error';
      case '403':
        return 'Access denied';
      default:
        return `Error ${status}`;
    }
  }
  
  if (error.message.includes('Failed to fetch')) {
    return 'Network error - please check your connection';
  }
  
  return error.message || fallbackMessage;
};

// Export default API object
const api = {
  books: booksAPI,
  ml: mlAPI,
  openLibrary: openLibraryUtils,
  handleError: handleApiError
};

export default api;