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
    console.log(`API call: ${url}`); // Debug
    const response = await fetch(url, config);
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
    }
    
    const data = await response.json();
    console.log(`API response for ${endpoint}:`, data); // Debug
    return data;
  } catch (error) {
    console.error(`API call failed for ${endpoint}:`, error);
    throw error;
  }
};

// Books API functions
export const booksAPI = {
  // Get featured books for home page
  getFeatured: async () => {
    const response = await apiCall('/books/featured/');
    // Backend zwraca obiekt z top_rated, recent, popular
    return {
      top_rated: response.top_rated || [],
      recent: response.recent || [],
      popular: response.popular || []
    };
  },
  
  // Get all books with pagination and filters
  getBooks: (params = {}) => {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = queryString ? `/books/?${queryString}` : '/books/';
    return apiCall(endpoint);
  },
  
  // Get top rated books with pagination
  getTopRated: (params = {}) => {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = queryString ? `/books/top-rated/?${queryString}` : '/books/top-rated/';
    return apiCall(endpoint);
  },
  
  // Get single book details
  getBook: (id) => apiCall(`/books/${id}/`),
  
  // Search books
  searchBooks: (query, params = {}) => {
    const allParams = { search: query, ...params };
    const queryString = new URLSearchParams(allParams).toString();
    return apiCall(`/books/?${queryString}`);
  },
  
  // NEW SIMILARITY METHODS
  getSimilarBooks: (bookId, params = {}) => {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = queryString 
      ? `/books/${bookId}/recommendations/?${queryString}` 
      : `/books/${bookId}/recommendations/`;
    console.log(`🔍 Calling similar books API: ${endpoint}`);
    return apiCall(endpoint);
  },
  
  // Alias for similar books
  getRecommendations: (bookId, params = {}) => {
    return booksAPI.getSimilarBooks(bookId, params);
  },
  
  // Get similarity statistics
  getSimilarityStats: () => apiCall('/similarities/stats/'),
  
  // Force recalculation of similarities
  recalculateSimilarities: (bookId = null, options = {}) => {
    const endpoint = bookId 
      ? `/similarities/recalculate/${bookId}/`
      : '/similarities/recalculate/';
    
    return apiCall(endpoint, {
      method: 'POST',
      body: JSON.stringify(options)
    });
  },
  
  // Legacy compatibility functions
  getOpenLibraryInfo: (bookId) => {
    console.warn('getOpenLibraryInfo not implemented yet');
    return Promise.resolve({});
  },
  
  getOpenLibraryCovers: (isbn) => {
    console.warn('getOpenLibraryCovers not implemented yet');
    return Promise.resolve({});
  },
  
  refreshCovers: (limit = 50) => {
    console.warn('refreshCovers not implemented yet');
    return Promise.resolve({});
  }
};

// Categories API
export const categoriesAPI = {
  getCategories: () => apiCall('/categories/')
};

// Status API
export const statusAPI = {
  getStatus: () => apiCall('/status/')
};

// ML API functions (zachowane dla kompatybilności)
export const mlAPI = {
  predict: (features) => {
    console.warn('ML prediction not implemented yet');
    return Promise.resolve({});
  },
  
  getHistory: () => {
    console.warn('ML history not implemented yet');
    return Promise.resolve([]);
  },
  
  getStatus: () => statusAPI.getStatus()
};

// Pagination utilities
export const paginationUtils = {
  // Create pagination info from API response
  createPaginationInfo: (apiResponse) => {
    return {
      currentPage: apiResponse.current_page || 1,
      totalPages: apiResponse.num_pages || 1,
      totalItems: apiResponse.count || 0,
      hasNext: apiResponse.has_next || false,
      hasPrevious: apiResponse.has_previous || false,
      nextPage: apiResponse.next_page || null,
      previousPage: apiResponse.previous_page || null,
      pageSize: apiResponse.page_size || 20
    };
  },
  
  // Generate page numbers for pagination display
  generatePageNumbers: (currentPage, totalPages, maxVisible = 5) => {
    const pages = [];
    const start = Math.max(1, currentPage - Math.floor(maxVisible / 2));
    const end = Math.min(totalPages, start + maxVisible - 1);
    
    for (let i = start; i <= end; i++) {
      pages.push(i);
    }
    
    return pages;
  }
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
    const candidates = [
      book.cover_image_url,
      book.best_cover_medium,
      book.image_url_m,
      book.image_url_l,
      book.image_url_s,
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
  console.error('API Error:', error);
  
  if (error.message.includes('HTTP error')) {
    const status = error.message.match(/status: (\d+)/)?.[1];
    switch (status) {
      case '404':
        return 'Not found';
      case '500':
        return 'Server error - please try again later';
      case '403':
        return 'Access denied';
      case '400':
        return 'Bad request - please check your input';
      default:
        return `Error ${status} - please try again`;
    }
  }
  
  if (error.message.includes('Failed to fetch')) {
    return 'Network error - please check your connection and try again';
  }
  
  if (error.message.includes('NetworkError')) {
    return 'Cannot connect to server - please check if the backend is running';
  }
  
  return error.message || fallbackMessage;
};

// Data transformation utilities
export const dataUtils = {
  // Normalize book data from different API responses
  normalizeBook: (book) => {
    if (!book) return null;
    
    return {
      id: book.id,
      title: book.title || 'Unknown Title',
      authors: book.authors || book.author || 'Unknown Author',
      author: book.author || (book.authors ? (Array.isArray(book.authors) ? book.authors[0] : book.authors) : 'Unknown Author'),
      description: book.description,
      categories: book.categories || book.category_names || [],
      average_rating: Number(book.average_rating || 0),
      ratings_count: Number(book.ratings_count || 0),
      price: book.price,
      publish_year: book.publish_year || book.publication_year,
      publication_year: book.publication_year || book.publish_year,
      cover_image_url: book.cover_image_url,
      best_cover_medium: book.best_cover_medium || book.cover_image_url,
      best_cover_large: book.best_cover_large || book.cover_image_url,
      image_url_m: book.image_url_m || book.cover_image_url,
      image_url_l: book.image_url_l || book.cover_image_url,
      isbn: book.isbn,
      publisher: book.publisher,
      created_at: book.created_at,
      updated_at: book.updated_at,
      
      // Similarity specific fields
      similarity_score: book.similarity_score,
      similarity_details: book.similarity_details
    };
  },
  
  // Normalize API response structure
  normalizeApiResponse: (response) => {
    // Handle different response structures
    if (response.results) {
      return {
        ...response,
        results: response.results.map(dataUtils.normalizeBook)
      };
    }
    
    if (Array.isArray(response)) {
      return response.map(dataUtils.normalizeBook);
    }
    
    if (response.books) {
      return {
        ...response,
        books: response.books.map(dataUtils.normalizeBook)
      };
    }
    
    if (response.recommendations) {
      return {
        ...response,
        recommendations: response.recommendations.map(dataUtils.normalizeBook)
      };
    }
    
    return response;
  }
};

// Export default API object
const api = {
  books: booksAPI,
  categories: categoriesAPI,
  status: statusAPI,
  ml: mlAPI,
  openLibrary: openLibraryUtils,
  pagination: paginationUtils,
  data: dataUtils,
  handleError: handleApiError
};

export default api;