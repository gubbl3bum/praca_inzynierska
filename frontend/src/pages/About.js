import React from 'react';

const About = () => {
  return (
    <div className="px-4 py-8 max-w-7xl mx-auto text-center">
      <div className="flex justify-center mb-8">
        <img
          src="https://via.placeholder.com/150" //TODO: Replace with actual mascot image URL
          alt="Mascot"
          className="rounded-full w-32 h-32 object-cover"
        />
      </div>

      <h1 className="text-3xl font-bold mb-4">About WolfRead</h1>
      <p className="text-lg text-gray-700 max-w-3xl mx-auto mb-8">
        Welcome to WolfRead! This is a platform where book enthusiasts can discover, review, and organize their favorite books.
        Our mission is to provide a space for readers to find great books and share their experiences with the community.
      </p>

      <p className="text-lg text-gray-700 max-w-3xl mx-auto">
        Whether you're into fiction, non-fiction, fantasy, mystery, or any other genre, we've got you covered. Explore the
        best-reviewed books, track your reading progress, and discover new favorites. Join us in celebrating the world of books!
      </p>

      <div className="mt-12">
        <h2 className="text-2xl font-semibold mb-4">Technical Overview</h2>
        <p className="text-lg text-gray-700 max-w-3xl mx-auto">
          {/* WolfRead is powered by a React-based frontend and a Django backend. The backend leverages Django REST Framework to 
          expose API endpoints for seamless communication with the frontend. PostgreSQL is used as the primary database, 
          ensuring data integrity and scalability. The application is containerized using Docker, enabling easy deployment 
          and consistent environments across development and production. */}
          Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard
           dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen
            book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially 
            unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and 
            more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.
        </p>
      </div>
    </div>
  );
};

export default About;
