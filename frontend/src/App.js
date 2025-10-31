import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./services/AuthContext";
import Navbar from "./components/Navbar";
import ProtectedRoute from "./components/auth/ProtectedRoute";

// Pages
import Home from "./pages/Home";
import Catalog from "./pages/Catalog";
import Top100 from "./pages/Top100";
import About from "./pages/About";
import UserProfile from "./pages/UserProfile";
import BookDetails from "./pages/BookDetails";
import UserFavourites from "./pages/UserFavourites";
import UserReviews from "./pages/UserReviews";
import UserLists from "./pages/UserLists";
import Badges from './pages/Badges';

// Auth pages
import LoginForm from "./components/auth/LoginForm";
import RegisterForm from "./components/auth/RegisterForm";

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Navbar />
          <Routes>
            {/* Public route - accessible to all */}
            <Route path="/" element={<Home />} />
            <Route path="/catalog" element={<Catalog />} />
            <Route path="/top100" element={<Top100 />} />
            <Route path="/about" element={<About />} />
            <Route path="/book/:id" element={<BookDetails />} />

            {/* Authorization routes - only for non-logged in users */}
            <Route 
              path="/login" 
              element={
                <ProtectedRoute requireAuth={false}>
                  <LoginForm />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/register" 
              element={
                <ProtectedRoute requireAuth={false}>
                  <RegisterForm />
                </ProtectedRoute>
              } 
            />

            {/* Protected routes - only for logged in users */}
            <Route 
              path="/profile" 
              element={
                <ProtectedRoute requireAuth={true}>
                  <UserProfile />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/user-favorites" 
              element={
                <ProtectedRoute requireAuth={true}>
                  <UserFavourites />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/reviews" 
              element={
                <ProtectedRoute requireAuth={true}>
                  <UserReviews />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/lists" 
              element={
                <ProtectedRoute requireAuth={true}>
                  <UserLists />
                </ProtectedRoute>
              } 
            />

            {/* 404 - page not found */}
            <Route 
              path="*" 
              element={
                <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                  <div className="text-center">
                    <h1 className="text-6xl font-bold text-gray-400 mb-4">404</h1>
                    <p className="text-xl text-gray-600 mb-4">Page not found</p>
                    <a 
                      href="/" 
                      className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition-colors"
                    >
                      Return to the home page
                    </a>
                  </div>
                </div>
              } 
            />

            <Route 
              path="/badges" 
              element={
                <ProtectedRoute requireAuth={true}>
                  <Badges />
                </ProtectedRoute>
              } 
            />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;