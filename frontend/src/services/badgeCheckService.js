import api from './api';

/**
 * Sprawdza odznaki dla użytkownika
 * @param {string} token - Access token
 * @param {Function} onBadgeEarned - Callback wywoływany dla każdej nowej odznaki
 */
export const checkUserBadges = async (token, onBadgeEarned) => {
  try {
    const response = await api.gamification.checkBadges(token);
    
    if (response.status === 'success' && response.new_badges?.length > 0) {
      // Wywołaj callback dla każdej nowej odznaki z opóźnieniem
      response.new_badges.forEach((badge, index) => {
        setTimeout(() => {
          onBadgeEarned(badge);
        }, index * 1000); // 1 sekunda opóźnienia między kolejnymi powiadomieniami
      });
      
      return {
        success: true,
        badges: response.new_badges,
        count: response.new_badges.length
      };
    }
    
    return {
      success: true,
      badges: [],
      count: 0
    };
  } catch (error) {
    console.error('Error checking badges:', error);
    return {
      success: false,
      error: error.message
    };
  }
};