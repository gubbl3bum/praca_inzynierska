import React from "react";
import { Link } from "react-router-dom";

const Navbar = () => {
  return (
    <nav className="bg-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 py-3 flex justify-between items-center">
        <div className="flex items-center space-x-4">
          <Link to="/" className="text-2xl font-bold text-blue-600">
            WolfRead
          </Link>
          <input
            type="text"
            placeholder="Search books..."
            className="border rounded px-2 py-1 text-sm"
          />
        </div>
        <div className="space-x-4">
          <Link to="/login" className="text-sm text-blue-500 hover:underline">Login</Link>
          <Link to="/register" className="text-sm text-blue-500 hover:underline">Register</Link>
        </div>
      </div>
      <div className="bg-blue-100 px-4 py-2 flex justify-center space-x-6 text-sm">
        <Link to="/" className="hover:underline">Home</Link>
        <Link to="/catalog" className="hover:underline">Catalog</Link>
        <Link to="/top100" className="hover:underline">Top 100</Link>
        <Link to="/about" className="hover:underline">About</Link>
        <Link to="/profile" className="hover:underline">Profile</Link>
      </div>
    </nav>
  );
};

export default Navbar;