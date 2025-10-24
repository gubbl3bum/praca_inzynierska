import React, { useState, useEffect } from 'react';
import { useAuth } from '../services/AuthContext';
import api from '../services/api';

const AddToListButton = ({ book, compact = false, onFavoriteChange }) => {
  const { isAuthenticated, user } = useAuth();
  const [showMenu, setShowMenu] = useState(false);
  const [lists, setLists] = useState([]);
  const [bookLists, setBookLists] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [isFavorite, setIsFavorite] = useState(false);
  const [favoriteListId, setFavoriteListId] = useState(null);
  const [favoriteItemId, setFavoriteItemId] = useState(null);

  useEffect(() => {
    if (isAuthenticated && showMenu) {
      fetchLists();
      checkBookInLists();
    }
  }, [isAuthenticated, showMenu]);

  useEffect(() => {
    if (isAuthenticated && compact) {
      checkIfFavorite();
    }
  }, [isAuthenticated, compact]);

  const checkIfFavorite = async () => {
    try {
      const token = localStorage.getItem('wolfread_tokens');
      const tokens = token ? JSON.parse(token) : null;
      
      if (!tokens?.access) return;

      const response = await api.lists.checkBookInLists(book.id, tokens.access);
      
      if (response.status === 'success') {
        const favList = response.in_lists?.find(list => list.list_type === 'favorites');
        setIsFavorite(!!favList);
        if (favList) {
          setFavoriteListId(favList.id);
          // Znajdź item ID dla tej książki
          const listsResponse = await api.lists.getLists(tokens.access);
          if (listsResponse.status === 'success') {
            const fullFavList = listsResponse.lists?.find(l => l.id === favList.id);
            if (fullFavList) {
              const detailResponse = await api.lists.getListDetail(fullFavList.id, tokens.access);
              if (detailResponse.status === 'success') {
                const item = detailResponse.list.items?.find(i => i.book.id === book.id);
                if (item) {
                  setFavoriteItemId(item.id);
                }
              }
            }
          }
        }
      }
    } catch (error) {
      console.error('Error checking favorite status:', error);
    }
  };

  const fetchLists = async () => {
    try {
      const token = localStorage.getItem('wolfread_tokens');
      const tokens = token ? JSON.parse(token) : null;
      
      if (!tokens?.access) return;

      const response = await api.lists.getLists(tokens.access);
      
      if (response.status === 'success') {
        setLists(response.lists || []);
      }
    } catch (error) {
      console.error('Error fetching lists:', error);
    }
  };

  const checkBookInLists = async () => {
    try {
      const token = localStorage.getItem('wolfread_tokens');
      const tokens = token ? JSON.parse(token) : null;
      
      if (!tokens?.access) return;

      const response = await api.lists.checkBookInLists(book.id, tokens.access);
      
      if (response.status === 'success') {
        setBookLists(response.in_lists || []);
      }
    } catch (error) {
      console.error('Error checking book in lists:', error);
    }
  };

  const handleAddToList = async (listId) => {
    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      const token = localStorage.getItem('wolfread_tokens');
      const tokens = token ? JSON.parse(token) : null;
      
      if (!tokens?.access) {
        setMessage({ type: 'error', text: 'Please log in first' });
        return;
      }

      const response = await api.lists.addBookToList(listId, book.id, tokens.access);
      
      if (response.status === 'success') {
        setMessage({ type: 'success', text: 'Book added to list!' });
        await checkBookInLists();
        
        setTimeout(() => {
          setMessage({ type: '', text: '' });
          setShowMenu(false);
        }, 2000);
      }
    } catch (error) {
      const errorMessage = api.handleError(error, 'Failed to add book to list');
      setMessage({ type: 'error', text: errorMessage });
    } finally {
      setLoading(false);
    }
  };

  const handleToggleFavorite = async (e) => {
    e.stopPropagation();
    setLoading(true);

    try {
      const token = localStorage.getItem('wolfread_tokens');
      const tokens = token ? JSON.parse(token) : null;
      
      if (!tokens?.access) {
        setMessage({ type: 'error', text: 'Please log in first' });
        setTimeout(() => setMessage({ type: '', text: '' }), 2000);
        setLoading(false);
        return;
      }

      if (isFavorite) {
        // Usuń z ulubionych
        if (!favoriteListId || !favoriteItemId) {
          // Spróbuj ponownie pobrać info
          await checkIfFavorite();
          if (!favoriteListId || !favoriteItemId) {
            setMessage({ type: 'error', text: 'Cannot find favorite item' });
            setTimeout(() => setMessage({ type: '', text: '' }), 2000);
            setLoading(false);
            return;
          }
        }

        const response = await api.lists.removeBookFromList(
          favoriteListId,
          favoriteItemId,
          tokens.access
        );
        
        if (response.status === 'success') {
          setIsFavorite(false);
          setFavoriteListId(null);
          setFavoriteItemId(null);
          setMessage({ type: 'success', text: '💔 Removed from favorites' });
          
          if (onFavoriteChange) {
            onFavoriteChange(false);
          }
          
          setTimeout(() => {
            setMessage({ type: '', text: '' });
          }, 2000);
        }
      } else {
        // Dodaj do ulubionych
        const response = await api.lists.quickAddToFavorites(book.id, tokens.access);
        
        if (response.status === 'success') {
          setIsFavorite(true);
          setMessage({ type: 'success', text: '❤️ Added to favorites!' });
          
          // Pobierz ID listy i itemu
          await checkIfFavorite();
          
          if (onFavoriteChange) {
            onFavoriteChange(true);
          }
          
          setTimeout(() => {
            setMessage({ type: '', text: '' });
          }, 2000);
        }
      }
    } catch (error) {
      const errorMessage = api.handleError(error, 'Failed to update favorites');
      setMessage({ type: 'error', text: errorMessage });
      
      setTimeout(() => {
        setMessage({ type: '', text: '' });
      }, 3000);
    } finally {
      setLoading(false);
    }
  };

  const isBookInList = (listId) => {
    return bookLists.some(l => l.id === listId);
  };

  const getBookCount = (list) => {
    if (typeof list.book_count === 'number') {
      return list.book_count;
    }
    if (typeof list.book_count === 'object' && list.book_count !== null) {
      return 0;
    }
    return 0;
  };

  if (!isAuthenticated) {
    return null;
  }

  if (compact) {
    return (
      <div className="relative">
        <button
          onClick={handleToggleFavorite}
          disabled={loading}
          className={`p-2 bg-white bg-opacity-90 hover:bg-opacity-100 rounded-full shadow-md transition-all disabled:opacity-50 ${
            isFavorite 
              ? 'text-red-500 hover:text-red-600' 
              : 'text-gray-400 hover:text-red-500'
          }`}
          title={isFavorite ? "Remove from favorites" : "Add to favorites"}
        >
          {loading ? (
            <span className="animate-spin">⏳</span>
          ) : (
            <span className={`text-xl ${isFavorite ? 'animate-pulse' : ''}`}>
              {isFavorite ? '❤️' : '🤍'}
            </span>
          )}
        </button>
        
        {message.text && (
          <div className={`absolute top-full left-0 mt-1 px-2 py-1 rounded text-xs whitespace-nowrap z-20 shadow-lg ${
            message.type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}>
            {message.text}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="relative">
      <button
        onClick={(e) => {
          e.stopPropagation();
          setShowMenu(!showMenu);
        }}
        className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors flex items-center gap-2"
      >
        <span>📚</span>
        <span>Add to List</span>
      </button>

      {showMenu && (
        <>
          <div
            className="fixed inset-0 z-40"
            onClick={() => setShowMenu(false)}
          ></div>

          <div className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-xl border border-gray-200 z-50 max-h-96 overflow-y-auto">
            
            <div className="px-4 py-3 border-b border-gray-200">
              <h3 className="font-semibold text-gray-800">Add to list</h3>
            </div>

            {message.text && (
              <div className={`mx-4 my-2 px-3 py-2 rounded text-sm ${
                message.type === 'success' 
                  ? 'bg-green-50 text-green-800 border border-green-200' 
                  : 'bg-red-50 text-red-800 border border-red-200'
              }`}>
                {message.text}
              </div>
            )}

            {loading ? (
              <div className="px-4 py-8 text-center text-gray-500">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500 mx-auto mb-2"></div>
                Loading...
              </div>
            ) : lists.length === 0 ? (
              <div className="px-4 py-8 text-center text-gray-500">
                <p className="mb-4">No lists yet</p>
                <button
                  onClick={async () => {
                    const token = localStorage.getItem('wolfread_tokens');
                    const tokens = token ? JSON.parse(token) : null;
                    if (tokens?.access) {
                      await api.lists.initializeDefaultLists(tokens.access);
                      fetchLists();
                    }
                  }}
                  className="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700"
                >
                  Create default lists
                </button>
              </div>
            ) : (
              <div className="py-2">
                {lists.map((list) => {
                  const bookCount = getBookCount(list);
                  
                  return (
                    <button
                      key={list.id}
                      onClick={() => handleAddToList(list.id)}
                      disabled={isBookInList(list.id)}
                      className={`w-full px-4 py-3 text-left hover:bg-gray-50 flex items-center justify-between transition-colors ${
                        isBookInList(list.id) ? 'opacity-50 cursor-not-allowed' : ''
                      }`}
                    >
                      <div>
                        <div className="font-medium text-gray-800">
                          {list.name}
                          {list.is_default && (
                            <span className="ml-2 text-xs text-blue-600">Default</span>
                          )}
                        </div>
                        <div className="text-xs text-gray-500">
                          {bookCount} book{bookCount !== 1 ? 's' : ''}
                        </div>
                      </div>
                      
                      {isBookInList(list.id) && (
                        <span className="text-green-600 text-sm">✓ Added</span>
                      )}
                    </button>
                  );
                })}
              </div>
            )}

            <div className="px-4 py-3 border-t border-gray-200">
              <button
                onClick={() => {
                  alert('Create list feature coming soon!');
                }}
                className="w-full text-blue-600 hover:text-blue-700 text-sm font-medium"
              >
                + Create new list
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default AddToListButton;