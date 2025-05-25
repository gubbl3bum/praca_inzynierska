import React from 'react';
import BookCard from '../components/BookCard'; 

const UserFavorites = () => {
  // Sample data
  const favoriteBooks = [
    { title: '1984', author: 'George Orwell' },
    { title: 'To Kill a Mockingbird', author: 'Harper Lee' },
    { title: 'Pride and Prejudice', author: 'Jane Austen' },
    { title: 'The Great Gatsby', author: 'F. Scott Fitzgerald' },
    { title: 'Moby Dick', author: 'Herman Melville' },
  ];

  return (
    <div className="px-4 py-12 max-w-6xl mx-auto">
    <h1 className="text-3xl font-bold text-center text-blue-700 mb-8">
      ❤️ Your Favourite Books
    </h1>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {favoriteBooks.map((book, idx) => (
          <BookCard
            key={idx}
            title={book.title}
            author={book.author}
          />
        ))}
      </div>
    </div>
  );
};

export default UserFavorites;
