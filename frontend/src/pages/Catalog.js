import React from 'react';
import BookCard from '../components/BookCard';

const Catalog = () => {
  return (
    <div className="flex flex-col lg:flex-row px-4 py-8 gap-6 max-w-7xl mx-auto">
      <aside className="lg:w-1/4 w-full bg-white p-4 rounded shadow h-fit">
        <h2 className="text-xl font-bold mb-4">Filters</h2>

        <div className="mb-4">
          <label className="block font-medium mb-1">Average Rating</label>
          <select className="w-full border p-2 rounded">
            <option>Any</option>
            <option>4★ and up</option>
            <option>3★ and up</option>
            <option>2★ and up</option>
          </select>
        </div>

        <div className="mb-4">
          <label className="block font-medium mb-1">Categories</label>
          <input type="text" className="w-full border p-2 rounded" placeholder="e.g. Fantasy" />
        </div>

        <div className="mb-4">
          <label className="block font-medium mb-1">Authors</label>
          <input type="text" className="w-full border p-2 rounded" placeholder="e.g. Tolkien" />
        </div>

        <div className="mb-4">
          <label className="block font-medium mb-1">Keywords</label>
          <input type="text" className="w-full border p-2 rounded" placeholder="e.g. adventure" />
        </div>

        <div className="mb-4">
          <label className="block font-medium mb-1">Release Year</label>
          <input type="number" className="w-full border p-2 rounded" placeholder="e.g. 2020" />
        </div>

        <button className="bg-blue-600 text-white w-full py-2 rounded hover:bg-blue-700 transition">
          Apply Filters
        </button>
      </aside>

      <section className="lg:w-3/4 w-full grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
        {Array.from({ length: 9 }).map((_, idx) => (
          <BookCard
            key={idx}
            title={`Book ${idx + 1}`}
            author="Author Name"
          >
            <div className="mt-2 flex flex-col gap-2 text-sm">
              <p>Category: Fiction</p>
              <p>Rating: ★★★★☆</p>
              <p>Readers: {Math.floor(Math.random() * 1000) + 100}</p>
              <div className="flex gap-2 mt-2">
                <button className="text-xs px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600">Add Review</button>
                <button className="text-xs px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600">Like</button>
              </div>
            </div>
          </BookCard>
        ))}
      </section>
    </div>
  );
};

export default Catalog;
