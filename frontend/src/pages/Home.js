import React, { useState, useEffect } from "react";
import BookCard from '../components/BookCard';
import api from '../services/api';

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
      const data = await api.books.getFeatured();
      setFeaturedBooks(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching featured books:', err);
      const errorMessage = api.handleError(err, 'Failed to load books');
      setError(errorMessage);
      
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

  const handleBookClick = (book) => {
    console.log('Clicked book:', book);
    // Navigation jest obsługiwana w BookCard
  };

  // Fallback sample data with Open Library integration
  const sampleBooks = [
    { 
      id: 1, 
      title: 'Pride and Prejudice', 
      author: 'Jane Austen', 
      isbn: '9780141439518',
      categories: ['Fiction', 'Romance'], 
      average_rating: 4.5,
      open_library_id: '/works/OL66554W'
    },
    { 
      id: 2, 
      title: 'To Kill a Mockingbird', 
      author: 'Harper Lee', 
      isbn: '9780061120084',
      categories: ['Fiction', 'Classic'], 
      average_rating: 4.2,
      open_library_id: '/works/OL4296W'
    },
    { 
      id: 3, 
      title: '1984', 
      author: 'George Orwell', 
      isbn: '9780451524935',
      categories: ['Fiction', 'Dystopian'], 
      average_rating: 4.7,
      open_library_id: '/works/OL1168007W'
    },
    { 
      id: 4, 
      title: 'The Great Gatsby', 
      author: 'F. Scott Fitzgerald', 
      isbn: '9780743273565',
      categories: ['Fiction', 'Classic'], 
      average_rating: 4.0,
      open_library_id: '/works/OL468431W'
    },
    { 
      id: 5, 
      title: 'The Hobbit', 
      author: 'J.R.R. Tolkien', 
      isbn: '9780547928227',
      categories: ['Fantasy', 'Adventure'], 
      average_rating: 4.3,
      open_library_id: '/works/OL262758W'
    },
    { 
      id: 6, 
      title: 'Harry Potter and the Philosopher\'s Stone', 
      author: 'J.K. Rowling', 
      isbn: '9780439708180',
      categories: ['Fantasy', 'Young Adult'], 
      average_rating: 4.8,
      open_library_id: '/works/OL82563W'
    },
    { 
      id: 7, 
      title: 'The Catcher in the Rye', 
      author: 'J.D. Salinger', 
      isbn: '9780316769488',
      categories: ['Fiction', 'Coming of Age'], 
      average_rating: 4.1,
      open_library_id: '/works/OL3335401W'
    },
    { 
      id: 8, 
      title: 'One Hundred Years of Solitude', 
      author: 'Gabriel García Márquez', 
      isbn: '9780452284234',
      categories: ['Fiction', 'Magical Realism'], 
      average_rating: 4.6,
      open_library_id: '/works/OL9756966W'
    },
  ];

  const BookSection = ({ title, books, icon }) => (
    <section className="mb-12">
      <h2 className="text-2xl font-semibold mb-6 text-gray-800 flex items-center gap-2">
        <span className="text-2xl">{icon}</span>
        {title}
      </h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {books
          .filter(book => book && book.id)
          .map((book) => (
            <BookCard
              key={book.id}
              book={book}  
              onClick={handleBookClick}
            />
          ))
        }
      </div>
    </section>
  );

  const handleRefreshCovers = async () => {
    try {
      setLoading(true);
      await api.books.refreshCovers(20); // Refresh covers for 20 books
      await fetchFeaturedBooks(); // Reload data
    } catch (err) {
      console.error('Error refreshing covers:', err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading amazing books...</p>
          <p className="text-sm text-gray-500 mt-2">Fetching covers from Open Library...</p>
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
          Powered by Open Library for the best book covers and information.
        </p>
        
        {error && (
          <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded mx-auto max-w-md mb-8">
            <p className="text-sm">{error}</p>
            <button 
              onClick={fetchFeaturedBooks}
              className="text-blue-600 hover:text-blue-800 underline text-sm mt-2"
            >
              Try again
            </button>
          </div>
        )}

        {/* Admin controls for development */}
        {process.env.NODE_ENV === 'development' && (
          <div className="mb-8">
            <button
              onClick={handleRefreshCovers}
              className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded text-sm"
            >
              Refresh Book Covers from Open Library
            </button>
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
            <button
              onClick={fetchFeaturedBooks}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded mt-4"
            >
              Refresh
            </button>
          </div>
        )}

        {/* Open Library Attribution */}
        <div className="text-center text-gray-500 text-sm mt-12 border-t pt-8">
          <p>Book covers and information powered by 
            <a 
              href="https://openlibrary.org" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 ml-1"
            >
              Open Library
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Home;