import React, { createContext, useContext, useState, useCallback } from 'react';
import ToastNotification from '../components/gamification/ToastNotification';

const NotificationContext = createContext();

export const NotificationProvider = ({ children }) => {
  const [notifications, setNotifications] = useState([]);

  const showBadgeNotification = useCallback((badge) => {
    console.log('showBadgeNotification called with:', badge);
    
    const id = Date.now();
    const notification = {
      id,
      badge,
      timestamp: new Date()
    };

    console.log('Adding notification to state:', notification);
    setNotifications(prev => {
      console.log('Current notifications:', prev);
      return [...prev, notification];
    });

    setTimeout(() => {
      removeNotification(id);
    }, 5500); 
  }, []);

  const removeNotification = useCallback((id) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  }, []);

  return (
    <NotificationContext.Provider value={{ showBadgeNotification }}>
      {children}
      
      <div className="fixed bottom-4 right-4 z-[9999] space-y-4 pointer-events-none">
        {notifications.map((notification, index) => (
          <div
            key={notification.id}
            className="pointer-events-auto"
            style={{ 
              marginBottom: index > 0 ? '16px' : '0'
            }}
          >
            <ToastNotification
              badge={notification.badge}
              onClose={() => removeNotification(notification.id)}
            />
          </div>
        ))}
      </div>
    </NotificationContext.Provider>
  );
};

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within NotificationProvider');
  }
  return context;
};