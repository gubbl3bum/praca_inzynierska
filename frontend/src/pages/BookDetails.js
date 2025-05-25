import { useLocation } from 'react-router-dom';

const BookDetails = () => {


  const location = useLocation();
  const { title, author, cover, description, rating, category } = location.state || {};

  if (!title) {
    return <div className="text-center text-gray-500 py-12">Book details not available.</div>;
  }

  return (
    <div className="max-w-4xl mx-auto p-8 bg-white rounded-2xl shadow-lg mt-12">
      <div className="flex flex-col md:flex-row items-start gap-8">
        <div className="w-full md:w-1/3 aspect-[3/4] bg-gray-200 rounded-lg overflow-hidden">
          {cover ? (
            <img src={cover} alt={title} className="w-full h-full object-cover" />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-gray-500 text-sm italic">
              No Cover
            </div>
          )}
        </div>

        <div className="w-full md:w-2/3">
          <h1 className="text-3xl font-bold text-blue-700 mb-2">{title}</h1>
          <p className="text-lg text-gray-600 mb-1">{author}</p>
          <span className="text-sm text-gray-500 mb-4 inline-block">{category}</span>

          <p className="text-gray-700 leading-relaxed mb-4">{description}</p>

          <div className="text-sm bg-blue-100 text-blue-800 px-3 py-1 rounded inline-block font-semibold">
            ⭐ Rating: {rating}
          </div>
        </div>
      </div>
    </div>
  );
};

export default BookDetails;
