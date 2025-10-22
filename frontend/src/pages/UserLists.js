import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../services/AuthContext';
import BookCard from '../components/BookCard';
import api from '../services/api';

const UserLists = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [lists, setLists] = useState([]);
  const [selectedList, setSelectedList] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newListData, setNewListData] = useState({
    name: '',
    description: '',
    is_public: false
  });

  useEffect(() => {
    fetchLists();
  }, []);

  const fetchLists = async () => {
    try {
      setLoading(true);
      setError(null);

      const token = localStorage.getItem('wolfread_tokens');
      const tokens = token ? JSON.parse(token) : null;
      
      if (!tokens?.access) {
        navigate('/login');
        return;
      }

      const response = await api.lists.getLists(tokens.access);
      
      if (response.status === 'success') {
        setLists(response.lists || []);
        
        // Auto-select first list
        if (response.lists && response.lists.length > 0 && !selectedList) {
          fetchListDetails(response.lists[0].id);
        }
      }
    } catch (err) {
      console.error('Error fetching lists:', err);
      setError(api.handleError(err, 'Failed to load lists'));
    } finally {
      setLoading(false);
    }
  };

  const fetchListDetails = async (listId) => {
    try {
      const token = localStorage.getItem('wolfread_tokens');
      const tokens = token ? JSON.parse(token) : null;
      
      if (!tokens?.access) return;

      const response = await api.lists.getListDetail(listId, tokens.access);
      
      if (response.status === 'success') {
        setSelectedList(response.list);
      }
    } catch (err) {
      console.error('Error fetching list details:', err);
    }
  };

  const handleCreateList = async (e) => {
    e.preventDefault();

    try {
      const token = localStorage.getItem('wolfread_tokens');
      const tokens = token ? JSON.parse(token) : null;
      
      if (!tokens?.access) return;

      const response = await api.lists.createList(newListData, tokens.access);
      
      if (response.status === 'success') {
        setShowCreateModal(false);
        setNewListData({ name: '', description: '', is_public: false });
        await fetchLists();
      }
    } catch (err) {
      console.error('Error creating list:', err);
      alert(api.handleError(err, 'Failed to create list'));
    }
  };

  const handleDeleteList = async (listId) => {
    if (!window.confirm('Are you sure you want to delete this list?')) {
      return;
    }

    try {
      const token = localStorage.getItem('wolfread_tokens');
      const tokens = token ? JSON.parse(token) : null;
      
      if (!tokens?.access) return;

      const response = await api.lists.deleteList(listId, tokens.access);
      
      if (response.status === 'success') {
        if (selectedList && selectedList.id === listId) {
          setSelectedList(null);
        }
        await fetchLists();
      }
    } catch (err) {
      console.error('Error deleting list:', err);
      alert(api.handleError(err, 'Failed to delete list'));
    }
  };

  const handleRemoveFromList = async (itemId) => {
    if (!selectedList) return;

    try {
      const token = localStorage.getItem('wolfread_tokens');
      const tokens = token ? JSON.parse(token) : null;
      
      if (!tokens?.access) return;

      const response = await api.lists.removeBookFromList(
        selectedList.id,
        itemId,
        tokens.access
      );
      
      if (response.status === 'success') {
        await fetchListDetails(selectedList.id);
      }
    } catch (err) {
      console.error('Error removing book:', err);
      alert(api.handleError(err, 'Failed to remove book'));
    }
  };

  const initializeDefaultLists = async () => {
    try {
      const token = localStorage.getItem('wolfread_tokens');
      const tokens = token ? JSON.parse(token) : null;
      
      if (!tokens?.access) return;

      await api.lists.initializeDefaultLists(tokens.access);
      await fetchLists();
    } catch (err) {
      console.error('Error initializing lists:', err);
    }
  };

  const getListIcon = (listType) => {
    switch (listType) {
      case 'favorites': return '❤️';
      case 'to_read': return '📖';
      case 'reading': return '📚';
      case 'read': return '✅';
      default: return '📋';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your lists...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            📚 My Book Lists
          </h1>
          <p className="text-gray-600">
            Organize your books into custom lists
          </p>
        </div>

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
            {error}
          </div>
        )}

        <div className="flex flex-col lg:flex-row gap-6">
          
          {/* Sidebar - Lists */}
          <div className="lg:w-1/4">
            <div className="bg-white rounded-lg shadow-md p-4">
              
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-semibold text-gray-800">Your Lists</h2>
                <button
                  onClick={() => setShowCreateModal(true)}
                  className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                >
                  + New
                </button>
              </div>

              {lists.length === 0 ? (
                <div className="text-center py-8">
                  <p className="text-gray-500 mb-4">No lists yet</p>
                  <button
                    onClick={initializeDefaultLists}
                    className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 text-sm"
                  >
                    Create Default Lists
                  </button>
                </div>
              ) : (
                <div className="space-y-2">
                  {lists.map((list) => (
                    <button
                      key={list.id}
                      onClick={() => fetchListDetails(list.id)}
                      className={`w-full text-left px-3 py-2 rounded transition-colors ${
                        selectedList && selectedList.id === list.id
                          ? 'bg-blue-50 text-blue-700'
                          : 'hover:bg-gray-50'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span>{getListIcon(list.list_type)}</span>
                          <span className="font-medium">{list.name}</span>
                        </div>
                        <span className="text-sm text-gray-500">
                          {list.book_count}
                        </span>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Main content - Selected list */}
          <div className="lg:w-3/4">
            {selectedList ? (
              <div className="bg-white rounded-lg shadow-md p-6">
                
                {/* List header */}
                <div className="flex items-start justify-between mb-6">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-800 mb-2">
                      {getListIcon(selectedList.list_type)} {selectedList.name}
                    </h2>
                    {selectedList.description && (
                      <p className="text-gray-600">{selectedList.description}</p>
                    )}
                    <div className="mt-2 flex items-center gap-4 text-sm text-gray-500">
                      <span>{selectedList.book_count} books</span>
                      {selectedList.is_public && (
                        <span className="flex items-center gap-1">
                          🌍 Public
                        </span>
                      )}
                      {selectedList.is_default && (
                        <span className="text-blue-600">Default list</span>
                      )}
                    </div>
                  </div>

                  {!selectedList.is_default && (
                    <button
                      onClick={() => handleDeleteList(selectedList.id)}
                      className="text-red-600 hover:text-red-700 text-sm"
                    >
                      🗑️ Delete
                    </button>
                  )}
                </div>

                {/* Books grid */}
                {selectedList.items && selectedList.items.length > 0 ? (
                  <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                    {selectedList.items.map((item) => (
                      <div key={item.id} className="relative">
                        <BookCard book={item.book} />
                        
                        {/* Remove button */}
                        <button
                          onClick={() => handleRemoveFromList(item.id)}
                          className="absolute top-2 right-2 bg-red-500 hover:bg-red-600 text-white w-8 h-8 rounded-full flex items-center justify-center shadow-lg z-10"
                          title="Remove from list"
                        >
                          ×
                        </button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <div className="text-6xl mb-4">📚</div>
                    <p className="text-gray-500 mb-4">
                      This list is empty
                    </p>
                    <Link
                      to="/catalog"
                      className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg inline-block"
                    >
                      Browse Books
                    </Link>
                  </div>
                )}
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-md p-12 text-center">
                <div className="text-6xl mb-4">📋</div>
                <h3 className="text-xl font-semibold text-gray-700 mb-2">
                  Select a list
                </h3>
                <p className="text-gray-500">
                  Choose a list from the sidebar to view its contents
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Create list modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg p-6 max-w-md w-full">
              <h2 className="text-xl font-bold mb-4">Create New List</h2>
              
              <form onSubmit={handleCreateList}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    List Name *
                  </label>
                  <input
                    type="text"
                    required
                    value={newListData.name}
                    onChange={(e) => setNewListData({...newListData, name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                    placeholder="My Awesome List"
                  />
                </div>

                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Description
                  </label>
                  <textarea
                    value={newListData.description}
                    onChange={(e) => setNewListData({...newListData, description: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
                    rows="3"
                    placeholder="What's this list about?"
                  />
                </div>

                <div className="mb-6">
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={newListData.is_public}
                      onChange={(e) => setNewListData({...newListData, is_public: e.target.checked})}
                      className="rounded"
                    />
                    <span className="text-sm text-gray-700">
                      Make this list public (others can see it)
                    </span>
                  </label>
                </div>

                <div className="flex justify-end gap-3">
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded"
                  >
                    Create List
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};

export default UserLists;