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
    </div>
  );
};

export default About;
