import React from 'react';
import BookCard from '../components/BookCard';

const Top100 = () => {
  return (
    <div className="px-4 py-12 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold text-center text-blue-700 mb-2">
        📚 Top 100 Books of All Time
      </h1>
      <p className="text-center text-gray-600 mb-8">
        Based on highest reviews from our amazing readers!
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {Array.from({ length: 100 }).map((_, idx) => (
          <BookCard
            key={idx}
            title={`Top Book #${idx + 1}`}
            author="Famous Author"
          >
            <div className="mt-2 text-sm text-gray-600">
              <p>Category: Classic</p>
              <p>Rating: ★★★★★</p>
              <p>Readers: {1000 + idx * 10}</p>
            </div>
          </BookCard>
        ))}
      </div>
    </div>
  );
};

export default Top100;
