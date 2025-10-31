import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../services/AuthContext';
import api from '../services/api';

const UserProfile = () => {
  const navigate = useNavigate();
  const { user, logout, updateProfile, changePassword, isLoading } = useAuth();
  
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
  
  // Statistics
  const [statistics, setStatistics] = useState(null);
  const [statsLoading, setStatsLoading] = useState(true);

  useEffect(() => {
    if (user) {
      setProfileData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        email: user.email || ''
      });
      fetchUserStatistics();
    }
  }, [user]);

  const fetchUserStatistics = async () => {
    try {
      setStatsLoading(true);
      const token = localStorage.getItem('wolfread_tokens');
      const tokens = token ? JSON.parse(token) : null;
      
      if (!tokens?.access) return;

      // Fetch from gamification API
      const gamificationStats = await api.gamification.getStatistics(tokens.access);
      
      // Fetch review stats
      const reviewStats = await api.reviews.getUserReviews(tokens.access, { page_size: 1 });
      
      // Fetch lists
      const listsResponse = await api.lists.getLists(tokens.access);
      
      setStatistics({
        totalPoints: gamificationStats.statistics?.total_points || 0,
        badgesEarned: gamificationStats.statistics?.badges_earned || 0,
        booksRead: gamificationStats.statistics?.books_read || 0,
        totalReviews: reviewStats.user_statistics?.total_reviews || 0,
        averageRating: reviewStats.user_statistics?.average_rating || 0,
        totalLists: listsResponse.lists?.length || 0,
      });
    } catch (error) {
      console.error('Error fetching statistics:', error);
    } finally {
      setStatsLoading(false);
    }
  };

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

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    setUpdateError(null);
    setUpdateSuccess(null);

    if (passwordData.new_password !== passwordData.confirm_new_password) {
      setUpdateError('New passwords do not match!');
      return;
    }

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
        setPasswordData({
          current_password: '',
          new_password: '',
          confirm_new_password: ''
        });
        setTimeout(() => navigate('/login'), 2000);
      } else {
        setUpdateError(result.error || 'Failed to change password');
      }
    } catch (error) {
      setUpdateError('An error occurred while changing password');
    } finally {
      setUpdateLoading(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

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

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Not logged in</h2>
          <Link to="/login" className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg">
            Go to Login
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        
        {/* Hero Section */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl shadow-xl p-8 mb-6 text-white">
          <div className="flex flex-col md:flex-row items-center gap-6">
            <div className="w-32 h-32 bg-white bg-opacity-20 backdrop-blur rounded-full flex items-center justify-center text-5xl font-bold shadow-lg ring-4 ring-white ring-opacity-50">
              {user.first_name?.charAt(0) || user.username?.charAt(0) || 'U'}
            </div>
            <div className="flex-1 text-center md:text-left">
              <h1 className="text-4xl font-bold mb-2">
                Welcome, {user.first_name || user.username}! 👋
              </h1>
              <p className="text-blue-100 text-lg mb-3">{user.email}</p>
              <div className="flex flex-wrap justify-center md:justify-start gap-4 text-sm">
                <span className="bg-white bg-opacity-20 px-3 py-1 rounded-full">
                  📅 Member since {new Date(user.date_joined).toLocaleDateString()}
                </span>
                {user.last_login && (
                  <span className="bg-white bg-opacity-20 px-3 py-1 rounded-full">
                    🕐 Last seen {new Date(user.last_login).toLocaleDateString()}
                  </span>
                )}
              </div>
            </div>
            {!showProfileEdit && (
              <button
                onClick={() => setShowProfileEdit(true)}
                className="px-6 py-3 bg-white text-blue-600 rounded-xl hover:bg-blue-50 transition-colors font-medium shadow-lg"
              >
                ✏️ Edit Profile
              </button>
            )}
          </div>
        </div>

        {/* Success/Error Messages */}
        {updateSuccess && (
          <div className="mb-6 bg-green-50 border border-green-200 rounded-xl p-4 text-green-800 text-center shadow-sm">
            {updateSuccess}
          </div>
        )}

        {updateError && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-xl p-4 text-red-800 text-center shadow-sm">
            {updateError}
          </div>
        )}

        {/* Edit Profile Form */}
        {showProfileEdit && (
          <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">✏️ Edit Profile</h2>
            <form onSubmit={handleProfileUpdate} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    First Name
                  </label>
                  <input
                    type="text"
                    value={profileData.first_name}
                    onChange={(e) => setProfileData({...profileData, first_name: e.target.value})}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="John"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Last Name
                  </label>
                  <input
                    type="text"
                    value={profileData.last_name}
                    onChange={(e) => setProfileData({...profileData, last_name: e.target.value})}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="Doe"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email
                </label>
                <input
                  type="email"
                  value={profileData.email}
                  onChange={(e) => setProfileData({...profileData, email: e.target.value})}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                  placeholder="john@example.com"
                />
              </div>
              <div className="flex justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowProfileEdit(false);
                    setProfileData({
                      first_name: user.first_name || '',
                      last_name: user.last_name || '',
                      email: user.email || ''
                    });
                  }}
                  className="px-6 py-3 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={updateLoading}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 font-medium"
                >
                  {updateLoading ? 'Saving...' : '💾 Save Changes'}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Statistics Dashboard */}
        {!statsLoading && statistics && (
          <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">📊 Your Statistics</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-xl text-center">
                <div className="text-3xl font-bold text-blue-600">{statistics.totalPoints}</div>
                <div className="text-sm text-blue-700 mt-1">Points</div>
              </div>
              <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-xl text-center">
                <div className="text-3xl font-bold text-purple-600">{statistics.badgesEarned}</div>
                <div className="text-sm text-purple-700 mt-1">Badges</div>
              </div>
              <div className="bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-xl text-center">
                <div className="text-3xl font-bold text-green-600">{statistics.booksRead}</div>
                <div className="text-sm text-green-700 mt-1">Books Read</div>
              </div>
              <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 p-4 rounded-xl text-center">
                <div className="text-3xl font-bold text-yellow-600">{statistics.totalReviews}</div>
                <div className="text-sm text-yellow-700 mt-1">Reviews</div>
              </div>
              <div className="bg-gradient-to-br from-orange-50 to-orange-100 p-4 rounded-xl text-center">
                <div className="text-3xl font-bold text-orange-600">{statistics.averageRating.toFixed(1)}</div>
                <div className="text-sm text-orange-700 mt-1">Avg Rating</div>
              </div>
              <div className="bg-gradient-to-br from-pink-50 to-pink-100 p-4 rounded-xl text-center">
                <div className="text-3xl font-bold text-pink-600">{statistics.totalLists}</div>
                <div className="text-sm text-pink-700 mt-1">Lists</div>
              </div>
            </div>
          </div>
        )}

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Left Column - Quick Actions */}
          <div className="lg:col-span-2 space-y-4">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">🚀 Quick Actions</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Link to="/user-favorites">
                <div className="bg-white rounded-xl shadow-md p-6 hover:shadow-xl transition-all cursor-pointer group">
                  <div className="flex items-center gap-4 mb-3">
                    <div className="w-12 h-12 bg-gradient-to-br from-red-400 to-red-600 rounded-xl flex items-center justify-center text-2xl group-hover:scale-110 transition-transform">
                      ❤️
                    </div>
                    <div>
                      <h3 className="font-bold text-gray-800 text-lg">Favorites</h3>
                      <p className="text-gray-600 text-sm">Your favorite books</p>
                    </div>
                  </div>
                </div>
              </Link>

              <Link to="/reviews">
                <div className="bg-white rounded-xl shadow-md p-6 hover:shadow-xl transition-all cursor-pointer group">
                  <div className="flex items-center gap-4 mb-3">
                    <div className="w-12 h-12 bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-xl flex items-center justify-center text-2xl group-hover:scale-110 transition-transform">
                      ⭐
                    </div>
                    <div>
                      <h3 className="font-bold text-gray-800 text-lg">Reviews</h3>
                      <p className="text-gray-600 text-sm">Manage reviews</p>
                    </div>
                  </div>
                </div>
              </Link>

              <Link to="/lists">
                <div className="bg-white rounded-xl shadow-md p-6 hover:shadow-xl transition-all cursor-pointer group">
                  <div className="flex items-center gap-4 mb-3">
                    <div className="w-12 h-12 bg-gradient-to-br from-blue-400 to-blue-600 rounded-xl flex items-center justify-center text-2xl group-hover:scale-110 transition-transform">
                      📚
                    </div>
                    <div>
                      <h3 className="font-bold text-gray-800 text-lg">My Lists</h3>
                      <p className="text-gray-600 text-sm">Organize books</p>
                    </div>
                  </div>
                </div>
              </Link>

              <Link to="/badges">
                <div className="bg-white rounded-xl shadow-md p-6 hover:shadow-xl transition-all cursor-pointer group">
                  <div className="flex items-center gap-4 mb-3">
                    <div className="w-12 h-12 bg-gradient-to-br from-purple-400 to-purple-600 rounded-xl flex items-center justify-center text-2xl group-hover:scale-110 transition-transform">
                      🏆
                    </div>
                    <div>
                      <h3 className="font-bold text-gray-800 text-lg">Badges</h3>
                      <p className="text-gray-600 text-sm">View achievements</p>
                    </div>
                  </div>
                </div>
              </Link>
            </div>
          </div>

          {/* Right Column - Settings */}
          <div className="space-y-4">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">⚙️ Settings</h2>
            
            <div className="bg-white rounded-xl shadow-md p-6">
              <div className="space-y-3">
                <button
                  onClick={() => setShowPasswordForm(!showPasswordForm)}
                  className="w-full flex items-center justify-between p-4 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">🔒</span>
                    <div className="text-left">
                      <div className="font-medium text-gray-800">Password</div>
                      <div className="text-xs text-gray-600">Change password</div>
                    </div>
                  </div>
                  <span className="text-gray-400">{showPasswordForm ? '▼' : '▶'}</span>
                </button>

                {showPasswordForm && (
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <form onSubmit={handlePasswordChange} className="space-y-3">
                      <input
                        type="password"
                        value={passwordData.current_password}
                        onChange={(e) => setPasswordData({...passwordData, current_password: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
                        placeholder="Current password"
                        required
                      />
                      <input
                        type="password"
                        value={passwordData.new_password}
                        onChange={(e) => setPasswordData({...passwordData, new_password: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
                        placeholder="New password (min 8 chars)"
                        required
                        minLength={8}
                      />
                      <input
                        type="password"
                        value={passwordData.confirm_new_password}
                        onChange={(e) => setPasswordData({...passwordData, confirm_new_password: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
                        placeholder="Confirm new password"
                        required
                      />
                      <div className="flex gap-2 pt-2">
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
                          className="flex-1 px-3 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition text-sm"
                        >
                          Cancel
                        </button>
                        <button
                          type="submit"
                          disabled={updateLoading}
                          className="flex-1 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 text-sm"
                        >
                          {updateLoading ? '...' : 'Change'}
                        </button>
                      </div>
                    </form>
                  </div>
                )}

                <hr className="border-gray-200" />

                <button
                  onClick={handleLogout}
                  className="w-full flex items-center justify-between p-4 rounded-lg hover:bg-red-50 transition-colors group"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">🚪</span>
                    <div className="text-left">
                      <div className="font-medium text-gray-800 group-hover:text-red-600">Log Out</div>
                      <div className="text-xs text-gray-600">Sign out of account</div>
                    </div>
                  </div>
                </button>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};

export default UserProfile;