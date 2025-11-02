import { useCallback } from 'react';
import { useNotifications } from '../services/NotificationContext';
import { checkUserBadges } from '../services/badgeCheckService';

export const useBadgeCheck = () => {
  const { showBadgeNotification } = useNotifications();

  const checkBadges = useCallback(async () => {
    try {
      const token = localStorage.getItem('wolfread_tokens');
      const tokens = token ? JSON.parse(token) : null;
      
      if (!tokens?.access) {
        console.log('❌ No auth token - skipping badge check');
        return;
      }

      console.log('🔍 Checking for new badges...');
      
      const result = await checkUserBadges(tokens.access, (badge) => {
        console.log('🎉 New badge earned:', badge.name);
        console.log('📢 Calling showBadgeNotification...'); 
        showBadgeNotification(badge);
      });

      if (result.success && result.count > 0) {
        console.log(`✨ Earned ${result.count} new badge(s)!`);
      } else {
        console.log('ℹ️ No new badges earned');
      }
      
      return result;
    } catch (error) {
      console.error('❌ Error checking badges:', error);
      return { success: false, error: error.message };
    }
  }, [showBadgeNotification]);

  return { checkBadges };
};