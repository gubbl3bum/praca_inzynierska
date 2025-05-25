import BookCard from '../components/BookCard';

const Catalog = () => {
  // Placeholder danych książek – do podmiany na dane z backendu
  const books = [
    {
      title: 'Book 1',
      author: 'Author A',
      description: 'Short summary of the book.',
      rating: '4.5',
      category: 'Fiction',
    },
    {
      title: 'Book 2',
      author: 'Author B',
      description: 'A thrilling story about life and mystery.',
      rating: '4.0',
      category: 'Mystery',
    },
    {
      title: 'Book 3',
      author: 'Author C',
      description: 'An inspiring tale of hope and perseverance.',
      rating: '4.7',
      category: 'Drama',
    },

  ];

  return (
    <div className="flex flex-col lg:flex-row px-4 py-12 gap-6 max-w-7xl mx-auto">
      <aside className="lg:w-1/4 w-full bg-white p-6 rounded-2xl shadow-md sticky top-6 self-start">
        <h2 className="text-2xl font-bold mb-6 text-blue-700">Filters</h2>

        {[
          { label: 'Average Rating', placeholder: null, type: 'select', options: ['Any', '4★ and up', '3★ and up', '2★ and up'] },
          { label: 'Categories', placeholder: 'e.g. Fantasy' },
          { label: 'Authors', placeholder: 'e.g. Tolkien' },
          { label: 'Keywords', placeholder: 'e.g. adventure' },
          { label: 'Release Year', placeholder: 'e.g. 2020', type: 'number' },
        ].map(({ label, placeholder, type = 'text', options }, i) => (
          <div key={i} className="mb-4">
            <label className="block font-medium mb-1 text-gray-700">{label}</label>
            {type === 'select' ? (
              <select className="w-full border rounded-lg p-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition">
                {options.map(opt => <option key={opt}>{opt}</option>)}
              </select>
            ) : (
              <input
                type={type}
                className="w-full border rounded-lg p-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
                placeholder={placeholder}
              />
            )}
          </div>
        ))}

        <button className="bg-blue-600 hover:bg-blue-700 text-white py-2 w-full rounded-lg font-semibold transition">
          Apply Filters
        </button>
      </aside>

      <section className="lg:w-3/4 w-full grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
        {books.map((book, idx) => (
          <BookCard
            key={idx}
            title={book.title}
            author={book.author}
            description={book.description}
            rating={book.rating}
            category={book.category}
          />
        ))}
      </section>
    </div>
  );
};

export default UserProfile;
