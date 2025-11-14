import React from 'react';
import PreferenceForm from './PreferenceForm';

const PreferenceModal = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="fixed inset-0 bg-black bg-opacity-50" onClick={onClose}></div>
      
      <div className="relative min-h-screen flex items-center justify-center p-4">
        <div className="relative bg-white rounded-2xl shadow-2xl max-w-5xl w-full max-h-[90vh] overflow-y-auto">
          <button
            onClick={onClose}
            className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 text-2xl z-10"
          >
            ×
          </button>
          
          <PreferenceForm onComplete={onClose} onSkip={onClose} />
        </div>
      </div>
    </div>
  );
};

export default PreferenceModal;