import React from 'react';
import { useNavigate } from 'react-router-dom';

function BookCard({ id, title, author, cover, description, rating, category }) {
  const navigate = useNavigate();

  const handleClick = () => {
    // navigate to book details
    navigate(`/book/${id}`, {
      state: { title, author, cover, description, rating, category }
    });
  };

  return (
    <div className="bg-white rounded-lg shadow p-4 cursor-pointer" onClick={handleClick}>
      <div className="bg-gray-200 h-40 mb-4">
        {cover && <img src={cover} alt={title} className="w-full h-full object-cover rounded" />}
      </div>
      <h3 className="text-lg font-medium">{title}</h3>
      <p className="text-sm text-gray-500">{author}</p>
    </div>
  );
}

export default BookCard;
