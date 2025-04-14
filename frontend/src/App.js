import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import Catalog from "./pages/Catalog";
import Top100 from "./pages/Top100";
import About from "./pages/About";
import UserProfile from "./pages/UserProfile";
import BookDetails from "./pages/BookDetails";
import UserFavourites from "./pages/UserFavourites";
import UserReviews from "./pages/UserReviews";
import Login from "./pages/Login";
import Register from "./pages/Register";

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/catalog" element={<Catalog />} />
          <Route path="/top100" element={<Top100 />} />
          <Route path="/about" element={<About />} />
          <Route path="/profile" element={<UserProfile />} />
          <Route path="/book/:id" element={<BookDetails />} />
          <Route path="/user-favorites" element={<UserFavourites />} />
          <Route path="/reviews" element={<UserReviews />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
