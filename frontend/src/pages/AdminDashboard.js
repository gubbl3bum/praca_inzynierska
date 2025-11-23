import React, { useState, useEffect } from 'react';
import { useAuth } from '../services/AuthContext';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import ConfirmModal from '../components/ConfirmModal';

const AdminDashboard = () => {
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    // Check admin/staff permission
    if (!isAuthenticated || !user?.is_staff) {
      navigate('/');
      return;
    }
    
    loadDashboardData();
  }, [isAuthenticated, user, navigate]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [statsData, healthData] = await Promise.all([
        api.admin.getDashboardStats(),
        api.admin.getSystemHealth()
      ]);
      
      setStats(statsData.stats);
      setHealth(healthData.health);
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRecalculateSimilarities = async (type) => {
    if (!window.confirm(`Are you sure you want to recalculate ${type} similarities? This may take a while.`)) {
      return;
    }

    try {
      setProcessing(true);
      const response = type === 'book' 
        ? await api.admin.recalculateBookSimilarities({ limit: 10 })
        : await api.admin.recalculateUserSimilarities({ limit: 10 });
      
      alert(response.message || 'Recalculation completed successfully!');
      loadDashboardData();
    } catch (error) {
      alert('Error: ' + (error.message || 'Recalculation failed'));
    } finally {
      setProcessing(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading admin panel...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900">Admin Panel</h1>
          <p className="text-gray-600">System management and statistics</p>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex space-x-4 border-b border-gray-200 overflow-x-auto">
          {['dashboard', 'users', 'books', 'authors', 'publishers', 'reviews', 'badges', 'categories', 'system'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 font-medium capitalize whitespace-nowrap ${
                activeTab === tab
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Dashboard Tab */}
        {activeTab === 'dashboard' && stats && (
          <div className="space-y-6">
            {/* System Health */}
            <div className={`p-4 rounded-lg ${
              health?.overall_status === 'healthy' ? 'bg-green-100 border-green-400' :
              health?.overall_status === 'warning' ? 'bg-yellow-100 border-yellow-400' :
              'bg-red-100 border-red-400'
            } border`}>
              <h3 className="font-bold mb-2">System Health: {health?.overall_status?.toUpperCase()}</h3>
              {health?.issues?.length > 0 && (
                <ul className="list-disc list-inside">
                  {health.issues.map((issue, idx) => (
                    <li key={idx}>{issue}</li>
                  ))}
                </ul>
              )}
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {/* Content Stats */}
              <StatsCard
                title="Books"
                value={stats.content.total_books}
                color="blue"
              />
              <StatsCard
                title="Authors"
                value={stats.content.total_authors}
                color="green"
              />
              <StatsCard
                title="Users"
                value={stats.users.total_users}
                color="purple"
              />
              <StatsCard
                title="Reviews"
                value={stats.reviews.total_reviews}
                color="yellow"
              />
            </div>

            {/* Recommendations */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold mb-4">Recommendation System</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-gray-600 mb-2">Book Similarities</p>
                  <p className="text-2xl font-bold">{stats.recommendations.book_similarities}</p>
                  <p className="text-sm text-gray-500">Coverage: {stats.recommendations.coverage_books}%</p>
                </div>
                <div>
                  <p className="text-gray-600 mb-2">User Similarities</p>
                  <p className="text-2xl font-bold">{stats.recommendations.user_similarities}</p>
                </div>
              </div>
              <div className="mt-4 flex gap-4">
                <button
                  onClick={() => handleRecalculateSimilarities('book')}
                  disabled={processing}
                  className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:bg-gray-400"
                >
                  {processing ? 'Processing...' : 'Recalculate Book Similarities'}
                </button>
                <button
                  onClick={() => handleRecalculateSimilarities('user')}
                  disabled={processing}
                  className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:bg-gray-400"
                >
                  {processing ? 'Processing...' : 'Recalculate User Similarities'}
                </button>
              </div>
            </div>

            {/* Top Books */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold mb-4">Top Books (by reviews)</h2>
              <div className="space-y-2">
                {stats.top_books.map((book, idx) => (
                  <div key={book.id} className="flex justify-between items-center p-2 hover:bg-gray-50 rounded">
                    <span className="font-medium">{idx + 1}. {book.title}</span>
                    <span className="text-gray-600">{book.review_count} reviews</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Users Tab */}
        {activeTab === 'users' && <UserManagement />}

        {/* Books Tab */}
        {activeTab === 'books' && <BooksManagement />}

        {/* Reviews Tab */}
        {activeTab === 'reviews' && <ReviewsManagement />}

        {/* Badges Tab */}
        {activeTab === 'badges' && <BadgesManagement />}

        {/* Categories Tab */}
        {activeTab === 'categories' && <CategoriesManagement />}

        {/* Authors Tab */}
        {activeTab === 'authors' && <AuthorsManagement />}

        {/* Publishers Tab */}
        {activeTab === 'publishers' && <PublishersManagement />}

        {/* System Tab */}
        {activeTab === 'system' && health && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4">System Status</h2>
            <div className="space-y-4">
              <StatusRow label="Database" status={health.database_ok ? 'OK' : 'ERROR'} />
              <StatusRow label="Similarity Coverage" value={`${health.similarity_coverage}%`} />
              <StatusRow label="Active Users" value={`${health.active_users_percentage}%`} />
              <StatusRow label="User Engagement" value={`${health.user_engagement_rate}%`} />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

const StatsCard = ({ title, value, icon, color }) => {
  const colors = {
    blue: 'bg-blue-100 text-blue-800',
    green: 'bg-green-100 text-green-800',
    purple: 'bg-purple-100 text-purple-800',
    yellow: 'bg-yellow-100 text-yellow-800',
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-600 text-sm">{title}</p>
          <p className="text-3xl font-bold mt-2">{value}</p>
        </div>
        <div className={`text-4xl ${colors[color]} p-3 rounded-lg`}>
          {icon}
        </div>
      </div>
    </div>
  );
};

const StatusRow = ({ label, status, value }) => (
  <div className="flex justify-between items-center p-3 bg-gray-50 rounded">
    <span className="font-medium">{label}</span>
    {status && (
      <span className={`px-3 py-1 rounded ${
        status === 'OK' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
      }`}>
        {status}
      </span>
    )}
    {value && <span className="text-gray-600">{value}</span>}
  </div>
);

const UserManagement = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    search: '',
    has_reviews: '',
    is_active: '',
    sort: '-date_joined'
  });
  const [debouncedFilters, setDebouncedFilters] = useState(filters);
  const [pagination, setPagination] = useState({
    currentPage: 1,
    totalPages: 1,
    totalItems: 0,
    pageSize: 20
  });
  const [editingUser, setEditingUser] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showToggleModal, setShowToggleModal] = useState(false);
  const [userToToggle, setUserToToggle] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedFilters(filters);
    }, 500);
    return () => clearTimeout(timer);
  }, [filters]);

  useEffect(() => {
    loadUsers(1);
  }, [debouncedFilters]);

  const loadUsers = async (page = 1) => {
    try {
      setLoading(true);
      setError(null);
      
      const params = {
        page,
        page_size: 20,
        ...debouncedFilters
      };

      Object.keys(params).forEach(key => {
        if (params[key] === '' || params[key] === null || params[key] === undefined) {
          delete params[key];
        }
      });

      const data = await api.admin.getUsers(params);
      setUsers(data.users || []);
      
      setPagination({
        currentPage: data.pagination?.page || page,
        totalPages: data.pagination?.total_pages || 1,
        totalItems: data.pagination?.total || 0,
        pageSize: data.pagination?.page_size || 20
      });
    } catch (error) {
      console.error('Error loading users:', error);
      setError(api.handleError(error, 'Failed to load users'));
      setUsers([]);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (user) => {
    setEditingUser({
      ...user,
      first_name: user.first_name || '',
      last_name: user.last_name || ''
    });
    setShowEditModal(true);
  };

  const handleSaveEdit = async (e) => {
    e.preventDefault();
    setIsProcessing(true);
    try {
      await api.admin.updateUser(editingUser.id, {
        first_name: editingUser.first_name,
        last_name: editingUser.last_name,
        is_staff: editingUser.is_staff,
        is_active: editingUser.is_active
      });
      setShowEditModal(false);
      setEditingUser(null);
      loadUsers(pagination.currentPage);
    } catch (error) {
      alert('Error: ' + error.message);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleToggleClick = (user) => {
    setUserToToggle(user);
    setShowToggleModal(true);
  };

  const handleToggleConfirm = async () => {
    setIsProcessing(true);
    try {
      await api.admin.toggleUserStatus(userToToggle.id);
      setShowToggleModal(false);
      setUserToToggle(null);
      loadUsers(pagination.currentPage);
    } catch (error) {
      alert('Error: ' + error.message);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleFilterChange = (name, value) => {
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSearch = (e) => {
    e.preventDefault();
    loadUsers(1);
  };

  const resetFilters = () => {
    setFilters({
      search: '',
      has_reviews: '',
      is_active: '',
      sort: '-date_joined'
    });
  };

  const handlePageChange = (newPage) => {
    loadUsers(newPage);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const generatePageNumbers = () => {
    return api.pagination.generatePageNumbers(pagination.currentPage, pagination.totalPages, 5);
  };

  const sortOptions = [
    { value: '-date_joined', label: 'Newest First' },
    { value: 'date_joined', label: 'Oldest First' },
    { value: 'username', label: 'Username A-Z' },
    { value: '-username', label: 'Username Z-A' },
  ];

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4 text-gray-800">Search & Filter Users</h2>
        
        <form onSubmit={handleSearch} className="mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <input
                type="text"
                placeholder="Search by username, email, name..."
                value={filters.search}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              {loading && filters.search && (
                <div className="absolute right-3 top-3">
                  <div className="animate-spin h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
                </div>
              )}
            </div>
            <button
              type="submit"
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              🔍 Search
            </button>
          </div>
        </form>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Review Status</label>
            <select
              value={filters.has_reviews}
              onChange={(e) => handleFilterChange('has_reviews', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Users</option>
              <option value="true">Has Reviews</option>
              <option value="false">No Reviews</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Account Status</label>
            <select
              value={filters.is_active}
              onChange={(e) => handleFilterChange('is_active', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Statuses</option>
              <option value="true">Active</option>
              <option value="false">Inactive</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Sort By</label>
            <select
              value={filters.sort}
              onChange={(e) => handleFilterChange('sort', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500"
            >
              {sortOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-end">
            <button
              onClick={resetFilters}
              className="w-full px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 transition-colors"
            >
              🔄 Reset Filters
            </button>
          </div>
        </div>
      </div>

      {/* Loading/Error */}
      {loading && (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading users...</p>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="text-red-800 text-center">
            <div className="text-4xl mb-2">⚠️</div>
            <h3 className="text-lg font-semibold mb-2">Error Loading Users</h3>
            <p className="mb-4">{error}</p>
            <button
              onClick={() => loadUsers(pagination.currentPage)}
              className="bg-red-600 hover:bg-red-700 text-white px-6 py-2 rounded-lg"
            >
              Try Again
            </button>
          </div>
        </div>
      )}

      {/* User table */}
      {!loading && !error && users.length > 0 && (
        <>
          <div className="flex justify-between items-center">
            <p className="text-gray-600">
              Showing {((pagination.currentPage - 1) * pagination.pageSize) + 1}-{Math.min(pagination.currentPage * pagination.pageSize, pagination.totalItems)} of {pagination.totalItems.toLocaleString()} users
            </p>
          </div>

          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Reviews</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Joined</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {users.map(user => (
                    <tr key={user.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10">
                            <div className="h-10 w-10 rounded-full bg-blue-600 flex items-center justify-center text-white font-medium">
                              {user.username?.charAt(0)?.toUpperCase() || 'U'}
                            </div>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">
                              {user.username}
                              {user.is_staff && (
                                <span className="ml-2 px-2 py-0.5 text-xs bg-purple-100 text-purple-800 rounded">Admin</span>
                              )}
                            </div>
                            <div className="text-sm text-gray-500">{user.full_name}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{user.email}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {user.review_count || 0}
                          {user.avg_rating && (
                            <span className="text-gray-500 ml-2">(avg: {user.avg_rating})</span>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(user.date_joined).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        }`}>
                          {user.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-3">
                            <button
                              onClick={() => handleEdit(user)}
                              className="text-blue-600 hover:text-blue-900 inline-flex items-center gap-1"
                            >
                              <span>Edit</span>
                            </button>
                            <button
                              onClick={() => handleToggleClick(user)}
                              disabled={loading}
                              className="text-yellow-600 hover:text-yellow-900"
                            >
                              {user.is_active ? 'Deactivate' : 'Activate'}
                            </button>
                          </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Pagination */}
          {pagination.totalPages > 1 && (
            <div className="flex justify-center items-center gap-2 py-6">
              <button
                onClick={() => handlePageChange(pagination.currentPage - 1)}
                disabled={pagination.currentPage === 1}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  pagination.currentPage > 1
                    ? 'bg-blue-600 hover:bg-blue-700 text-white cursor-pointer'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                ← Previous
              </button>

              {pagination.currentPage > 3 && (
                <>
                  <button
                    onClick={() => handlePageChange(1)}
                    className="px-4 py-2 rounded-lg bg-white text-gray-700 hover:bg-gray-100 border border-gray-300"
                  >
                    1
                  </button>
                  {pagination.currentPage > 4 && <span className="px-2 text-gray-500">...</span>}
                </>
              )}

              {generatePageNumbers().map(pageNum => (
                <button
                  key={pageNum}
                  onClick={() => handlePageChange(pageNum)}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    pageNum === pagination.currentPage
                      ? 'bg-blue-600 text-white'
                      : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
                  }`}
                >
                  {pageNum}
                </button>
              ))}

              {pagination.currentPage < pagination.totalPages - 2 && (
                <>
                  {pagination.currentPage < pagination.totalPages - 3 && <span className="px-2 text-gray-500">...</span>}
                  <button
                    onClick={() => handlePageChange(pagination.totalPages)}
                    className="px-4 py-2 rounded-lg bg-white text-gray-700 hover:bg-gray-100 border border-gray-300"
                  >
                    {pagination.totalPages}
                  </button>
                </>
              )}

              <button
                onClick={() => handlePageChange(pagination.currentPage + 1)}
                disabled={pagination.currentPage === pagination.totalPages}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  pagination.currentPage < pagination.totalPages
                    ? 'bg-blue-600 hover:bg-blue-700 text-white cursor-pointer'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                Next →
              </button>
            </div>
          )}
        </>
      )}

      {/* Edit User Modal */}
      {showEditModal && editingUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-bold mb-4">Edit User</h3>
            <form onSubmit={handleSaveEdit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Username</label>
                <input
                  type="text"
                  value={editingUser.username}
                  disabled
                  className="w-full px-4 py-2 border rounded-lg bg-gray-100 text-gray-600"
                />
                <p className="text-xs text-gray-500 mt-1">Username cannot be changed</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input
                  type="email"
                  value={editingUser.email}
                  disabled
                  className="w-full px-4 py-2 border rounded-lg bg-gray-100 text-gray-600"
                />
                <p className="text-xs text-gray-500 mt-1">Email cannot be changed</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                  <input
                    type="text"
                    value={editingUser.first_name}
                    onChange={(e) => setEditingUser({...editingUser, first_name: e.target.value})}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
                  <input
                    type="text"
                    value={editingUser.last_name}
                    onChange={(e) => setEditingUser({...editingUser, last_name: e.target.value})}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div className="flex items-center space-x-6">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={editingUser.is_staff}
                    onChange={(e) => setEditingUser({...editingUser, is_staff: e.target.checked})}
                    className="mr-2 w-4 h-4"
                  />
                  <span className="text-sm font-medium text-gray-700">Staff / Admin</span>
                </label>

                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={editingUser.is_active}
                    onChange={(e) => setEditingUser({...editingUser, is_active: e.target.checked})}
                    className="mr-2 w-4 h-4"
                  />
                  <span className="text-sm font-medium text-gray-700">Active</span>
                </label>
              </div>

              <div className="flex justify-end gap-4 mt-6">
                <button
                  type="button"
                  onClick={() => {
                    setShowEditModal(false);
                    setEditingUser(null);
                  }}
                  disabled={isProcessing}
                  className="px-6 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 disabled:bg-gray-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isProcessing}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-blue-300"
                >
                  {isProcessing ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Toggle Status Confirmation Modal */}
      <ConfirmModal
        isOpen={showToggleModal}
        onClose={() => {
          setShowToggleModal(false);
          setUserToToggle(null);
        }}
        onConfirm={handleToggleConfirm}
        title={`${userToToggle?.is_active ? 'Deactivate' : 'Activate'} User`}
        message={`Are you sure you want to ${userToToggle?.is_active ? 'deactivate' : 'activate'} user "${userToToggle?.username}"?`}
        confirmText={userToToggle?.is_active ? 'Deactivate' : 'Activate'}
        confirmColor={userToToggle?.is_active ? 'yellow' : 'green'}
        isProcessing={isProcessing}
      />
    </div>
  );
};

// =============================================================================
// BOOKS MANAGEMENT COMPONENT
// =============================================================================

const BooksManagement = () => {
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    search: '',
    category: '',
    sort: '-created_at'
  });
  const [debouncedFilters, setDebouncedFilters] = useState(filters);
  const [pagination, setPagination] = useState({
    currentPage: 1,
    totalPages: 1,
    totalItems: 0,
    pageSize: 20
  });
  const [editingBook, setEditingBook] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);

  // Debounce
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedFilters(filters);
    }, 500);
    return () => clearTimeout(timer);
  }, [filters]);

  // Load books
  useEffect(() => {
    loadBooks(1);
  }, [debouncedFilters]);

  const loadBooks = async (page = 1) => {
    try {
      setLoading(true);
      setError(null);
      
      const params = {
        page,
        page_size: 20,
        ...debouncedFilters
      };

      Object.keys(params).forEach(key => {
        if (params[key] === '' || params[key] === null) {
          delete params[key];
        }
      });

      const data = await api.admin.getBooks(params);
      setBooks(data.books || []);
      
      setPagination({
        currentPage: data.pagination?.page || page,
        totalPages: data.pagination?.total_pages || 1,
        totalItems: data.pagination?.total || 0,
        pageSize: data.pagination?.page_size || 20
      });
    } catch (error) {
      console.error('Error loading books:', error);
      setError(api.handleError(error, 'Failed to load books'));
      setBooks([]);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (book) => {
    setEditingBook(book);
    setShowEditModal(true);
  };

  const handleDelete = async (bookId) => {
    if (!window.confirm('Are you sure you want to delete this book? This action cannot be undone.')) {
      return;
    }

    try {
      await api.admin.deleteBook(bookId);
      alert('Book deleted successfully');
      loadBooks(pagination.currentPage);
    } catch (error) {
      alert('Error: ' + (error.message || 'Failed to delete book'));
    }
  };

  const handleSaveEdit = async (e) => {
    e.preventDefault();
    
    try {
      await api.admin.updateBook(editingBook.id, {
        title: editingBook.title,
        description: editingBook.description,
        price: editingBook.price,
        publish_year: editingBook.publish_year
      });
      
      alert('Book updated successfully');
      setShowEditModal(false);
      setEditingBook(null);
      loadBooks(pagination.currentPage);
    } catch (error) {
      alert('Error: ' + (error.message || 'Failed to update book'));
    }
  };

  const handleFilterChange = (name, value) => {
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  const resetFilters = () => {
    setFilters({ search: '', category: '', sort: '-created_at' });
  };

  const handlePageChange = (newPage) => {
    loadBooks(newPage);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const generatePageNumbers = () => {
    return api.pagination.generatePageNumbers(pagination.currentPage, pagination.totalPages, 5);
  };

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4 text-gray-800">Search & Filter Books</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="relative">
            <input
              type="text"
              placeholder="Search by title, description..."
              value={filters.search}
              onChange={(e) => handleFilterChange('search', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            {loading && filters.search && (
              <div className="absolute right-3 top-3">
                <div className="animate-spin h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
              </div>
            )}
          </div>

          <input
            type="text"
            placeholder="Category..."
            value={filters.category}
            onChange={(e) => handleFilterChange('category', e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />

          <button
            onClick={resetFilters}
            className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
          >
            🔄 Reset
          </button>
        </div>
      </div>

      {/* Loading */}
      {loading && (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading books...</p>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Results */}
      {!loading && !error && (
        <>
          <div className="flex justify-between items-center">
            <p className="text-gray-600">
              Showing {books.length} of {pagination.totalItems.toLocaleString()} books
            </p>
          </div>

          {books.length > 0 ? (
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Title</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Authors</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Year</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reviews</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rating</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {books.map(book => (
                    <tr key={book.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div className="text-sm font-medium text-gray-900">{book.title}</div>
                        {book.description && (
                          <div className="text-sm text-gray-500 truncate max-w-xs">{book.description}</div>
                        )}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">{book.authors || 'Unknown'}</td>
                      <td className="px-6 py-4 text-sm text-gray-500">{book.publish_year || 'N/A'}</td>
                      <td className="px-6 py-4 text-sm text-gray-500">{book.review_count || 0}</td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        {book.avg_rating ? `${book.avg_rating}/10` : 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-3">
                          <button
                            onClick={() => handleEdit(book)}
                            className="text-blue-600 hover:text-blue-900 inline-flex items-center gap-1"
                          >
                            <span>Edit</span>
                          </button>
                          <button
                            onClick={() => handleDelete(book.id)}
                            className="text-red-600 hover:text-red-900 inline-flex items-center gap-1"
                          >
                            <span>Delete</span>
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow p-12 text-center">
              <div className="text-6xl mb-4">📚</div>
              <h3 className="text-xl font-semibold text-gray-700 mb-2">No Books Found</h3>
            </div>
          )}

          {/* Pagination */}
          {pagination.totalPages > 1 && (
            <div className="flex justify-center items-center gap-2 py-6">
              <button
                onClick={() => handlePageChange(pagination.currentPage - 1)}
                disabled={pagination.currentPage === 1}
                className={`px-4 py-2 rounded-lg ${
                  pagination.currentPage > 1
                    ? 'bg-blue-600 hover:bg-blue-700 text-white'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                ← Previous
              </button>

              {generatePageNumbers().map(pageNum => (
                <button
                  key={pageNum}
                  onClick={() => handlePageChange(pageNum)}
                  className={`px-4 py-2 rounded-lg ${
                    pageNum === pagination.currentPage
                      ? 'bg-blue-600 text-white'
                      : 'bg-white text-gray-700 hover:bg-gray-100 border'
                  }`}
                >
                  {pageNum}
                </button>
              ))}

              <button
                onClick={() => handlePageChange(pagination.currentPage + 1)}
                disabled={pagination.currentPage === pagination.totalPages}
                className={`px-4 py-2 rounded-lg ${
                  pagination.currentPage < pagination.totalPages
                    ? 'bg-blue-600 hover:bg-blue-700 text-white'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                Next →
              </button>
            </div>
          )}
        </>
      )}

      {/* Edit Modal */}
      {showEditModal && editingBook && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <h3 className="text-xl font-bold mb-4">Edit Book</h3>
            <form onSubmit={handleSaveEdit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
                <input
                  type="text"
                  value={editingBook.title}
                  onChange={(e) => setEditingBook({...editingBook, title: e.target.value})}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  value={editingBook.description || ''}
                  onChange={(e) => setEditingBook({...editingBook, description: e.target.value})}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  rows="4"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Price</label>
                  <input
                    type="number"
                    step="0.01"
                    value={editingBook.price || ''}
                    onChange={(e) => setEditingBook({...editingBook, price: e.target.value})}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Year</label>
                  <input
                    type="number"
                    value={editingBook.publish_year || ''}
                    onChange={(e) => setEditingBook({...editingBook, publish_year: e.target.value})}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-4 mt-6">
                <button
                  type="button"
                  onClick={() => {
                    setShowEditModal(false);
                    setEditingBook(null);
                  }}
                  className="px-6 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

// =============================================================================
// AUTHORS MANAGEMENT COMPONENT
// =============================================================================

const AuthorsManagement = () => {
  const [authors, setAuthors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [pagination, setPagination] = useState({
    currentPage: 1,
    totalPages: 1,
    totalItems: 0,
    pageSize: 20
  });
  const [editingAuthor, setEditingAuthor] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newAuthor, setNewAuthor] = useState({ first_name: '', last_name: '' });

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearch(search), 500);
    return () => clearTimeout(timer);
  }, [search]);

  useEffect(() => {
    loadAuthors(1);
  }, [debouncedSearch]);

  const loadAuthors = async (page = 1) => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.admin.getAuthors({ search: debouncedSearch, page, page_size: 20 });
      setAuthors(data.authors || []);
      setPagination({
        currentPage: data.pagination?.page || page,
        totalPages: data.pagination?.total_pages || 1,
        totalItems: data.pagination?.total || 0,
        pageSize: data.pagination?.page_size || 20
      });
    } catch (error) {
      setError(api.handleError(error, 'Failed to load authors'));
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await api.admin.createAuthor(newAuthor);
      alert('Author created successfully');
      setShowCreateModal(false);
      setNewAuthor({ first_name: '', last_name: '' });
      loadAuthors(1);
    } catch (error) {
      alert('Error: ' + error.message);
    }
  };

  const handleEdit = (author) => {
    setEditingAuthor(author);
    setShowEditModal(true);
  };

  const handleSaveEdit = async (e) => {
    e.preventDefault();
    try {
      await api.admin.updateAuthor(editingAuthor.id, {
        first_name: editingAuthor.first_name,
        last_name: editingAuthor.last_name
      });
      alert('Author updated successfully');
      setShowEditModal(false);
      setEditingAuthor(null);
      loadAuthors(pagination.currentPage);
    } catch (error) {
      alert('Error: ' + error.message);
    }
  };

  const handleDelete = async (authorId) => {
    if (!window.confirm('Are you sure? This will fail if the author has books.')) return;
    try {
      await api.admin.deleteAuthor(authorId);
      alert('Author deleted successfully');
      loadAuthors(pagination.currentPage);
    } catch (error) {
      alert('Error: ' + error.message);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Authors Management</h2>
        <button
          onClick={() => setShowCreateModal(true)}
          className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
        >
          ➕ Add Author
        </button>
      </div>

      {/* Search */}
      <div className="bg-white rounded-lg shadow p-6">
        <input
          type="text"
          placeholder="Search authors..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <p className="text-red-800">{error}</p>
        </div>
      ) : (
        <>
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Books</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {authors.map(author => (
                  <tr key={author.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">{author.full_name}</td>
                    <td className="px-6 py-4 text-sm text-gray-500">{author.book_count}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-3">
                      <button
                        onClick={() => handleEdit(author)}
                        className="text-blue-600 hover:text-blue-900 inline-flex items-center gap-1"
                      >
                        <span>Edit</span>
                      </button>

                      <button
                        onClick={() => handleDelete(author.id)}
                        className="text-red-600 hover:text-red-900 inline-flex items-center gap-1"
                      >
                        <span>Delete</span>
                      </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-bold mb-4">Create New Author</h3>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                <input
                  type="text"
                  value={newAuthor.first_name}
                  onChange={(e) => setNewAuthor({...newAuthor, first_name: e.target.value})}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Last Name *</label>
                <input
                  type="text"
                  value={newAuthor.last_name}
                  onChange={(e) => setNewAuthor({...newAuthor, last_name: e.target.value})}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div className="flex justify-end gap-4">
                <button type="button" onClick={() => setShowCreateModal(false)} className="px-6 py-2 bg-gray-500 text-white rounded-lg">
                  Cancel
                </button>
                <button type="submit" className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {showEditModal && editingAuthor && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-bold mb-4">Edit Author</h3>
            <form onSubmit={handleSaveEdit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                <input
                  type="text"
                  value={editingAuthor.first_name}
                  onChange={(e) => setEditingAuthor({...editingAuthor, first_name: e.target.value})}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Last Name *</label>
                <input
                  type="text"
                  value={editingAuthor.last_name}
                  onChange={(e) => setEditingAuthor({...editingAuthor, last_name: e.target.value})}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div className="flex justify-end gap-4">
                <button type="button" onClick={() => setShowEditModal(false)} className="px-6 py-2 bg-gray-500 text-white rounded-lg">
                  Cancel
                </button>
                <button type="submit" className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                  Save
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

// =============================================================================
// PUBLISHERS MANAGEMENT COMPONENT
// =============================================================================

const PublishersManagement = () => {
  const [publishers, setPublishers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [pagination, setPagination] = useState({
    currentPage: 1,
    totalPages: 1,
    totalItems: 0,
    pageSize: 20
  });
  const [editingPublisher, setEditingPublisher] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newPublisher, setNewPublisher] = useState({ name: '' });

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearch(search), 500);
    return () => clearTimeout(timer);
  }, [search]);

  useEffect(() => {
    loadPublishers(1);
  }, [debouncedSearch]);

  const loadPublishers = async (page = 1) => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.admin.getPublishers({ search: debouncedSearch, page, page_size: 20 });
      setPublishers(data.publishers || []);
      setPagination({
        currentPage: data.pagination?.page || page,
        totalPages: data.pagination?.total_pages || 1,
        totalItems: data.pagination?.total || 0,
        pageSize: data.pagination?.page_size || 20
      });
    } catch (error) {
      setError(api.handleError(error, 'Failed to load publishers'));
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await api.admin.createPublisher(newPublisher);
      alert('Publisher created successfully');
      setShowCreateModal(false);
      setNewPublisher({ name: '' });
      loadPublishers(1);
    } catch (error) {
      alert('Error: ' + error.message);
    }
  };

  const handleEdit = (publisher) => {
    setEditingPublisher(publisher);
    setShowEditModal(true);
  };

  const handleSaveEdit = async (e) => {
    e.preventDefault();
    try {
      await api.admin.updatePublisher(editingPublisher.id, { name: editingPublisher.name });
      alert('Publisher updated successfully');
      setShowEditModal(false);
      setEditingPublisher(null);
      loadPublishers(pagination.currentPage);
    } catch (error) {
      alert('Error: ' + error.message);
    }
  };

  const handleDelete = async (publisherId) => {
    if (!window.confirm('Are you sure? This will fail if the publisher has books.')) return;
    try {
      await api.admin.deletePublisher(publisherId);
      alert('Publisher deleted successfully');
      loadPublishers(pagination.currentPage);
    } catch (error) {
      alert('Error: ' + error.message);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Publishers Management</h2>
        <button
          onClick={() => setShowCreateModal(true)}
          className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
        >
          ➕ Add Publisher
        </button>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <input
          type="text"
          placeholder="Search publishers..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <p className="text-red-800">{error}</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Books</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {publishers.map(publisher => (
                <tr key={publisher.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">{publisher.name}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">{publisher.book_count}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-3">
                      <button
                        onClick={() => handleEdit(publisher)}
                        className="text-blue-600 hover:text-blue-900 inline-flex items-center gap-1"
                      >
                        <span>Edit</span>
                      </button>

                      <button
                        onClick={() => handleDelete(publisher.id)}
                        className="text-red-600 hover:text-red-900 inline-flex items-center gap-1"
                      >
                        <span>Delete</span>
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-bold mb-4">Create New Publisher</h3>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name *</label>
                <input
                  type="text"
                  value={newPublisher.name}
                  onChange={(e) => setNewPublisher({name: e.target.value})}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div className="flex justify-end gap-4">
                <button type="button" onClick={() => setShowCreateModal(false)} className="px-6 py-2 bg-gray-500 text-white rounded-lg">Cancel</button>
                <button type="submit" className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">Create</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {showEditModal && editingPublisher && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-bold mb-4">Edit Publisher</h3>
            <form onSubmit={handleSaveEdit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name *</label>
                <input
                  type="text"
                  value={editingPublisher.name}
                  onChange={(e) => setEditingPublisher({...editingPublisher, name: e.target.value})}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div className="flex justify-end gap-4">
                <button type="button" onClick={() => setShowEditModal(false)} className="px-6 py-2 bg-gray-500 text-white rounded-lg">Cancel</button>
                <button type="submit" className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">Save</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

// =============================================================================
// REVIEWS MANAGEMENT COMPONENT
// =============================================================================

const ReviewsManagement = () => {
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({ search: '', rating: '' });
  const [debouncedFilters, setDebouncedFilters] = useState(filters);
  const [pagination, setPagination] = useState({
    currentPage: 1,
    totalPages: 1,
    totalItems: 0,
    pageSize: 20
  });
  const [editingReview, setEditingReview] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [reviewToDelete, setReviewToDelete] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedFilters(filters), 500);
    return () => clearTimeout(timer);
  }, [filters]);

  useEffect(() => {
    loadReviews(1);
  }, [debouncedFilters]);

  const loadReviews = async (page = 1) => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.admin.getReviews({ ...debouncedFilters, page, page_size: 20 });
      setReviews(data.reviews || []);
      setPagination({
        currentPage: data.pagination?.page || page,
        totalPages: data.pagination?.total_pages || 1,
        totalItems: data.pagination?.total || 0,
        pageSize: data.pagination?.page_size || 20
      });
    } catch (error) {
      setError(api.handleError(error, 'Failed to load reviews'));
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (review) => {
    setEditingReview(review);
    setShowEditModal(true);
  };

  const handleSaveEdit = async (e) => {
    e.preventDefault();
    setIsProcessing(true);
    try {
      await api.admin.updateReview(editingReview.id, {
        rating: editingReview.rating,
        review_text: editingReview.review_text
      });
      setShowEditModal(false);
      setEditingReview(null);
      loadReviews(pagination.currentPage);
    } catch (error) {
      alert('Error: ' + error.message);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDeleteClick = (review) => {
    setReviewToDelete(review);
    setShowDeleteModal(true);
  };

  const handleDeleteConfirm = async () => {
    setIsProcessing(true);
    try {
      await api.admin.deleteReview(reviewToDelete.id);
      setShowDeleteModal(false);
      setReviewToDelete(null);
      loadReviews(pagination.currentPage);
    } catch (error) {
      alert('Error: ' + error.message);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Reviews Management</h2>

      <div className="bg-white rounded-lg shadow p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <input
            type="text"
            placeholder="Search by user, book, or review text..."
            value={filters.search}
            onChange={(e) => setFilters({...filters, search: e.target.value})}
            className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          />
          <select
            value={filters.rating}
            onChange={(e) => setFilters({...filters, rating: e.target.value})}
            className="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Ratings</option>
            {[10,9,8,7,6,5,4,3,2,1].map(r => <option key={r} value={r}>{r}/10</option>)}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <p className="text-red-800">{error}</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Book</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rating</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Review</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {reviews.map(review => (
                <tr key={review.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm text-gray-900">{review.user}</td>
                  <td className="px-6 py-4 text-sm text-gray-900 max-w-xs truncate">{review.book}</td>
                  <td className="px-6 py-4 text-sm">
                    <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded font-medium">
                      {review.rating}/10
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
                    {review.review_text || <span className="text-gray-400 italic">No text</span>}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500 whitespace-nowrap">
                    {new Date(review.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-3">
                        <button
                        onClick={() => handleEdit(review)}
                        className="text-blue-600 hover:text-blue-900 inline-flex items-center gap-1"
                      >
                        <span>Edit</span>
                      </button>

                      <button
                        onClick={() => handleDeleteClick(review)}
                        className="text-red-600 hover:text-red-900 inline-flex items-center gap-1"
                      >
                        <span>Delete</span>
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Edit Modal */}
      {showEditModal && editingReview && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4">
            <h3 className="text-xl font-bold mb-4">Edit Review</h3>
            <form onSubmit={handleSaveEdit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">User</label>
                <input
                  type="text"
                  value={editingReview.user}
                  disabled
                  className="w-full px-4 py-2 border rounded-lg bg-gray-100 text-gray-600"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Book</label>
                <input
                  type="text"
                  value={editingReview.book}
                  disabled
                  className="w-full px-4 py-2 border rounded-lg bg-gray-100 text-gray-600"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Rating (1-10) *</label>
                <input
                  type="number"
                  min="1"
                  max="10"
                  value={editingReview.rating}
                  onChange={(e) => setEditingReview({...editingReview, rating: parseInt(e.target.value)})}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Review Text</label>
                <textarea
                  value={editingReview.review_text || ''}
                  onChange={(e) => setEditingReview({...editingReview, review_text: e.target.value})}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  rows="4"
                  placeholder="Review text (optional)"
                />
              </div>

              <div className="flex justify-end gap-4 mt-6">
                <button
                  type="button"
                  onClick={() => {
                    setShowEditModal(false);
                    setEditingReview(null);
                  }}
                  disabled={isProcessing}
                  className="px-6 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 disabled:bg-gray-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isProcessing}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-blue-300"
                >
                  {isProcessing ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      <ConfirmModal
        isOpen={showDeleteModal}
        onClose={() => {
          setShowDeleteModal(false);
          setReviewToDelete(null);
        }}
        onConfirm={handleDeleteConfirm}
        title="Delete Review"
        message={`Are you sure you want to delete this review by ${reviewToDelete?.user} for "${reviewToDelete?.book}"?`}
        confirmText="Delete"
        confirmColor="red"
        isProcessing={isProcessing}
      />
    </div>
  );
};

// =============================================================================
// BADGES MANAGEMENT COMPONENT
// =============================================================================

const BadgesManagement = () => {
  const [badges, setBadges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editingBadge, setEditingBadge] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [badgeToDelete, setBadgeToDelete] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const rarityOptions = [
    { value: 'common', label: 'Common', color: 'bg-gray-100 text-gray-800' },
    { value: 'rare', label: 'Rare', color: 'bg-blue-100 text-blue-800' },
    { value: 'epic', label: 'Epic', color: 'bg-purple-100 text-purple-800' },
    { value: 'legendary', label: 'Legendary', color: 'bg-yellow-100 text-yellow-800' }
  ];

  const categoryOptions = [
    { value: 'reviews', label: 'Reviews' },
    { value: 'reading', label: 'Reading' },
    { value: 'collections', label: 'Collections' },
    { value: 'discovery', label: 'Discovery' },
    { value: 'social', label: 'Social' },
    { value: 'time', label: 'Time-based' },
    { value: 'special', label: 'Special' }
  ];

  useEffect(() => {
    loadBadges();
  }, []);

  const loadBadges = async () => {
    try {
      setLoading(true);
      const data = await api.admin.getBadges();
      setBadges(data.badges || []);
    } catch (error) {
      setError(api.handleError(error, 'Failed to load badges'));
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (badge) => {
    setEditingBadge(badge);
    setShowEditModal(true);
  };

  const handleSaveEdit = async (e) => {
    e.preventDefault();
    setIsProcessing(true);
    try {
      await api.admin.updateBadge(editingBadge.id, editingBadge);
      setShowEditModal(false);
      setEditingBadge(null);
      loadBadges();
    } catch (error) {
      alert('Error: ' + error.message);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDeleteClick = (badge) => {
    setBadgeToDelete(badge);
    setShowDeleteModal(true);
  };

  const handleDeleteConfirm = async () => {
    setIsProcessing(true);
    try {
      await api.admin.deleteBadge(badgeToDelete.id);
      setShowDeleteModal(false);
      setBadgeToDelete(null);
      loadBadges();
    } catch (error) {
      alert('Error: ' + error.message);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Badges Management</h2>

      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <p className="text-red-800">{error}</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Badge</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rarity</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Requirement</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Points</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Users Earned</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {badges.map(badge => (
                <tr key={badge.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="flex items-center">
                      <span className="text-2xl mr-2">{badge.icon}</span>
                      <div>
                        <div className="text-sm font-medium text-gray-900">{badge.name}</div>
                        <div className="text-sm text-gray-500 truncate max-w-xs">{badge.description}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500 capitalize">{badge.category}</td>
                  <td className="px-6 py-4 text-sm">
                    <span className={`px-2 py-1 rounded text-xs capitalize ${
                      badge.rarity === 'legendary' ? 'bg-yellow-100 text-yellow-800' :
                      badge.rarity === 'epic' ? 'bg-purple-100 text-purple-800' :
                      badge.rarity === 'rare' ? 'bg-blue-100 text-blue-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {badge.rarity}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {badge.requirement_type}: {badge.requirement_value}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">{badge.points}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded text-xs ${
                      badge.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {badge.is_active ? 'Active' : 'Inactive'}
                    </span>
                    {badge.is_hidden && (
                      <span className="ml-2 px-2 py-1 rounded text-xs bg-purple-100 text-purple-800">
                        Hidden
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">{badge.users_earned}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-3">
                      <button 
                        onClick={() => handleEdit(badge)} 
                        className="text-blue-600 hover:text-blue-900 inline-flex items-center gap-1"
                      >
                        <span>Edit</span>
                      </button>
                      <button 
                        onClick={() => handleDeleteClick(badge)} 
                        className="text-red-600 hover:text-red-900 inline-flex items-center gap-1"
                      >
                        <span>Delete</span>
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Edit Modal */}
      {showEditModal && editingBadge && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <h3 className="text-xl font-bold mb-4">Edit Badge</h3>
            <form onSubmit={handleSaveEdit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Name *</label>
                  <input
                    type="text"
                    value={editingBadge.name}
                    onChange={(e) => setEditingBadge({...editingBadge, name: e.target.value})}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Icon</label>
                  <input
                    type="text"
                    value={editingBadge.icon}
                    onChange={(e) => setEditingBadge({...editingBadge, icon: e.target.value})}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="🏆"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description *</label>
                <textarea
                  value={editingBadge.description}
                  onChange={(e) => setEditingBadge({...editingBadge, description: e.target.value})}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  rows="2"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Category *</label>
                  <select
                    value={editingBadge.category}
                    onChange={(e) => setEditingBadge({...editingBadge, category: e.target.value})}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    required
                  >
                    {categoryOptions.map(opt => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Rarity *</label>
                  <select
                    value={editingBadge.rarity}
                    onChange={(e) => setEditingBadge({...editingBadge, rarity: e.target.value})}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    required
                  >
                    {rarityOptions.map(opt => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Points *</label>
                  <input
                    type="number"
                    value={editingBadge.points}
                    onChange={(e) => setEditingBadge({...editingBadge, points: parseInt(e.target.value)})}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    required
                    min="0"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Requirement Value *</label>
                  <input
                    type="number"
                    value={editingBadge.requirement_value}
                    onChange={(e) => setEditingBadge({...editingBadge, requirement_value: parseInt(e.target.value)})}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    required
                    min="0"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Requirement Type *</label>
                <input
                  type="text"
                  value={editingBadge.requirement_type}
                  onChange={(e) => setEditingBadge({...editingBadge, requirement_type: e.target.value})}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., review_count, books_read"
                  required
                />
              </div>

              <div className="flex items-center space-x-6">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={editingBadge.is_active}
                    onChange={(e) => setEditingBadge({...editingBadge, is_active: e.target.checked})}
                    className="mr-2 w-4 h-4"
                  />
                  <span className="text-sm font-medium text-gray-700">Active</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={editingBadge.is_hidden}
                    onChange={(e) => setEditingBadge({...editingBadge, is_hidden: e.target.checked})}
                    className="mr-2 w-4 h-4"
                  />
                  <span className="text-sm font-medium text-gray-700">Hidden</span>
                </label>
              </div>

              <div className="flex justify-end gap-4 mt-6">
                <button 
                  type="button" 
                  onClick={() => {
                    setShowEditModal(false);
                    setEditingBadge(null);
                  }} 
                  disabled={isProcessing}
                  className="px-6 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 disabled:bg-gray-300"
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  disabled={isProcessing}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-blue-300"
                >
                  {isProcessing ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      <ConfirmModal
        isOpen={showDeleteModal}
        onClose={() => {
          setShowDeleteModal(false);
          setBadgeToDelete(null);
        }}
        onConfirm={handleDeleteConfirm}
        title="Delete Badge"
        message={`Are you sure you want to delete "${badgeToDelete?.name}"? This action cannot be undone.`}
        confirmText="Delete"
        confirmColor="red"
        isProcessing={isProcessing}
      />
    </div>
  );
};

// =============================================================================
// CATEGORIES MANAGEMENT COMPONENT
// =============================================================================

const CategoriesManagement = () => {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editingCategory, setEditingCategory] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newCategory, setNewCategory] = useState({ name: '' });

  useEffect(() => {
    loadCategories();
  }, []);

  const loadCategories = async () => {
    try {
      setLoading(true);
      const data = await api.admin.getCategories();
      setCategories(data.categories || []);
    } catch (error) {
      setError(api.handleError(error, 'Failed to load categories'));
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await api.admin.createCategory(newCategory);
      alert('Category created successfully');
      setShowCreateModal(false);
      setNewCategory({ name: '' });
      loadCategories();
    } catch (error) {
      alert('Error: ' + error.message);
    }
  };

  const handleEdit = (category) => {
    setEditingCategory(category);
    setShowEditModal(true);
  };

  const handleSaveEdit = async (e) => {
    e.preventDefault();
    try {
      await api.admin.updateCategory(editingCategory.id, { name: editingCategory.name });
      alert('Category updated successfully');
      setShowEditModal(false);
      setEditingCategory(null);
      loadCategories();
    } catch (error) {
      alert('Error: ' + error.message);
    }
  };

  const handleDelete = async (categoryId) => {
    if (!window.confirm('Are you sure? This will fail if the category has books.')) return;
    try {
      await api.admin.deleteCategory(categoryId);
      alert('Category deleted successfully');
      loadCategories();
    } catch (error) {
      alert('Error: ' + error.message);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Categories Management</h2>
        <button
          onClick={() => setShowCreateModal(true)}
          className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
        >
          + Add Category
        </button>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <p className="text-red-800">{error}</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Books</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {categories.map(category => (
                <tr key={category.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">{category.name}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">{category.book_count}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-3">
                    <button onClick={() => handleEdit(category)} className="text-blue-600 hover:text-blue-900">
                      Edit
                    </button>
                    <button onClick={() => handleDelete(category.id)} className="text-red-600 hover:text-red-900">
                      Delete
                    </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-bold mb-4">Create New Category</h3>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name *</label>
                <input
                  type="text"
                  value={newCategory.name}
                  onChange={(e) => setNewCategory({name: e.target.value})}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div className="flex justify-end gap-4">
                <button type="button" onClick={() => setShowCreateModal(false)} className="px-6 py-2 bg-gray-500 text-white rounded-lg">Cancel</button>
                <button type="submit" className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700">Create</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {showEditModal && editingCategory && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-bold mb-4">Edit Category</h3>
            <form onSubmit={handleSaveEdit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name *</label>
                <input
                  type="text"
                  value={editingCategory.name}
                  onChange={(e) => setEditingCategory({...editingCategory, name: e.target.value})}
                  className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div className="flex justify-end gap-4">
                <button type="button" onClick={() => setShowEditModal(false)} className="px-6 py-2 bg-gray-500 text-white rounded-lg">Cancel</button>
                <button type="submit" className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">Save</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;