import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../services/AuthContext';

const UserProfile = () => {
  const navigate = useNavigate();
  const { user, logout, updateProfile, changePassword, isLoading } = useAuth();
  
  // Form states
  const [profileData, setProfileData] = useState({
    first_name: '',
    last_name: '',
    email: ''
  });
  
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_new_password: ''
  });
  
  const [showPasswordForm, setShowPasswordForm] = useState(false);
  const [showProfileEdit, setShowProfileEdit] = useState(false);
  const [updateLoading, setUpdateLoading] = useState(false);
  const [updateError, setUpdateError] = useState(null);
  const [updateSuccess, setUpdateSuccess] = useState(null);

  // Załaduj dane użytkownika po zamontowaniu komponentu
  useEffect(() => {
    if (user) {
      setProfileData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        email: user.email || ''
      });
    }
  }, [user]);

  // Handle profile update
  const handleProfileUpdate = async (e) => {
    e.preventDefault();
    setUpdateLoading(true);
    setUpdateError(null);
    setUpdateSuccess(null);

    try {
      const result = await updateProfile(profileData);
      
      if (result.success) {
        setUpdateSuccess('Profile updated successfully! ✅');
        setShowProfileEdit(false);
        
        // Clear success message after 3 seconds
        setTimeout(() => setUpdateSuccess(null), 3000);
      } else {
        setUpdateError(result.error || 'Failed to update profile');
      }
    } catch (error) {
      setUpdateError('An error occurred while updating profile');
    } finally {
      setUpdateLoading(false);
    }
  };

  // Handle password change
  const handlePasswordChange = async (e) => {
    e.preventDefault();
    setUpdateError(null);
    setUpdateSuccess(null);

    // Validate password confirmation
    if (passwordData.new_password !== passwordData.confirm_new_password) {
      setUpdateError('New passwords do not match!');
      return;
    }

    // Validate password strength (minimum 8 characters)
    if (passwordData.new_password.length < 8) {
      setUpdateError('New password must be at least 8 characters long');
      return;
    }

    setUpdateLoading(true);

    try {
      const result = await changePassword(
        passwordData.current_password,
        passwordData.new_password
      );

      if (result.success) {
        setUpdateSuccess('Password changed successfully! You will be logged out...');
        
        // Clear form
        setPasswordData({
          current_password: '',
          new_password: '',
          confirm_new_password: ''
        });
        
        // User will be automatically logged out by changePassword function
        setTimeout(() => {
          navigate('/login');
        }, 2000);
      } else {
        setUpdateError(result.error || 'Failed to change password');
      }
    } catch (error) {
      setUpdateError('An error occurred while changing password');
    } finally {
      setUpdateLoading(false);
    }
  };

  // Handle account deletion (placeholder)
  const handleDeleteAccount = () => {
    const confirmed = window.confirm(
      '⚠️ Are you sure you want to delete your account? This action cannot be undone!'
    );
    
    if (confirmed) {
      // TODO: Implement account deletion API call
      alert('Account deletion not implemented yet. This would permanently delete your account.');
    }
  };

  // Handle logout
  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading profile...</p>
        </div>
      </div>
    );
  }

  // No user state (should not happen due to ProtectedRoute)
  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Not logged in</h2>
          <Link
            to="/login"
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg"
          >
            Go to Login
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 px-4 py-8">
      <div className="max-w-4xl mx-auto">
        
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-24 h-24 bg-blue-600 rounded-full flex items-center justify-center text-white text-4xl font-bold mx-auto mb-4">
            {user.first_name?.charAt(0) || user.username?.charAt(0) || 'U'}
          </div>
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            {user.full_name || user.username}
          </h1>
          <p className="text-gray-600">{user.email}</p>
          <p className="text-sm text-gray-500 mt-1">
            Member since {new Date(user.date_joined).toLocaleDateString()}
          </p>
        </div>

        {/* Success/Error Messages */}
        {updateSuccess && (
          <div className="mb-6 bg-green-50 border border-green-200 rounded-lg p-4 text-green-800 text-center">
            {updateSuccess}
          </div>
        )}

        {updateError && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 text-red-800 text-center">
            {updateError}
          </div>
        )}

        {/* Profile Information Card */}
        <div className="bg-white shadow-lg rounded-lg p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-gray-800">Profile Information</h2>
            {!showProfileEdit && (
              <button
                onClick={() => setShowProfileEdit(true)}
                className="text-blue-600 hover:text-blue-800 text-sm font-medium"
              >
                ✏️ Edit Profile
              </button>
            )}
          </div>

          {!showProfileEdit ? (
            // Display mode
            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-medium text-gray-600">Username</h3>
                <p className="text-gray-800">{user.username}</p>
              </div>
              
              <div>
                <h3 className="text-sm font-medium text-gray-600">Email</h3>
                <p className="text-gray-800">{user.email}</p>
              </div>
              
              <div>
                <h3 className="text-sm font-medium text-gray-600">First Name</h3>
                <p className="text-gray-800">{user.first_name || 'Not set'}</p>
              </div>
              
              <div>
                <h3 className="text-sm font-medium text-gray-600">Last Name</h3>
                <p className="text-gray-800">{user.last_name || 'Not set'}</p>
              </div>

              <div>
                <h3 className="text-sm font-medium text-gray-600">Last Login</h3>
                <p className="text-gray-800">
                  {user.last_login ? new Date(user.last_login).toLocaleString() : 'Never'}
                </p>
              </div>
            </div>
          ) : (
            // Edit mode
            <form onSubmit={handleProfileUpdate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  value={profileData.email}
                  onChange={(e) => setProfileData({...profileData, email: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  First Name
                </label>
                <input
                  type="text"
                  value={profileData.first_name}
                  onChange={(e) => setProfileData({...profileData, first_name: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Last Name
                </label>
                <input
                  type="text"
                  value={profileData.last_name}
                  onChange={(e) => setProfileData({...profileData, last_name: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="flex justify-end gap-4 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowProfileEdit(false);
                    // Reset to original values
                    setProfileData({
                      first_name: user.first_name || '',
                      last_name: user.last_name || '',
                      email: user.email || ''
                    });
                  }}
                  className="px-4 py-2 bg-gray-300 text-gray-800 rounded-lg hover:bg-gray-400 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={updateLoading}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
                >
                  {updateLoading ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          )}
        </div>

        {/* Action Buttons */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <Link to="/user-favorites">
            <button className="w-full bg-purple-600 text-white py-3 px-6 rounded-lg hover:bg-purple-700 transition font-medium">
              ❤️ View Favourites
            </button>
          </Link>

          <Link to="/reviews">
            <button className="w-full bg-green-600 text-white py-3 px-6 rounded-lg hover:bg-green-700 transition font-medium">
              ⭐ View Reviews
            </button>
          </Link>

          <button
            onClick={() => setShowPasswordForm(!showPasswordForm)}
            className="w-full bg-indigo-600 text-white py-3 px-6 rounded-lg hover:bg-indigo-700 transition font-medium"
          >
            🔒 Change Password
          </button>

          <button
            onClick={handleLogout}
            className="w-full bg-gray-600 text-white py-3 px-6 rounded-lg hover:bg-gray-700 transition font-medium"
          >
            🚪 Log Out
          </button>
        </div>

        {/* Change Password Form */}
        {showPasswordForm && (
          <div className="bg-white shadow-lg rounded-lg p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4 text-center">Change Password</h2>
            <form onSubmit={handlePasswordChange} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Current Password
                </label>
                <input
                  type="password"
                  value={passwordData.current_password}
                  onChange={(e) => setPasswordData({...passwordData, current_password: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  New Password
                </label>
                <input
                  type="password"
                  value={passwordData.new_password}
                  onChange={(e) => setPasswordData({...passwordData, new_password: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                  minLength={8}
                />
                <p className="text-xs text-gray-500 mt-1">Minimum 8 characters</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Confirm New Password
                </label>
                <input
                  type="password"
                  value={passwordData.confirm_new_password}
                  onChange={(e) => setPasswordData({...passwordData, confirm_new_password: e.target.value})}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div className="flex justify-end gap-4 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowPasswordForm(false);
                    setPasswordData({
                      current_password: '',
                      new_password: '',
                      confirm_new_password: ''
                    });
                  }}
                  className="px-4 py-2 bg-gray-300 text-gray-800 rounded-lg hover:bg-gray-400 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={updateLoading}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition disabled:opacity-50"
                >
                  {updateLoading ? 'Changing...' : 'Change Password'}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Danger Zone */}
        {/* <div className="bg-white shadow-lg rounded-lg p-6 border-2 border-red-200">
          <h2 className="text-xl font-semibold mb-4 text-red-600">⚠️ Danger Zone</h2>
          <p className="text-gray-600 mb-4">
            Once you delete your account, there is no going back. Please be certain.
          </p>
          <button
            onClick={handleDeleteAccount}
            className="w-full bg-red-600 text-white py-3 px-6 rounded-lg hover:bg-red-700 transition font-medium"
          >
            🗑️ Delete Account
          </button>
        </div> */}

      </div>
    </div>
  );
};

export default UserProfile;