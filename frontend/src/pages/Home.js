import React from "react";
import BookCard from '../components/BookCard';

// sample data
const books = [
  { id: 1, title: 'Book 1', author: 'Author 1', cover: null, description: 'Description of book 1', rating: '4.5', category: 'Fiction' },
  { id: 2, title: 'Book 2', author: 'Author 2', cover: null, description: 'Description of book 2', rating: '4.2', category: 'Non-fiction' },
  { id: 3, title: 'Book 3', author: 'Author 3', cover: null, description: 'Description of book 3', rating: '4.7', category: 'Science' },
  { id: 4, title: 'Book 4', author: 'Author 4', cover: null, description: 'Description of book 4', rating: '4.0', category: 'History' },
  { id: 5, title: 'Book 5', author: 'Author 5', cover: null, description: 'Description of book 5', rating: '4.3', category: 'Fantasy' },
  { id: 6, title: 'Book 6', author: 'Author 6', cover: null, description: 'Description of book 6', rating: '4.8', category: 'Adventure' },
  { id: 7, title: 'Book 7', author: 'Author 7', cover: null, description: 'Description of book 7', rating: '4.1', category: 'Mystery' },
  { id: 8, title: 'Book 8', author: 'Author 8', cover: null, description: 'Description of book 8', rating: '4.6', category: 'Thriller' },
];

const Home = () => {
  return (
    <div className="text-center py-16">
      <h1 className="text-4xl font-bold mb-4 text-blue-700">📚 WolfRead</h1>
      <p className="text-gray-600 mb-8 max-w-xl mx-auto">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed euismod eros nec velit.</p>
      <h2 className="text-xl font-semibold mb-4">See what's new</h2>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 max-w-5xl mx-auto">
        {books.map((book) => (
          <BookCard
            key={book.id}
            id={book.id}
            title={book.title}
            author={book.author}
            cover={book.cover}
            description={book.description}
            rating={book.rating}
            category={book.category}
          />
        ))}
      </div>
    </div>
  );
};

export default Home;
