import React, { createContext, useContext, useReducer, useEffect } from 'react';
import api from './api';

// Initial state
const initialState = {
  user: null,                    
  isAuthenticated: false,        
  isLoading: true,              
  tokens: {                     
    access: null,
    refresh: null,
    customRefresh: null
  },
  error: null                  
};

// Actions
const AUTH_ACTIONS = {
  SET_LOADING: 'SET_LOADING',
  LOGIN_SUCCESS: 'LOGIN_SUCCESS',
  LOGOUT: 'LOGOUT',
  SET_ERROR: 'SET_ERROR',
  CLEAR_ERROR: 'CLEAR_ERROR',
  UPDATE_USER: 'UPDATE_USER',
  REFRESH_TOKEN: 'REFRESH_TOKEN'
};

// Reducer
function authReducer(state, action) {
  switch (action.type) {
    case AUTH_ACTIONS.SET_LOADING:
      return {
        ...state,
        isLoading: action.payload
      };
    
    case AUTH_ACTIONS.LOGIN_SUCCESS:
      return {
        ...state,
        user: action.payload.user,
        tokens: action.payload.tokens,
        isAuthenticated: true,
        isLoading: false,
        error: null
      };
    
    case AUTH_ACTIONS.LOGOUT:
      return {
        ...initialState,
        isLoading: false
      };
    
    case AUTH_ACTIONS.SET_ERROR:
      return {
        ...state,
        error: action.payload,
        isLoading: false
      };
    
    case AUTH_ACTIONS.CLEAR_ERROR:
      return {
        ...state,
        error: null
      };
    
    case AUTH_ACTIONS.UPDATE_USER:
      return {
        ...state,
        user: { ...state.user, ...action.payload }
      };
    
    case AUTH_ACTIONS.REFRESH_TOKEN:
      return {
        ...state,
        tokens: { ...state.tokens, ...action.payload }
      };
    
    default:
      return state;
  }
}

// Context
const AuthContext = createContext();

