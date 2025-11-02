import React, { useEffect, useState } from 'react';

const ToastNotification = ({ badge, onClose, duration = 5000 }) => {
  const [isVisible, setIsVisible] = useState(false);
  const [isLeaving, setIsLeaving] = useState(false);

  useEffect(() => {
    setTimeout(() => setIsVisible(true), 10);

    const timer = setTimeout(() => {
      handleClose();
    }, duration);

    return () => clearTimeout(timer);
  }, [duration]);

  const handleClose = () => {
    setIsLeaving(true);
    setTimeout(() => {
      onClose();
    }, 300);
  };

  const getRarityGradient = (rarity) => {
    const gradients = {
      common: 'from-gray-500 to-gray-700',
      rare: 'from-blue-500 to-blue-700',
      epic: 'from-purple-500 to-purple-700',
      legendary: 'from-yellow-500 to-orange-600'
    };
    return gradients[rarity] || gradients.common;
  };

  return (
    <div
      className={`
        w-full max-w-sm
        transition-all duration-300 ease-out
        ${isVisible && !isLeaving ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'}
      `}
    >
      <div className={`
        bg-gradient-to-r ${getRarityGradient(badge.rarity)}
        rounded-xl shadow-2xl
        p-6
        text-white
        relative
        overflow-hidden
        border-2 border-white border-opacity-20
      `}>
        {/* Animated Background Effect */}
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-20 animate-shimmer"></div>
        
        {/* Close Button */}
        <button
          onClick={handleClose}
          className="absolute top-2 right-2 text-white hover:text-gray-200 transition-colors z-20"
        >
          <span className="text-2xl leading-none">×</span>
        </button>

        {/* Content */}
        <div className="relative z-10">
          {/* Header */}
          <div className="flex items-center gap-2 mb-3">
            <span className="text-2xl animate-bounce">🎉</span>
            <h3 className="font-bold text-lg">Badge Unlocked!</h3>
          </div>

          {/* Badge Info */}
          <div className="flex items-center gap-4">
            {/* Badge Icon */}
            <div className="w-16 h-16 bg-white bg-opacity-20 rounded-full flex items-center justify-center text-4xl flex-shrink-0 animate-pulse">
              {badge.icon}
            </div>

            {/* Badge Details */}
            <div className="flex-1">
              <h4 className="font-bold text-xl mb-1">{badge.name}</h4>
              <p className="text-sm text-white text-opacity-90 mb-2">
                {badge.description}
              </p>
              <div className="flex items-center gap-2 text-sm">
                <span className="bg-white bg-opacity-20 px-2 py-1 rounded-full">
                  +{badge.points} points
                </span>
                <span className="capitalize">{badge.rarity}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="absolute bottom-0 left-0 right-0 h-1 bg-white bg-opacity-20">
          <div
            className="h-full bg-white"
            style={{
              animation: `shrink ${duration}ms linear`,
            }}
          ></div>
        </div>
      </div>
    </div>
  );
};

export default ToastNotification;