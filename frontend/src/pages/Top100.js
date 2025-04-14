import React from 'react';
import BookCard from '../components/BookCard';

const Top100 = () => {
  return (
    <div className="px-4 py-8 max-w-7xl mx-auto">
      <h1 className="text-2xl font-bold text-center mb-8">
        📚 Here are the Top 100 Books of All Time<br />
        <span className="text-gray-600 text-base font-normal">
          (with highest reviews from our users)
        </span>
      </h1>

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
