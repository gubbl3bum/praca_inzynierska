import React, { useState, useEffect } from 'react';
import { useAuth } from '../services/AuthContext';
import { useNavigate } from 'react-router-dom';
import Badge from '../components/gamification/Badge';
import api from '../services/api';

const Badges = () => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  
  const [allBadges, setAllBadges] = useState({});
  const [userBadges, setUserBadges] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedRarity, setSelectedRarity] = useState('all');
  const [showOnlyEarned, setShowOnlyEarned] = useState(false); // Nowy filtr

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    fetchBadgesData();
  }, [isAuthenticated]);

  const fetchBadgesData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('wolfread_tokens');
      const tokens = token ? JSON.parse(token) : null;
      
      if (!tokens?.access) return;

      // Fetch all badges grouped by category
      const badgesResponse = await api.gamification.getBadges({
        group_by_category: true
      });
      
      // Fetch user's badge progress
      const userBadgesResponse = await api.gamification.getUserBadges(tokens.access);
      
      // Fetch user statistics
      const statsResponse = await api.gamification.getStatistics(tokens.access);
      
      if (badgesResponse.status === 'success') {
        setAllBadges(badgesResponse.categories || {});
      }
      
      if (userBadgesResponse.status === 'success') {
        setUserBadges(userBadgesResponse.badges || []);
      }
      
      if (statsResponse.status === 'success') {
        setStatistics(statsResponse.statistics);
      }
      
    } catch (error) {
      console.error('Error fetching badges:', error);
    } finally {
      setLoading(false);
    }
  };

  const getUserBadgeProgress = (badgeId) => {
    const userBadge = userBadges.find(ub => ub.badge.id === badgeId);
    return userBadge || null;
  };

  const toggleShowcase = async (badgeId) => {
    try {
      const token = localStorage.getItem('wolfread_tokens');
      const tokens = token ? JSON.parse(token) : null;
      
      if (!tokens?.access) return;

      await api.gamification.toggleShowcase(badgeId, tokens.access);
      await fetchBadgesData(); // Refresh
    } catch (error) {
      console.error('Error toggling showcase:', error);
    }
  };

  // Calculate stats
  const earnedCount = userBadges.filter(ub => ub.completed).length;
  const totalBadges = Object.values(allBadges).reduce(
    (sum, category) => sum + category.badges.length, 
    0
  );
  const completionPercentage = totalBadges > 0 ? (earnedCount / totalBadges) * 100 : 0;

  const categories = Object.keys(allBadges);
  const filteredCategories = selectedCategory === 'all' 
    ? categories 
    : [selectedCategory];

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading badges...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            🏆 Badges & Achievements
          </h1>
          <p className="text-gray-600">
            Collect badges by completing challenges
          </p>
        </div>

        {/* Statistics Card */}
        {statistics && (
          <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg p-6 mb-8 text-white shadow-lg">
            <h2 className="text-2xl font-bold mb-4">Your Progress</h2>
            
            {/* Progress Bar */}
            <div className="mb-6">
              <div className="flex justify-between text-sm mb-2">
                <span>Collection Progress</span>
                <span>{earnedCount} / {totalBadges} badges</span>
              </div>
              <div className="w-full bg-white/30 rounded-full h-4 overflow-hidden">
                <div 
                  className="h-full bg-white rounded-full transition-all duration-500 flex items-center justify-end pr-2"
                  style={{ width: `${completionPercentage}%` }}
                >
                  <span className="text-xs font-bold text-purple-600">
                    {completionPercentage.toFixed(0)}%
                  </span>
                </div>
              </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center bg-white/10 rounded-lg p-3">
                <div className="text-3xl font-bold">{earnedCount}</div>
                <div className="text-sm opacity-90">Badges Earned</div>
              </div>
              <div className="text-center bg-white/10 rounded-lg p-3">
                <div className="text-3xl font-bold">{statistics.total_points}</div>
                <div className="text-sm opacity-90">Total Points</div>
              </div>
              <div className="text-center bg-white/10 rounded-lg p-3">
                <div className="text-3xl font-bold">{statistics.total_reviews}</div>
                <div className="text-sm opacity-90">Reviews Written</div>
              </div>
              <div className="text-center bg-white/10 rounded-lg p-3">
                <div className="text-3xl font-bold">{statistics.books_read}</div>
                <div className="text-sm opacity-90">Books Read</div>
              </div>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-md p-4 mb-6">
          <div className="flex flex-wrap gap-4 items-center">
            {/* Category Filter */}
            <div className="flex items-center gap-2">
              <label className="font-medium text-gray-700">Category:</label>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">All Categories</option>
                {categories.map(cat => (
                  <option key={cat} value={cat}>
                    {allBadges[cat].name}
                  </option>
                ))}
              </select>
            </div>

            {/* Rarity Filter */}
            <div className="flex items-center gap-2">
              <label className="font-medium text-gray-700">Rarity:</label>
              <select
                value={selectedRarity}
                onChange={(e) => setSelectedRarity(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">All Rarities</option>
                <option value="common">Common</option>
                <option value="rare">Rare</option>
                <option value="epic">Epic</option>
                <option value="legendary">Legendary</option>
              </select>
            </div>

            {/* Show Only Earned Toggle */}
            <div className="flex items-center gap-2 ml-auto">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={showOnlyEarned}
                  onChange={(e) => setShowOnlyEarned(e.target.checked)}
                  className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                />
                <span className="font-medium text-gray-700">Show only earned</span>
              </label>
            </div>
          </div>
        </div>

        {/* Badges by Category */}
        {filteredCategories.map(categoryKey => {
          const category = allBadges[categoryKey];
          let categoryBadges = category.badges.filter(badge => 
            selectedRarity === 'all' || badge.rarity === selectedRarity
          );

          // Filter by earned status if toggle is on
          if (showOnlyEarned) {
            categoryBadges = categoryBadges.filter(badge => {
              const userProgress = getUserBadgeProgress(badge.id);
              return userProgress?.completed;
            });
          }

          if (categoryBadges.length === 0) return null;

          // Count earned in this category
          const earnedInCategory = categoryBadges.filter(badge => {
            const userProgress = getUserBadgeProgress(badge.id);
            return userProgress?.completed;
          }).length;

          return (
            <div key={categoryKey} className="mb-12">
              {/* Category Header */}
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
                  <span>{categoryBadges[0]?.icon || '📋'}</span>
                  {category.name}
                  <span className="text-sm font-normal text-gray-500 ml-2">
                    ({earnedInCategory}/{categoryBadges.length})
                  </span>
                </h2>
              </div>
              
              {/* Badges Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-6">
                {categoryBadges.map(badge => {
                  const userProgress = getUserBadgeProgress(badge.id);
                  const isEarned = userProgress?.completed || false;
                  const progress = userProgress?.progress || 0;
                  
                  return (
                    <div 
                      key={badge.id} 
                      className={`
                        bg-white rounded-lg p-4 shadow-md transition-all duration-300
                        ${isEarned ? 'hover:shadow-xl hover:scale-105' : 'opacity-60 hover:opacity-80'}
                      `}
                    >
                      {/* Badge Component */}
                      <Badge
                        badge={badge}
                        earned={isEarned}
                        progress={progress}
                        size="medium"
                        showProgress={!isEarned}
                        showcased={userProgress?.is_showcased || false}
                      />
                      
                      {/* Badge Description */}
                      <div className="mt-3 text-xs text-gray-600 text-center">
                        {badge.description}
                      </div>
                      
                      {/* Bottom Info */}
                      <div className="mt-3 space-y-2">
                        {/* Rarity Badge */}
                        <div className="text-center">
                          <span className={`
                            inline-block px-2 py-1 rounded-full text-xs font-medium
                            ${badge.rarity === 'common' ? 'bg-gray-200 text-gray-700' : ''}
                            ${badge.rarity === 'rare' ? 'bg-blue-200 text-blue-700' : ''}
                            ${badge.rarity === 'epic' ? 'bg-purple-200 text-purple-700' : ''}
                            ${badge.rarity === 'legendary' ? 'bg-yellow-200 text-yellow-700' : ''}
                          `}>
                            {badge.rarity.toUpperCase()}
                          </span>
                        </div>

                        {/* Earned Date */}
                        {isEarned && userProgress?.earned_at && (
                          <div className="text-center">
                            <div className="text-xs text-green-600 font-medium">
                              ✓ Earned
                            </div>
                            <div className="text-xs text-gray-500">
                              {new Date(userProgress.earned_at).toLocaleDateString()}
                            </div>
                          </div>
                        )}

                        {/* Progress Bar for Locked Badges */}
                        {!isEarned && userProgress && (
                          <div className="text-center">
                            <div className="text-xs text-gray-500">
                              {userProgress.progress_percentage?.toFixed(0)}% Complete
                            </div>
                            <div className="text-xs text-gray-400">
                              {userProgress.remaining} more needed
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}

        {/* Empty State */}
        {filteredCategories.every(categoryKey => {
          const category = allBadges[categoryKey];
          let categoryBadges = category.badges.filter(badge => 
            selectedRarity === 'all' || badge.rarity === selectedRarity
          );
          if (showOnlyEarned) {
            categoryBadges = categoryBadges.filter(badge => {
              const userProgress = getUserBadgeProgress(badge.id);
              return userProgress?.completed;
            });
          }
          return categoryBadges.length === 0;
        }) && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🔍</div>
            <h3 className="text-xl font-semibold text-gray-700 mb-2">
              No badges found
            </h3>
            <p className="text-gray-500">
              {showOnlyEarned 
                ? "You haven't earned any badges in this category yet. Keep going!"
                : "Try adjusting your filters"
              }
            </p>
          </div>
        )}

        {/* Legend */}
        <div className="bg-white rounded-lg shadow-md p-6 mt-8">
          <h3 className="font-bold text-gray-800 mb-4 text-lg">Legend</h3>
          
          {/* Rarity Colors */}
          <div className="mb-6">
            <h4 className="text-sm font-semibold text-gray-700 mb-3">Rarity Levels</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div className="flex items-center gap-2">
                <span className="inline-block w-4 h-4 rounded bg-gray-400"></span>
                <div>
                  <span className="font-medium">Common</span>
                  <p className="text-xs text-gray-500">Easy to earn</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="inline-block w-4 h-4 rounded bg-blue-400"></span>
                <div>
                  <span className="font-medium">Rare</span>
                  <p className="text-xs text-gray-500">Requires effort</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="inline-block w-4 h-4 rounded bg-purple-400"></span>
                <div>
                  <span className="font-medium">Epic</span>
                  <p className="text-xs text-gray-500">Challenging</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="inline-block w-4 h-4 rounded bg-yellow-400"></span>
                <div>
                  <span className="font-medium">Legendary</span>
                  <p className="text-xs text-gray-500">Very rare</p>
                </div>
              </div>
            </div>
          </div>

          {/* Tips */}
          <div className="border-t pt-4">
            <h4 className="text-sm font-semibold text-gray-700 mb-2">Tips</h4>
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex items-start gap-2">
                <span>💡</span>
                <span>Click on earned badges to showcase them on your profile!</span>
              </li>
              <li className="flex items-start gap-2">
                <span>🎯</span>
                <span>Hover over locked badges to see your progress</span>
              </li>
              <li className="flex items-start gap-2">
                <span>⭐</span>
                <span>Showcased badges appear with a star in the corner</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Badges;