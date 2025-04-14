import React from 'react';
import { useLocation } from 'react-router-dom';

const BookDetails = () => {
  // retrieve book details from the location state
  // this is passed from the BookCard component when navigating to this page
  const location = useLocation();
  const { title, author, cover, description, rating, category } = location.state || {};

  if (!title) {
    return <div>Book details not available.</div>;
  }

  return (
    <div className="max-w-4xl mx-auto p-8 bg-white rounded-lg shadow-md">
      <div className="flex flex-col md:flex-row items-center mb-8">
        <div className="w-full md:w-1/3 mb-4 md:mb-0">
          <img src={cover} alt={title} className="w-full h-auto object-cover rounded" />
        </div>
        <div className="w-full md:w-2/3 ml-0 md:ml-8">
          <h2 className="text-3xl font-semibold text-blue-700">{title}</h2>
          <p className="text-xl text-gray-600">{author}</p>
          <p className="text-sm text-gray-500">{category}</p>
          <div className="mt-4">
            <p className="text-gray-700">{description}</p>
          </div>
          <div className="mt-4">
            <span className="font-semibold">Rating:</span> {rating}
          </div>
        </div>
      </div>
    </div>
  );
};

export default BookDetails;
