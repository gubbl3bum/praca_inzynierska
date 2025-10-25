import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../services/AuthContext';
import BookCard from '../components/BookCard';
import AddToListButton from '../components/AddToListButton';
import api from '../services/api';

const UserFavorites = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [favoritesList, setFavoritesList] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    fetchFavorites();
  }, [isAuthenticated]);

  const fetchFavorites = async () => {
    try {
      setLoading(true);
      setError(null);

      const token = localStorage.getItem('wolfread_tokens');
      const tokens = token ? JSON.parse(token) : null;
      
      if (!tokens?.access) {
        navigate('/login');
        return;
      }

      const listsResponse = await api.lists.getLists(tokens.access);
      
      if (listsResponse.status === 'success') {
        const favList = listsResponse.lists?.find(list => list.list_type === 'favorites');
        
        if (favList) {
          const detailResponse = await api.lists.getListDetail(favList.id, tokens.access);
          
          if (detailResponse.status === 'success') {
            setFavoritesList(detailResponse.list);
          }
        } else {
          await api.lists.initializeDefaultLists(tokens.access);
          await fetchFavorites();
          return;
        }
      }
    } catch (err) {
      console.error('Error fetching favorites:', err);
      setError(api.handleError(err, 'Failed to load favorites'));
    } finally {
      setLoading(false);
    }
  };

  const handleFavoriteChange = async (isFavorite) => {
    // Odśwież listę po zmianie
    await fetchFavorites();
  };

  const handleBookClick = (book) => {
    console.log('Clicked favorite book:', book);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your favorites...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Error Loading Favorites</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={fetchFavorites}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            ❤️ Your Favorite Books
          </h1>
          <p className="text-gray-600">
            {favoritesList?.book_count || 0} book{favoritesList?.book_count !== 1 ? 's' : ''} in your favorites
          </p>
        </div>

        {favoritesList?.items && favoritesList.items.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
            {favoritesList.items.map((item) => (
              <div key={item.id} className="relative">
                <BookCard 
                  book={item.book}
                  onClick={handleBookClick}
                />
                
                {/* Serduszko do usuwania - teraz wbudowane w BookCard poprzez AddToListButton */}
                <div className="absolute top-2 left-2 z-10">
                  <AddToListButton 
                    book={item.book} 
                    compact={true}
                    onFavoriteChange={handleFavoriteChange}
                  />
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12 bg-white rounded-lg shadow-md">
            <div className="text-6xl mb-4">💔</div>
            <h3 className="text-xl font-semibold text-gray-700 mb-2">
              No Favorites Yet
            </h3>
            <p className="text-gray-500 mb-6">
              Start adding books to your favorites to see them here!
            </p>
            <Link
              to="/catalog"
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg inline-block transition-colors"
            >
              Browse Books
            </Link>
          </div>
        )}

        {favoritesList?.items && favoritesList.items.length > 0 && (
          <div className="mt-12 bg-gradient-to-r from-pink-500 to-red-600 rounded-lg p-8 text-white">
            <h3 className="text-2xl font-bold mb-4">❤️ Your Favorites Statistics</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-3xl font-bold">
                  {favoritesList.book_count}
                </div>
                <div className="text-pink-100">Total Favorites</div>
              </div>
              
              <div className="text-center">
                <div className="text-3xl font-bold">
                  {favoritesList.items.length > 0 
                    ? (favoritesList.items.reduce((sum, item) => sum + (item.book.average_rating || 0), 0) / favoritesList.items.length).toFixed(1)
                    : '0.0'
                  }⭐
                </div>
                <div className="text-pink-100">Average Rating</div>
              </div>
              
              <div className="text-center">
                <div className="text-3xl font-bold">
                  {new Set(favoritesList.items.flatMap(item => item.book.categories || [])).size}
                </div>
                <div className="text-pink-100">Different Categories</div>
              </div>
            </div>
          </div>
        )}

        <div className="mt-8 flex flex-wrap gap-4 justify-center">
          <Link
            to="/lists"
            className="bg-white hover:bg-gray-50 text-gray-800 px-6 py-3 rounded-lg shadow-md transition-colors border border-gray-200"
          >
            📚 View All Lists
          </Link>
          
          <Link
            to="/catalog"
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg shadow-md transition-colors"
          >
            🔍 Browse More Books
          </Link>
          
          <button
            onClick={fetchFavorites}
            className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg shadow-md transition-colors"
          >
            🔄 Refresh
          </button>
        </div>
      </div>
    </div>
  );
};

export default UserFavorites;