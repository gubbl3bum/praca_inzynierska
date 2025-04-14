import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import BookCard from '../components/BookCard'; 

const UserReviews = () => {
  const [reviews, setReviews] = useState([
    { id: 1, bookTitle: 'The Great Gatsby', author: 'F. Scott Fitzgerald', review: 'Excellent book!', rating: 5, coverImage: null },
    { id: 2, bookTitle: '1984', author: 'George Orwell', review: 'Thought-provoking.', rating: 4, coverImage: null },
    { id: 3, bookTitle: 'Moby Dick', author: 'Herman Melville', review: 'A bit long, but great storytelling.', rating: 3, coverImage: null },
    { id: 4, bookTitle: 'To Kill a Mockingbird', author: 'Harper Lee', review: 'A masterpiece.', rating: 5, coverImage: null },
    { id: 5, bookTitle: 'The Catcher in the Rye', author: 'J.D. Salinger', review: 'A little overrated.', rating: 2, coverImage: null },
  ]);

  const [sortBy, setSortBy] = useState('rating'); // by default sorting by rating

  const sortedReviews = [...reviews].sort((a, b) => {
    if (sortBy === 'rating') {
      return b.rating - a.rating; // sort by rating
    }
    return a.bookTitle.localeCompare(b.bookTitle); // sort by name
  });

  return (
    <div className="px-4 py-8 max-w-7xl mx-auto">
      <h1 className="text-2xl font-bold mb-4 text-center">User's Reviews</h1>

      <div className="mb-6 text-center">
        <label htmlFor="sort-by" className="mr-2">Sort by: </label>
        <select
          id="sort-by"
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="px-4 py-2 border rounded"
        >
          <option value="rating">Rating</option>
          <option value="title">Title</option>
        </select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {sortedReviews.map((review) => (
          <BookCard key={review.id} title={review.bookTitle} author={review.author} cover={review.coverImage}>
            <p className="text-sm text-gray-600">{review.review}</p>
            <div className="mt-2 text-yellow-500">
              {'★'.repeat(review.rating)}
            </div>
          </BookCard>
        ))}
      </div>
    </div>
  );
};

export default UserReviews;
