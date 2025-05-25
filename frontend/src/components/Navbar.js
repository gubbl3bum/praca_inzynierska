import React from "react";
import { Link } from "react-router-dom";

const Navbar = () => {
  return (
    <nav className="bg-white shadow-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 py-3 flex justify-between items-center">
        <div className="flex items-center space-x-4">
          <span className="text-3xl font-bold text-blue-600 tracking-wide">📚 WolfRead</span>
          <input
            type="text"
            placeholder="Search books..."
            className="px-3 py-1.5 rounded-full border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-400 transition duration-200 text-sm shadow-sm"
          />
        </div>
        <div className="space-x-4">
          <Link
            to="/login"
            className="text-sm text-blue-600 hover:text-blue-800 transition"
          >
            Login
          </Link>
          <Link
            to="/register"
            className="text-sm text-white bg-blue-600 hover:bg-blue-700 transition px-3 py-1 rounded-full shadow"
          >
            Register
          </Link>
        </div>
      </div>
      <div className="bg-blue-50 px-4 py-2 flex justify-center space-x-6 text-sm font-medium text-blue-700">
        {[
          { name: "Home", to: "/" },
          { name: "Catalog", to: "/catalog" },
          { name: "Top 100", to: "/top100" },
          { name: "About", to: "/about" },
          { name: "Profile", to: "/profile" },
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

    </nav>
  );
};