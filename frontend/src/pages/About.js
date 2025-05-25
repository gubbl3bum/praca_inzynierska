import React from 'react';

const About = () => {
  return (
    <div className="px-4 py-12 max-w-4xl mx-auto bg-white rounded-2xl shadow-lg text-center">
      <div className="flex justify-center mb-6">
        <img
          src="https://via.placeholder.com/150" //TODO: Replace with actual mascot image URL
          alt="Mascot"
          className="rounded-full w-32 h-32 object-cover shadow-md"
        />
      </div>

      <h1 className="text-3xl font-bold text-blue-700 mb-4">About <span className="text-blue-600">WolfRead</span></h1>

      <p className="text-lg text-gray-700 leading-relaxed mb-6">
        Welcome to <strong>WolfRead</strong> — a place for book lovers to discover, review, and organize their favorite reads.
        Our mission is to create a community where readers can connect and share their literary journeys.
      </p>

      <p className="text-lg text-gray-700 leading-relaxed">
        No matter if you're into fiction, non-fiction, fantasy, mystery, or sci-fi — we've got you covered.
        Explore top-rated books, track your progress, and find your next favorite!
      </p>
      
    

    </div>
  );
};

export default About;
