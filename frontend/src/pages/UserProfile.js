import React, { useState } from 'react';
import { Link } from 'react-router-dom';

const UserProfile = () => {
  // form for changing password
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmNewPassword, setConfirmNewPassword] = useState('');

  // state to show/hide password change form
  const [showPasswordForm, setShowPasswordForm] = useState(false);

  // password change logic
  const handlePasswordChange = (e) => {
    e.preventDefault();
    if (newPassword === confirmNewPassword) {
      // TODO: Add logic to change the password in the backend
      alert('Hasło zostało zmienione!');
      setShowPasswordForm(false);  // hide form after changing password
    } else {
      alert('Nowe hasło i potwierdzenie hasła muszą być takie same!');
    }
  };

  return (
    <div className="px-4 py-8 max-w-7xl mx-auto text-center">
      <h1 className="text-2xl font-bold mb-4">User Profile</h1>

      <div className="bg-white shadow rounded-lg p-6 mb-8">
        <div className="mb-4">
          <h2 className="text-xl font-semibold">User Name: John Doe</h2>
        </div>

        <div className="mb-4">
          <p className="text-lg text-gray-700">
            <strong>Last Liked Book:</strong> "The Great Gatsby" by F. Scott Fitzgerald
          </p>
        </div>

        <div className="mb-4">
          <p className="text-lg text-gray-700">
            <strong>Number of Reviews:</strong> 15
          </p>
        </div>
      </div>

      {/* buttons - user account */}
      <div className="space-x-4 mb-4">
        <button className="bg-red-600 text-white py-2 px-6 rounded hover:bg-red-700 transition">
          Delete Account
        </button>
        <Link to="/user-favorites">
          <button className="bg-blue-600 text-white py-2 px-6 rounded hover:bg-blue-700 transition">
            View Favourites
          </button>
        </Link>
        <Link to={"/reviews"}>
        <button className="bg-green-600 text-white py-2 px-6 rounded hover:bg-green-700 transition">
          View Reviews
        </button>
        </Link>
      </div>

      {/* button to show password change form */}
      <div className="mb-4">
        <button
          onClick={() => setShowPasswordForm(true)} 
          className="bg-indigo-600 text-white py-2 px-6 rounded hover:bg-indigo-700 transition"
        >
          Change Password
        </button>
      </div>

      {/* form for changing password */}
      {showPasswordForm && (
        <div className="bg-white shadow rounded-lg p-6 mt-8">
          <h2 className="text-xl font-semibold mb-4">Change Password</h2>
          <form onSubmit={handlePasswordChange}>
            <div className="mb-4">
              <label htmlFor="current-password" className="block text-lg font-medium text-gray-700">
                Current Password
              </label>
              <input
                id="current-password"
                type="password"
                className="w-full p-3 border border-gray-300 rounded-md"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                required
              />
            </div>

            <div className="mb-4">
              <label htmlFor="new-password" className="block text-lg font-medium text-gray-700">
                New Password
              </label>
              <input
                id="new-password"
                type="password"
                className="w-full p-3 border border-gray-300 rounded-md"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
              />
            </div>

            <div className="mb-4">
              <label htmlFor="confirm-new-password" className="block text-lg font-medium text-gray-700">
                Confirm New Password
              </label>
              <input
                id="confirm-new-password"
                type="password"
                className="w-full p-3 border border-gray-300 rounded-md"
                value={confirmNewPassword}
                onChange={(e) => setConfirmNewPassword(e.target.value)}
                required
              />
            </div>

            <button
              type="submit"
              className="bg-indigo-600 text-white py-2 px-6 rounded hover:bg-indigo-700 transition"
            >
              Change Password
            </button>
          </form>
        </div>
      )}
    </div>
  );
};

export default UserProfile;
