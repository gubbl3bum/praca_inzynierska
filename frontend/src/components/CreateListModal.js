// frontend/src/components/CreateListModal.js
import React, { useState } from 'react';
import api from '../services/api';

const CreateListModal = ({ isOpen, onClose, onSuccess }) => {
  const [newListData, setNewListData] = useState({
    name: '',
    description: '',
    is_public: false
  });
  const [createError, setCreateError] = useState(null);
  const [createLoading, setCreateLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setCreateError(null);
    setCreateLoading(true);

    try {
      if (!newListData.name.trim()) {
        setCreateError('List name is required');
        setCreateLoading(false);
        return;
      }

      const token = localStorage.getItem('wolfread_tokens');
      const tokens = token ? JSON.parse(token) : null;
      
      if (!tokens?.access) {
        setCreateError('Please log in first');
        setCreateLoading(false);
        return;
      }

      const listDataToSend = {
        name: newListData.name.trim(),
        description: newListData.description.trim(),
        is_public: newListData.is_public,
        list_type: 'custom'
      };

      console.log('Creating list with data:', listDataToSend);

      const response = await api.lists.createList(listDataToSend, tokens.access);
      
      if (response.status === 'success') {
        // Reset form
        setNewListData({ name: '', description: '', is_public: false });
        setCreateError(null);
        
        // Call success callback with the new list
        if (onSuccess) {
          onSuccess(response.list);
        }
        
        // Close modal
        onClose();
      } else {
        throw new Error(response.message || 'Failed to create list');
      }
    } catch (err) {
      console.error('Error creating list:', err);
      const errorMsg = api.handleError(err, 'Failed to create list');
      setCreateError(errorMsg);
    } finally {
      setCreateLoading(false);
    }
  };

  const handleClose = () => {
    setNewListData({ name: '', description: '', is_public: false });
    setCreateError(null);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <>
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 z-40"
        onClick={handleClose}
      ></div>
      
      <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-lg p-6 max-w-md w-full shadow-2xl">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold">Create New List</h2>
            <button
              onClick={handleClose}
              className="text-gray-400 hover:text-gray-600 text-2xl leading-none"
            >
              ×
            </button>
          </div>
          
          {createError && (
            <div className="mb-4 bg-red-50 border border-red-200 rounded p-3 text-red-800 text-sm">
              {createError}
            </div>
          )}
          
          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                List Name *
              </label>
              <input
                type="text"
                required
                value={newListData.name}
                onChange={(e) => setNewListData({...newListData, name: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="My Awesome List"
                disabled={createLoading}
              />
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                value={newListData.description}
                onChange={(e) => setNewListData({...newListData, description: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                rows="3"
                placeholder="What's this list about?"
                disabled={createLoading}
              />
            </div>

            <div className="mb-6">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={newListData.is_public}
                  onChange={(e) => setNewListData({...newListData, is_public: e.target.checked})}
                  className="rounded text-blue-600 focus:ring-2 focus:ring-blue-500"
                  disabled={createLoading}
                />
                <span className="text-sm text-gray-700">
                  🌍 Make this list public (others can see it)
                </span>
              </label>
            </div>

            <div className="flex justify-end gap-3">
              <button
                type="button"
                onClick={handleClose}
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded transition-colors"
                disabled={createLoading}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                disabled={createLoading}
              >
                {createLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    Creating...
                  </>
                ) : (
                  '✨ Create List'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </>
  );
};

export default CreateListModal;