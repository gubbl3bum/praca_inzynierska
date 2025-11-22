import React, { useState, useEffect } from 'react';
import { useAuth } from '../services/AuthContext';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

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
        <div className="flex space-x-4 border-b border-gray-200">
          {['dashboard', 'users', 'system'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 font-medium capitalize ${
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

  const sortOptions = [
    { value: '-date_joined', label: 'Newest First' },
    { value: 'date_joined', label: 'Oldest First' },
    { value: 'username', label: 'Username A-Z' },
    { value: '-username', label: 'Username Z-A' },
    { value: '-review_count', label: 'Most Reviews' },
    { value: 'review_count', label: 'Least Reviews' }
  ];

  // Debounce filters
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedFilters(filters);
    }, 500);

    return () => clearTimeout(timer);
  }, [filters]);

  // Load users when debounced filters change
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

      // Remove empty filters
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

  const toggleUserStatus = async (userId) => {
    if (!window.confirm('Are you sure you want to change this user\'s status?')) {
      return;
    }

    try {
      await api.admin.toggleUserStatus(userId);
      loadUsers(pagination.currentPage);
    } catch (error) {
      alert('Error: ' + (error.message || 'Failed to update user status'));
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

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4 text-gray-800">Search & Filter Users</h2>
        
        {/* Search */}
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

        {/* Other filters */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Has Reviews */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Review Status
            </label>
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

          {/* Is Active */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Account Status
            </label>
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

          {/* Sort */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Sort By
            </label>
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

          {/* Reset */}
          <div className="flex items-end">
            <button
              onClick={resetFilters}
              className="w-full px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 transition-colors"
            >
              🔄 Reset Filters
            </button>
          </div>
        </div>

        {/* Active filters display */}
        {(filters.search || filters.has_reviews || filters.is_active) && (
          <div className="mt-4 flex flex-wrap gap-2">
            <span className="text-sm text-gray-500">Active filters:</span>
            {filters.search && (
              <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
                Search: "{filters.search}"
              </span>
            )}
            {filters.has_reviews && (
              <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-sm">
                {filters.has_reviews === 'true' ? 'Has Reviews' : 'No Reviews'}
              </span>
            )}
            {filters.is_active && (
              <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded text-sm">
                {filters.is_active === 'true' ? 'Active' : 'Inactive'}
              </span>
            )}
          </div>
        )}
      </div>

      {/* Loading */}
      {loading && (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading users...</p>
        </div>
      )}

      {/* Error */}
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

      {/* Results */}
      {!loading && !error && (
        <>
          {/* Results info */}
          <div className="flex justify-between items-center">
            <p className="text-gray-600">
              {users.length > 0 ? (
                <>
                  Showing {((pagination.currentPage - 1) * pagination.pageSize) + 1}-{Math.min(pagination.currentPage * pagination.pageSize, pagination.totalItems)} of {pagination.totalItems.toLocaleString()} users
                  {pagination.totalPages > 1 && (
                    <> (page {pagination.currentPage} of {pagination.totalPages})</>
                  )}
                </>
              ) : (
                'No users found'
              )}
            </p>
          </div>

          {/* User table */}
          {users.length > 0 ? (
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        User
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Email
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Reviews
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Joined
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
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
                                  <span className="ml-2 px-2 py-0.5 text-xs bg-purple-100 text-purple-800 rounded">
                                    Admin
                                  </span>
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
                              <span className="text-gray-500 ml-2">
                                (avg: {user.avg_rating})
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(user.date_joined).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            user.is_active 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {user.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <button
                            onClick={() => toggleUserStatus(user.id)}
                            className="text-blue-600 hover:text-blue-900"
                            disabled={loading}
                          >
                            {user.is_active ? 'Deactivate' : 'Activate'}
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow p-12 text-center">
              <div className="text-6xl mb-4">👥</div>
              <h3 className="text-xl font-semibold text-gray-700 mb-2">
                No Users Found
              </h3>
              <p className="text-gray-500 mb-4">
                {filters.search || filters.has_reviews || filters.is_active
                  ? 'Try adjusting your filters or search terms'
                  : 'No users are available'
                }
              </p>
              <button
                onClick={resetFilters}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg"
              >
                Clear All Filters
              </button>
            </div>
          )}

          {/* Pagination */}
          {pagination.totalPages > 1 && (
            <div className="flex justify-center items-center gap-2 py-6">
              {/* Previous */}
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

              {/* First page */}
              {pagination.currentPage > 3 && (
                <>
                  <button
                    onClick={() => handlePageChange(1)}
                    className="px-4 py-2 rounded-lg bg-white text-gray-700 hover:bg-gray-100 border border-gray-300"
                  >
                    1
                  </button>
                  {pagination.currentPage > 4 && (
                    <span className="px-2 text-gray-500">...</span>
                  )}
                </>
              )}

              {/* Page numbers */}
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

              {/* Last page */}
              {pagination.currentPage < pagination.totalPages - 2 && (
                <>
                  {pagination.currentPage < pagination.totalPages - 3 && (
                    <span className="px-2 text-gray-500">...</span>
                  )}
                  <button
                    onClick={() => handlePageChange(pagination.totalPages)}
                    className="px-4 py-2 rounded-lg bg-white text-gray-700 hover:bg-gray-100 border border-gray-300"
                  >
                    {pagination.totalPages}
                  </button>
                </>
              )}

              {/* Next */}
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
    </div>
  );
};

export default AdminDashboard;