// Provider Component
export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Helper functions for Local Storage
  const saveTokensToStorage = (tokens) => {
    localStorage.setItem('wolfread_tokens', JSON.stringify(tokens));
  };

  const getTokensFromStorage = () => {
    try {
      const stored = localStorage.getItem('wolfread_tokens');
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  };

  const clearTokensFromStorage = () => {
    localStorage.removeItem('wolfread_tokens');
  };

  // Check authorization when starting the application
  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: true });
    
    try {
      // Check if tokens are in localStorage
      const storedTokens = getTokensFromStorage();
      
      if (!storedTokens?.access) {
        // No tokens - not logged in
        dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: false });
        return;
      }

      // Check if the token is still valid
      const response = await api.auth.checkStatus(storedTokens.access);
      
      console.log('🔍 Auth check response:', response); 
      console.log('👤 User data:', response.user); 

      if (response.status === 'success' && response.authenticated) {
        // Valid token - log in user
        dispatch({
          type: AUTH_ACTIONS.LOGIN_SUCCESS,
          payload: {
            user: response.user,
            tokens: storedTokens
          }
        });
      } else {
        // Token invalid - try refreshing
        await refreshAccessToken();
      }
    } catch (error) {
      console.error('Error checking auth status:', error);
      
      // Error - Logout User
      clearTokensFromStorage();
      dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: false });
    }
  };

  const refreshAccessToken = async () => {
    try {
      const storedTokens = getTokensFromStorage();
      
      if (!storedTokens?.refresh) {
        throw new Error('No refresh token available');
      }

      const response = await api.auth.refreshToken(storedTokens.refresh);
      
      if (response.access) {
        const newTokens = {
          ...storedTokens,
          access: response.access,
          refresh: response.refresh || storedTokens.refresh
        };
        
        saveTokensToStorage(newTokens);
        dispatch({
          type: AUTH_ACTIONS.REFRESH_TOKEN,
          payload: newTokens
        });
        
        // Check user status with new token
        await checkAuthStatus();
        return true;
      } else {
        throw new Error('Failed to refresh token');
      }
    } catch (error) {
      console.error('Error refreshing token:', error);
      clearTokensFromStorage();
      dispatch({ type: AUTH_ACTIONS.LOGOUT });
      return false;
    }
  };

  // Log in function
  const login = async (email, password) => {
    try {
      dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: true });
      dispatch({ type: AUTH_ACTIONS.CLEAR_ERROR });

      const response = await api.auth.login(email, password);

      if (response.status === 'success') {
        const { user, tokens } = response;
        
        // Save to state
        dispatch({
          type: AUTH_ACTIONS.LOGIN_SUCCESS,
          payload: { user, tokens }
        });
        
        // Save to localStorage
        saveTokensToStorage(tokens);
        
        // CHECK PREFERENCES IMMEDIATELY AFTER LOGIN
        try {
          const prefCheck = await api.preferences.checkProfile(tokens.access);
          console.log('🔍 Preference check result:', prefCheck);
          
          if (prefCheck.status === 'success' && prefCheck.should_show_form) {
            console.log('✨ Setting flag to show preference form');
            localStorage.setItem('show_preference_form', 'true');
          }
        } catch (err) {
          console.error('Could not check preferences:', err);
        }
        
        return { success: true, user };
      } else {
        throw new Error(response.message || 'Login failed');
      }
    } catch (err) {
      const errorMessage = api.handleError(err, 'Login failed');
      dispatch({ type: AUTH_ACTIONS.SET_ERROR, payload: errorMessage });
      return { success: false, error: errorMessage };
    }
  };

  // Registration function
  const register = async (userData) => {
    dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: true });
    dispatch({ type: AUTH_ACTIONS.CLEAR_ERROR });
    
    try {
      const response = await api.auth.register(userData);
      
      if (response.status === 'success') {
        const { user, tokens } = response;
        
        // Save tokens to localStorage
        saveTokensToStorage(tokens);
        
        // Update status
        dispatch({
          type: AUTH_ACTIONS.LOGIN_SUCCESS,
          payload: { user, tokens }
        });
        
        // ALWAYS SHOW PREFERENCE FORM AFTER REGISTRATION
        console.log('🆕 New user registered - setting preference form flag');
        localStorage.setItem('show_preference_form', 'true');
        
        return { success: true, user };
      } else {
        throw new Error(response.message || 'Registration failed');
      }
    } catch (error) {
      const errorMessage = api.handleError(error, 'Registration error');
      dispatch({ type: AUTH_ACTIONS.SET_ERROR, payload: errorMessage });
      return { success: false, error: errorMessage };
    }
  };

  // Log out function
  const logout = async () => {
    try {
      // Send logout request to backend
      if (state.tokens?.access) {
        await api.auth.logout(state.tokens.access);
      }
    } catch (error) {
      console.error('Error during logout:', error);
      // Continue logging out even on error
    } finally {
      // Clear localStorage and state
      clearTokensFromStorage();
      localStorage.removeItem('show_preference_form'); // ✅ Clear preference flag
      dispatch({ type: AUTH_ACTIONS.LOGOUT });
    }
  };

  // Profile update function
  const updateProfile = async (profileData) => {
    try {
      const response = await api.auth.updateProfile(profileData, state.tokens?.access);
      
      if (response.status === 'success') {
        dispatch({
          type: AUTH_ACTIONS.UPDATE_USER,
          payload: response.user
        });
        return { success: true, user: response.user };
      } else {
        throw new Error(response.message || 'Profile update failed');
      }
    } catch (error) {
      const errorMessage = api.handleError(error, 'Profile update error');
      return { success: false, error: errorMessage };
    }
  };

  // Password change function
  const changePassword = async (currentPassword, newPassword) => {
    try {
      const response = await api.auth.changePassword({
        current_password: currentPassword,
        new_password: newPassword,
        new_password_confirm: newPassword
      }, state.tokens?.access);
      
      if (response.status === 'success') {
        // After changing the password, log the user out (tokens have been invalidated)
        await logout();
        return { success: true, message: response.message };
      } else {
        throw new Error(response.message || 'Password change failed');
      }
    } catch (error) {
      const errorMessage = api.handleError(error, 'Password change error');
      return { success: false, error: errorMessage };
    }
  };

  // Error clearing function
  const clearError = () => {
    dispatch({ type: AUTH_ACTIONS.CLEAR_ERROR });
  };

  // The value of context
  const value = {
    ...state,
    login,
    register,
    logout,
    updateProfile,
    changePassword,
    clearError,
    refreshAccessToken,
    checkAuthStatus
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Hook for using Auth Context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;