import React from 'react';
import { useNavigate } from 'react-router-dom';
import { FaStar, FaStarHalfAlt, FaRegStar } from 'react-icons/fa';

function BookCard({ id, title, author, cover, description, rating, category }) {
  const navigate = useNavigate();

  const handleClick = () => {
    // Navigate to the book details page with state
    navigate(`/book/${id}`, {
      state: { title, author, cover, description, rating, category }
    });
  };

  const renderStars = (rating) => {
    const stars = [];
    const r = parseFloat(rating);
    for (let i = 1; i <= 5; i++) {
      if (i <= Math.floor(r)) {
        stars.push(<FaStar key={i} className="text-yellow-400 inline" />);
      } else if (i - 0.5 <= r) {
        stars.push(<FaStarHalfAlt key={i} className="text-yellow-400 inline" />);
      } else {
        stars.push(<FaRegStar key={i} className="text-yellow-400 inline" />);
      }
    }
    return stars;
  };

  return (
    <div
      className="bg-white rounded-2xl shadow-md hover:shadow-xl transform hover:-translate-y-1 transition-all duration-300 p-4 cursor-pointer group"
      onClick={handleClick}
    >
      <div className="bg-gray-100 h-40 mb-4 flex items-center justify-center rounded overflow-hidden">
        {cover ? (
          <img
            src={cover}
            alt={title}
            className="w-full h-full object-cover rounded transition-transform duration-300 group-hover:scale-105"
          />
        ) : (
          <span className="text-gray-400 text-sm">No cover</span>
        )}
      </div>
      <h3 className="text-lg font-semibold text-gray-800 group-hover:text-blue-600 transition-colors duration-300">
        {title}
      </h3>
      <p className="text-sm text-gray-500">{author}</p>
      <div className="flex gap-1 mt-1">{renderStars(rating)}</div>
      <p className="text-xs text-gray-600 mt-2 line-clamp-2">{description}</p>
      <span className="inline-block mt-2 px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded-full">
        {category}
      </span>
    </div>
  );
}