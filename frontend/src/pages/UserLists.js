// frontend/src/pages/UserLists.js
import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../services/AuthContext';
import { useBadgeCheck } from '../hooks/useBadgeCheck';
import BookCard from '../components/BookCard';
import CreateListModal from '../components/CreateListModal';
import api from '../services/api';

const UserLists = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { checkBadges } = useBadgeCheck();
  const [lists, setLists] = useState([]);
  const [selectedList, setSelectedList] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Create modal states
  const [showCreateModal, setShowCreateModal] = useState(false);

  // Edit modal states
  const [showEditModal, setShowEditModal] = useState(false);
  const [editListData, setEditListData] = useState({
    id: null,
    name: '',
    description: '',
    is_public: false
  });
  const [editError, setEditError] = useState(null);
  const [editLoading, setEditLoading] = useState(false);

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

  const handleCreateListSuccess = async (newList) => {
    await fetchLists();
    
    if (newList?.id) {
      await fetchListDetails(newList.id);
    }
  };

  const handleOpenEditModal = (list) => {
    setEditListData({
      id: list.id,
      name: list.name,
      description: list.description || '',
      is_public: list.is_public || false
    });
    setEditError(null);
    setShowEditModal(true);
  };

  const handleEditList = async (e) => {
    e.preventDefault();
    setEditError(null);
    setEditLoading(true);

    try {
      if (!editListData.name.trim()) {
        setEditError('List name is required');
        setEditLoading(false);
        return;
      }

      const token = localStorage.getItem('wolfread_tokens');
      const tokens = token ? JSON.parse(token) : null;
      
      if (!tokens?.access) {
        navigate('/login');
        return;
      }

      const listDataToSend = {
        name: editListData.name.trim(),
        description: editListData.description.trim(),
        is_public: editListData.is_public
      };

      console.log('Updating list with data:', listDataToSend);

      const response = await api.lists.updateList(
        editListData.id, 
        listDataToSend, 
        tokens.access
      );
      
      if (response.status === 'success') {
        setShowEditModal(false);
        setEditListData({ id: null, name: '', description: '', is_public: false });
        
        await fetchLists();
        
        if (selectedList && selectedList.id === editListData.id) {
          await fetchListDetails(editListData.id);
        }
      } else {
        throw new Error(response.message || 'Failed to update list');
      }
    } catch (err) {
      console.error('Error updating list:', err);
      const errorMsg = api.handleError(err, 'Failed to update list');
      setEditError(errorMsg);
    } finally {
      setEditLoading(false);
    }
  };

  const handleCloseEditModal = () => {
    setShowEditModal(false);
    setEditListData({ id: null, name: '', description: '', is_public: false });
    setEditError(null);
  };

  const handleDeleteList = async (listId) => {
    if (!window.confirm('Are you sure you want to delete this list? This action cannot be undone.')) {
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

        await checkBadges();
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
                  className="text-blue-600 hover:text-blue-700 text-sm font-medium flex items-center gap-1"
                >
                  <span className="text-lg">+</span> New
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

                  {/* Action buttons */}
                  <div className="flex gap-2">
                    {!selectedList.is_default && (
                      <>
                        <button
                          onClick={() => handleOpenEditModal(selectedList)}
                          className="text-blue-600 hover:text-blue-700 text-sm flex items-center gap-1"
                        >
                          ✏️ Edit
                        </button>
                        <button
                          onClick={() => handleDeleteList(selectedList.id)}
                          className="text-red-600 hover:text-red-700 text-sm flex items-center gap-1"
                        >
                          🗑️ Delete
                        </button>
                      </>
                    )}
                    {selectedList.is_default && (
                      <button
                        onClick={() => handleOpenEditModal(selectedList)}
                        className="text-blue-600 hover:text-blue-700 text-sm flex items-center gap-1"
                        title="You can only edit description and privacy for default lists"
                      >
                        ✏️ Edit
                      </button>
                    )}
                  </div>
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

        {/* CREATE LIST MODAL */}
        <CreateListModal
          isOpen={showCreateModal}
          onClose={() => setShowCreateModal(false)}
          onSuccess={handleCreateListSuccess}
        />

        {/* EDIT LIST MODAL */}
        {showEditModal && (
          <>
            <div 
              className="fixed inset-0 bg-black bg-opacity-50 z-40"
              onClick={handleCloseEditModal}
            ></div>
            
            <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
              <div className="bg-white rounded-lg p-6 max-w-md w-full shadow-2xl">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-bold">Edit List</h2>
                  <button
                    onClick={handleCloseEditModal}
                    className="text-gray-400 hover:text-gray-600 text-2xl leading-none"
                  >
                    ×
                  </button>
                </div>
                
                {editError && (
                  <div className="mb-4 bg-red-50 border border-red-200 rounded p-3 text-red-800 text-sm">
                    {editError}
                  </div>
                )}

                {selectedList?.is_default && (
                  <div className="mb-4 bg-blue-50 border border-blue-200 rounded p-3 text-blue-800 text-sm">
                    ℹ️ Default lists can only have their description and privacy settings edited.
                  </div>
                )}
                
                <form onSubmit={handleEditList}>
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      List Name *
                    </label>
                    <input
                      type="text"
                      required
                      value={editListData.name}
                      onChange={(e) => setEditListData({...editListData, name: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
                      placeholder="My Awesome List"
                      disabled={editLoading || selectedList?.is_default}
                    />
                    {selectedList?.is_default && (
                      <p className="mt-1 text-xs text-gray-500">
                        Cannot change name of default lists
                      </p>
                    )}
                  </div>

                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Description
                    </label>
                    <textarea
                      value={editListData.description}
                      onChange={(e) => setEditListData({...editListData, description: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      rows="3"
                      placeholder="What's this list about?"
                      disabled={editLoading}
                    />
                  </div>

                  <div className="mb-6">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={editListData.is_public}
                        onChange={(e) => setEditListData({...editListData, is_public: e.target.checked})}
                        className="rounded text-blue-600 focus:ring-2 focus:ring-blue-500"
                        disabled={editLoading}
                      />
                      <span className="text-sm text-gray-700">
                        🌍 Make this list public (others can see it)
                      </span>
                    </label>
                  </div>

                  <div className="flex justify-end gap-3">
                    <button
                      type="button"
                      onClick={handleCloseEditModal}
                      className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded transition-colors"
                      disabled={editLoading}
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                      disabled={editLoading}
                    >
                      {editLoading ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                          Saving...
                        </>
                      ) : (
                        '💾 Save Changes'
                      )}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </>
        )}

      </div>
    </div>
  );
};

export default UserLists;