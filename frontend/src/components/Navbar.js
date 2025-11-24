import React, { useState, useEffect, useRef } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../services/AuthContext";

const Navbar = () => {
  const navigate = useNavigate();
  const { isAuthenticated, user, logout } = useAuth();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Ref for drop down menu
  const dropdownRef = useRef(null);

  const handleLogout = async () => {
    await logout();
    setShowUserMenu(false);
    navigate('/');
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/catalog?search=${encodeURIComponent(searchQuery)}`);
    }
  };

  // Zamknij dropdown po kliknięciu poza nim
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowUserMenu(false);
      }
    };

    // Dodaj listener tylko gdy dropdown jest otwarty
    if (showUserMenu) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    // Cleanup
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showUserMenu]);

  // Zamknij dropdown po kliknięciu w link
  const handleMenuItemClick = () => {
    setShowUserMenu(false);
  };

  return (
    <nav className="bg-white shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 py-3 flex justify-between items-center">
        <div className="flex items-center space-x-4">
          <Link to="/" className="text-3xl font-bold text-blue-600 tracking-wide">
            📚 WolfRead
          </Link>
          <form onSubmit={handleSearch} className="hidden md:flex">
            <input
              type="text"
              placeholder="Search books..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="px-3 py-1.5 rounded-l-full border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-400 transition duration-200 text-sm shadow-sm w-64"
            />
            <button
              type="submit"
              className="px-4 py-1.5 bg-blue-600 text-white rounded-r-full hover:bg-blue-700 transition duration-200 text-sm"
            >
              🔍
            </button>
          </form>
        </div>

        {/* Auth section */}
        <div className="flex items-center space-x-4">
          {isAuthenticated ? (
            // Logged in user
            <div className="relative" ref={dropdownRef}>
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center space-x-2 text-gray-700 hover:text-blue-600 transition-colors"
              >
                <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm font-medium">
                  {user?.first_name?.charAt(0) || user?.username?.charAt(0) || 'U'}
                </div>
                <span className="hidden md:block font-medium">
                  {user?.first_name || user?.username || 'User'}
                </span>
                <span className="text-xs">▼</span>
              </button>

              {/* Dropdown menu */}
              {showUserMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 border border-gray-200 z-50">
                  <div className="px-4 py-2 text-sm text-gray-700 border-b border-gray-100">
                    <div className="font-medium">{user?.full_name || user?.username}</div>
                    <div className="text-gray-500 text-xs">{user?.email}</div>
                  </div>
                  
                  <Link
                    to="/profile"
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    onClick={handleMenuItemClick}
                  >
                    👤 My Profile
                  </Link>
                  
                  <Link
                    to="/user-favorites"
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    onClick={handleMenuItemClick}
                  >
                    ❤️ Favorites
                  </Link>
                  
                  <Link
                    to="/reviews"
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    onClick={handleMenuItemClick}
                  >
                    ⭐ My Reviews
                  </Link>

                  <Link
                    to="/lists"
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    onClick={handleMenuItemClick}
                  >
                    📚 My Lists
                  </Link>

                  <Link
                    to="/badges"
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    onClick={handleMenuItemClick}
                  >
                    Badges
                  </Link>
                  
                  {user?.is_staff && (
                    <Link
                      to="/admin"
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      onClick={handleMenuItemClick}
                    >
                      🛡️ Admin Panel
                    </Link>
                  )}

                  <div className="border-t border-gray-100 mt-1">
                    <button
                      onClick={handleLogout}
                      className="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-100"
                    >
                      🚪 Log out
                    </button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            // Not logged in user
            <div className="flex items-center space-x-4">
              <Link
                to="/login"
                className="text-sm text-blue-600 hover:text-blue-800 transition font-medium"
              >
                Log in
              </Link>
              <Link
                to="/register"
                className="text-sm text-white bg-blue-600 hover:bg-blue-700 transition px-4 py-2 rounded-full shadow font-medium"
              >
                Register
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* Navigation menu */}
      <div className="bg-blue-50 px-4 py-2 flex justify-center space-x-6 text-sm font-medium text-blue-700">
        {[
          { name: "Home", to: "/" },
          { name: "Catalog", to: "/catalog" },
          { name: "Top 100", to: "/top100" },
          { name: "About", to: "/about" },
          ...(isAuthenticated ? [{ name: "Profile", to: "/profile" }] : [])
        ].map(({ name, to }) => (
          <Link
            key={name}
            to={to}
            className="relative px-2 py-1 group transition-transform duration-200 hover:scale-105"
          >
            {name}
            <span className="absolute left-0 bottom-0 w-0 h-0.5 bg-blue-500 transition-all duration-300 group-hover:w-full"></span>
          </Link>
        ))}
      </div>

      {/* Mobile search */}
      <div className="md:hidden px-4 py-2 border-t border-gray-200">
        <form onSubmit={handleSearch} className="flex">
          <input
            type="text"
            placeholder="Search books..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="flex-1 px-3 py-2 rounded-l-md border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-400 text-sm"
          />
          <button
            type="submit"
            className="px-4 py-2 bg-blue-600 text-white rounded-r-md hover:bg-blue-700 transition text-sm"
          >
            🔍
          </button>
        </form>
      </div>
    </nav>
  );
};

export default Navbar;