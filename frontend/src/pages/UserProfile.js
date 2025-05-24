import React, { useState } from 'react';
import { Link } from 'react-router-dom';

const UserProfile = () => {
  // Placeholdery danych użytkownika (do zamiany na dane z backendu)
  const userData = {
    name: 'John Doe',
    lastLikedBook: {
      title: 'The Great Gatsby',
      author: 'F. Scott Fitzgerald',
    },
    reviewCount: 15,
  };

  // Form state
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmNewPassword, setConfirmNewPassword] = useState('');
  const [showPasswordForm, setShowPasswordForm] = useState(false);

  const handlePasswordChange = (e) => {
    e.preventDefault();
    if (newPassword === confirmNewPassword) {
      // TODO: Send password update to backend
      alert('Hasło zostało zmienione!');
      setShowPasswordForm(false);
      setCurrentPassword('');
      setNewPassword('');
      setConfirmNewPassword('');
    } else {
      alert('Nowe hasło i potwierdzenie hasła muszą być takie same!');
    }
  };

  return (
    <div className="px-4 py-8 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-center">User Profile</h1>

      <div className="bg-white shadow rounded-lg p-6 space-y-4">
        <div>
          <h2 className="text-lg font-semibold text-gray-800">User Name:</h2>
          <p className="text-gray-700">{userData.name}</p>
        </div>

        <div>
          <h2 className="text-lg font-semibold text-gray-800">Last Liked Book:</h2>
          <p className="text-gray-700">
            <em>"{userData.lastLikedBook.title}"</em> by {userData.lastLikedBook.author}
          </p>
        </div>

        <div>
          <h2 className="text-lg font-semibold text-gray-800">Number of Reviews:</h2>
          <p className="text-gray-700">{userData.reviewCount}</p>
        </div>
      </div>

      <div className="flex flex-wrap justify-center gap-4 mt-6">
        <button className="bg-red-600 text-white py-2 px-6 rounded hover:bg-red-700 transition">
          Delete Account
        </button>

        <Link to="/user-favorites">
          <button className="bg-blue-600 text-white py-2 px-6 rounded hover:bg-blue-700 transition">
            View Favourites
          </button>
        </Link>

        <Link to="/reviews">
          <button className="bg-green-600 text-white py-2 px-6 rounded hover:bg-green-700 transition">
            View Reviews
          </button>
        </Link>

        <button
          onClick={() => setShowPasswordForm(true)}
          className="bg-indigo-600 text-white py-2 px-6 rounded hover:bg-indigo-700 transition"
        >
          Change Password
        </button>
      </div>

      {showPasswordForm && (
        <div className="bg-white shadow rounded-lg p-6 mt-8 max-w-xl mx-auto">
          <h2 className="text-xl font-semibold mb-4 text-center">Change Password</h2>
          <form onSubmit={handlePasswordChange} className="space-y-4">
            <div>
              <label htmlFor="current-password" className="block text-sm font-medium text-gray-700 mb-1">
                Current Password
              </label>
              <input
                id="current-password"
                type="password"
                className="w-full px-4 py-2 border border-gray-300 rounded"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                required
              />
            </div>

            <div>
              <label htmlFor="new-password" className="block text-sm font-medium text-gray-700 mb-1">
                New Password
              </label>
              <input
                id="new-password"
                type="password"
                className="w-full px-4 py-2 border border-gray-300 rounded"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
              />
            </div>

            <div>
              <label htmlFor="confirm-new-password" className="block text-sm font-medium text-gray-700 mb-1">
                Confirm New Password
              </label>
              <input
                id="confirm-new-password"
                type="password"
                className="w-full px-4 py-2 border border-gray-300 rounded"
                value={confirmNewPassword}
                onChange={(e) => setConfirmNewPassword(e.target.value)}
                required
              />
            </div>

            <div className="flex justify-end gap-4">
              <button
                type="button"
                onClick={() => setShowPasswordForm(false)}
                className="bg-gray-300 text-gray-800 py-2 px-4 rounded hover:bg-gray-400 transition"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="bg-indigo-600 text-white py-2 px-4 rounded hover:bg-indigo-700 transition"
              >
                Change Password
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

export default UserProfile;
