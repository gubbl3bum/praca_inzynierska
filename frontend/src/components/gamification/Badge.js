import React from 'react';

const Badge = ({ 
  badge, 
  earned = false, 
  progress = null,
  size = 'medium',
  showProgress = true,
  onClick = null,
  showcased = false
}) => {
  const sizeClasses = {
    small: 'w-16 h-16 text-2xl',
    medium: 'w-24 h-24 text-4xl',
    large: 'w-32 h-32 text-5xl'
  };

  const rarityColors = {
    common: 'from-gray-400 to-gray-600',
    rare: 'from-blue-400 to-blue-600',
    epic: 'from-purple-400 to-purple-600',
    legendary: 'from-yellow-400 to-yellow-600'
  };

  const rarityBorders = {
    common: 'border-gray-400',
    rare: 'border-blue-500',
    epic: 'border-purple-500',
    legendary: 'border-yellow-500'
  };

  const rarityGlow = {
    common: 'shadow-gray-400/50',
    rare: 'shadow-blue-500/50',
    epic: 'shadow-purple-500/50',
    legendary: 'shadow-yellow-500/50'
  };

  const progressPercentage = progress !== null 
    ? Math.min(100, (progress / badge.requirement_value) * 100)
    : 0;

  return (
    <div 
      className={`
        relative 
        transition-all duration-300
        ${earned ? 'hover:scale-105' : ''}
      `}
      title={earned ? badge.description : badge.description}
    >
      {/* Badge container */}
      <div className={`
        ${sizeClasses[size]}
        rounded-full
        bg-gradient-to-br ${rarityColors[badge.rarity]}
        border-4 ${rarityBorders[badge.rarity]}
        flex items-center justify-center
        relative
        overflow-hidden
        transition-all duration-300
        ${!earned 
          ? 'opacity-40 grayscale blur-[0.5px] shadow-md' 
          : `shadow-lg ${rarityGlow[badge.rarity]} hover:shadow-2xl`
        }
      `}>
        {/* Badge icon */}
        <span className={`
          relative z-10 
          ${!earned ? 'filter blur-[1px]' : ''}
          transition-all duration-300
        `}>
          {badge.icon}
        </span>
        
        {/* Shine effect for earned badges */}
        {earned && (
          <div className="absolute inset-0 bg-gradient-to-tr from-transparent via-white to-transparent opacity-30 animate-shine"></div>
        )}
        
        {/* Sparkle effect for legendary earned badges */}
        {earned && badge.rarity === 'legendary' && (
          <>
            <div className="absolute top-1 right-1 w-2 h-2 bg-white rounded-full animate-ping"></div>
            <div className="absolute bottom-1 left-1 w-2 h-2 bg-white rounded-full animate-ping" style={{ animationDelay: '0.5s' }}></div>
          </>
        )}
        
        {/* Lock overlay for unearned badges */}
        {!earned && (
          <div className="absolute inset-0 flex items-center justify-center bg-black/50 backdrop-blur-sm">
            <div className="text-center">
              <span className="text-white text-3xl drop-shadow-lg">🔒</span>
              {progress !== null && progress > 0 && (
                <div className="text-white text-xs mt-1 font-bold">
                  {progressPercentage.toFixed(0)}%
                </div>
              )}
            </div>
          </div>
        )}
        
        {/* Showcase star */}
        {showcased && earned && (
          <div className="absolute -top-2 -right-2 animate-bounce">
            <div className="bg-yellow-400 rounded-full p-1 shadow-lg border-2 border-white">
              <span className="text-xs">⭐</span>
            </div>
          </div>
        )}

        {/* New badge indicator */}
        {earned && (
          <div className="absolute -top-1 left-1/2 transform -translate-x-1/2">
            <div className="relative">
              <div className="absolute inset-0 bg-green-400 rounded-full blur-sm animate-pulse"></div>
              <div className="relative bg-green-500 text-white text-[10px] px-2 py-0.5 rounded-full font-bold shadow-lg">
                EARNED
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Progress bar for locked badges */}
      {showProgress && progress !== null && !earned && (
        <div className="mt-3">
          <div className="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden shadow-inner">
            <div 
              className={`
                h-full 
                bg-gradient-to-r ${rarityColors[badge.rarity]} 
                transition-all duration-500 ease-out
                relative
                overflow-hidden
              `}
              style={{ width: `${progressPercentage}%` }}
            >
              {/* Animated shine on progress bar */}
              {progressPercentage > 0 && (
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer"></div>
              )}
            </div>
          </div>
          <div className="flex justify-between text-xs text-gray-600 mt-1 font-medium">
            <span>{progress} / {badge.requirement_value}</span>
            <span>{badge.requirement_value - progress} to go</span>
          </div>
        </div>
      )}

      {/* Badge name and points */}
      <div className="text-center mt-3">
        <div className={`
          font-semibold 
          ${size === 'small' ? 'text-xs' : 'text-sm'} 
          ${earned ? 'text-gray-800' : 'text-gray-500'}
          transition-colors duration-300
        `}>
          {badge.name}
        </div>
        {size !== 'small' && (
          <div className={`
            text-xs 
            ${earned ? 'text-blue-600 font-semibold' : 'text-gray-400'}
            flex items-center justify-center gap-1
          `}>
            <span>{badge.points}</span>
            <span className="text-[10px]">points</span>
          </div>
        )}
      </div>

      {/* Hover tooltip for locked badges */}
      {!earned && (
        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg opacity-0 hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-10 shadow-xl">
          {badge.description}
          <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-1">
            <div className="border-4 border-transparent border-t-gray-900"></div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Badge;
