import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from "../../services/AuthContext";

const ProtectedRoute = ({ children, requireAuth = true, redirectTo = '/login' }) => {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  // Show loading while checking authorization
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Checking authorization...</p>
        </div>
      </div>
    );
  }

  // Redirect logic
  if (requireAuth && !isAuthenticated) {
    // Not logged in, but the page requires authorization -> redirect to login
    return <Navigate to={redirectTo} state={{ from: location }} replace />;
  }

  if (!requireAuth && isAuthenticated) {
    // Logged in, but the page is for non-logged in users only -> redirect to home
    return <Navigate to="/" replace />;
  }

  // Everything OK - render component
  return children;
};

export default ProtectedRoute;