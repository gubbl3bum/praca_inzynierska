import React, { useState, useEffect } from "react";
import BookCard from '../components/BookCard';

const API_BASE_URL = 'http://localhost:8000/api';

const Home = () => {
  const [featuredBooks, setFeaturedBooks] = useState({
    top_rated: [],
    recent: [],
    popular: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchFeaturedBooks();
  }, []);

  const fetchFeaturedBooks = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/books/featured/`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setFeaturedBooks(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching featured books:', err);
      setError('Failed to load books. Please try again later.');
      
      // Fallback to sample data if API fails
      setFeaturedBooks({
        top_rated: sampleBooks.slice(0, 4),
        recent: sampleBooks.slice(4, 8),
        popular: sampleBooks.slice(0, 4)
      });
    } finally {
      setLoading(false);
    }
  };

  // Fallback sample data
  const sampleBooks = [
    { id: 1, title: 'Book 1', author: 'Author 1', cover_image: null, categories: 'Fiction', average_rating: 4.5 },
    { id: 2, title: 'Book 2', author: 'Author 2', cover_image: null, categories: 'Non-fiction', average_rating: 4.2 },
    { id: 3, title: 'Book 3', author: 'Author 3', cover_image: null, categories: 'Science', average_rating: 4.7 },
    { id: 4, title: 'Book 4', author: 'Author 4', cover_image: null, categories: 'History', average_rating: 4.0 },
    { id: 5, title: 'Book 5', author: 'Author 5', cover_image: null, categories: 'Fantasy', average_rating: 4.3 },
    { id: 6, title: 'Book 6', author: 'Author 6', cover_image: null, categories: 'Adventure', average_rating: 4.8 },
    { id: 7, title: 'Book 7', author: 'Author 7', cover_image: null, categories: 'Mystery', average_rating: 4.1 },
    { id: 8, title: 'Book 8', author: 'Author 8', cover_image: null, categories: 'Thriller', average_rating: 4.6 },
  ];

  const BookSection = ({ title, books, icon }) => (
    <section className="mb-12">
      <h2 className="text-2xl font-semibold mb-6 text-gray-800 flex items-center gap-2">
        <span className="text-2xl">{icon}</span>
        {title}
      </h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {books.map((book) => (
          <BookCard 
            key={book.id} 
            id={book.id}
            title={book.title}
            author={book.author}
            cover={book.cover_image}
            description={book.description || `A great book by ${book.author}`}
            rating={book.average_rating || '0.0'}
            category={book.categories_list ? book.categories_list[0] : book.categories}
          />
        ))}
      </div>
    </section>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading amazing books...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Hero Section */}
      <div className="text-center py-20 px-4">
        <h1 className="text-5xl font-extrabold bg-clip-text bg-gradient-to-r from-blue-700 to-indigo-500 mb-4">
          📚 WolfRead
        </h1>
        <p className="text-gray-600 mb-8 max-w-2xl mx-auto">
          Discover your next favorite book. Dive into fiction, explore science, or unravel a mystery.
        </p>
        
        {error && (
          <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded mx-auto max-w-md mb-8">
            <p className="text-sm">{error}</p>
          </div>
        )}
      </div>

      {/* Books Sections */}
      <div className="max-w-7xl mx-auto px-4 pb-20">
        {featuredBooks.top_rated.length > 0 && (
          <BookSection 
            title="Top Rated Books" 
            books={featuredBooks.top_rated} 
            icon="⭐"
          />
        )}
        
        {featuredBooks.recent.length > 0 && (
          <BookSection 
            title="Recently Added" 
            books={featuredBooks.recent} 
            icon="🆕"
          />
        )}
        
        {featuredBooks.popular.length > 0 && (
          <BookSection 
            title="Most Popular" 
            books={featuredBooks.popular} 
            icon="🔥"
          />
        )}
        
        {/* If no books available */}
        {featuredBooks.top_rated.length === 0 && featuredBooks.recent.length === 0 && featuredBooks.popular.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">No books available at the moment.</p>
            <p className="text-gray-400 text-sm mt-2">Please check back later or contact support.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Home;