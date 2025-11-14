import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

const PreferenceForm = ({ onComplete, onSkip }) => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  
  // Available options
  const [options, setOptions] = useState({
    categories: [],
    authors: [],
    publishers: []
  });
  
  // User selections
  const [preferences, setPreferences] = useState({
    preferred_categories: {},
    preferred_authors: [],
    preferred_publishers: [],
    min_rating_threshold: 0,
    preferred_year_range: { min: 1900, max: 2024 }
  });
  
  // UI state
  const [step, setStep] = useState(1);
  const totalSteps = 3;

  useEffect(() => {
    fetchOptions();
  }, []);

  const fetchOptions = async () => {
    try {
      setLoading(true);
      const response = await api.preferences.getOptions();
      
      if (response.status === 'success') {
        setOptions(response.options);
      }
    } catch (err) {
      setError('Failed to load preference options');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCategoryToggle = (categoryId, categoryName) => {
    setPreferences(prev => {
      const newCategories = { ...prev.preferred_categories };
      
      if (newCategories[categoryId]) {
        delete newCategories[categoryId];
      } else {
        newCategories[categoryId] = 0.8; // Default weight
      }
      
      return {
        ...prev,
        preferred_categories: newCategories
      };
    });
  };

  const handleCategoryWeight = (categoryId, weight) => {
    setPreferences(prev => ({
      ...prev,
      preferred_categories: {
        ...prev.preferred_categories,
        [categoryId]: parseFloat(weight)
      }
    }));
  };

  const handleAuthorToggle = (authorId) => {
    setPreferences(prev => {
      const newAuthors = prev.preferred_authors.includes(authorId)
        ? prev.preferred_authors.filter(id => id !== authorId)
        : [...prev.preferred_authors, authorId];
      
      return { ...prev, preferred_authors: newAuthors };
    });
  };

  const handlePublisherToggle = (publisherId) => {
    setPreferences(prev => {
      const newPublishers = prev.preferred_publishers.includes(publisherId)
        ? prev.preferred_publishers.filter(id => id !== publisherId)
        : [...prev.preferred_publishers, publisherId];
      
      return { ...prev, preferred_publishers: newPublishers };
    });
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError(null);

      const token = localStorage.getItem('wolfread_tokens');
      const tokens = token ? JSON.parse(token) : null;
      
      if (!tokens?.access) {
        navigate('/login');
        return;
      }

      const response = await api.preferences.saveProfile(preferences, tokens.access);
      
      if (response.status === 'success') {
        if (onComplete) {
          onComplete();
        } else {
          navigate('/');
        }
      }
    } catch (err) {
      setError(api.handleError(err, 'Failed to save preferences'));
    } finally {
      setSaving(false);
    }
  };

  const handleSkip = () => {
    if (onSkip) {
      onSkip();
    } else {
      navigate('/');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading preferences...</p>
        </div>
      </div>
    );
  }

  const selectedCategoryCount = Object.keys(preferences.preferred_categories).length;
  const selectedAuthorCount = preferences.preferred_authors.length;
  const selectedPublisherCount = preferences.preferred_publishers.length;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            📚 Set Your Reading Preferences
          </h1>
          <p className="text-gray-600 text-lg">
            Help us recommend books you'll love!
          </p>
          
          {/* Progress */}
          <div className="mt-6 flex items-center justify-center gap-2">
            {[1, 2, 3].map(s => (
              <div key={s} className="flex items-center">
                <div className={`
                  w-10 h-10 rounded-full flex items-center justify-center font-bold
                  ${s === step ? 'bg-blue-600 text-white' : 
                    s < step ? 'bg-green-500 text-white' : 
                    'bg-gray-200 text-gray-500'}
                `}>
                  {s < step ? '✓' : s}
                </div>
                {s < totalSteps && (
                  <div className={`w-12 h-1 ${s < step ? 'bg-green-500' : 'bg-gray-200'}`} />
                )}
              </div>
            ))}
          </div>
        </div>

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
            {error}
          </div>
        )}

        <div className="bg-white rounded-2xl shadow-xl p-8">
          
          {/* Step 1: Categories */}
          {step === 1 && (
            <div>
              <h2 className="text-2xl font-bold text-gray-800 mb-4">
                📖 What genres do you enjoy?
              </h2>
              <p className="text-gray-600 mb-6">
                Select your favorite categories. You can adjust how much you like each one.
              </p>
              
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {options.categories.map(category => {
                  const isSelected = preferences.preferred_categories[category.id] !== undefined;
                  const weight = preferences.preferred_categories[category.id] || 0.5;
                  
                  return (
                    <div key={category.id} className="flex items-center gap-4 p-3 border rounded-lg hover:bg-gray-50">
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => handleCategoryToggle(category.id, category.name)}
                        className="w-5 h-5"
                      />
                      
                      <span className="flex-1 font-medium text-gray-800">
                        {category.name}
                      </span>
                      
                      {isSelected && (
                        <div className="flex items-center gap-2">
                          <input
                            type="range"
                            min="0.1"
                            max="1.0"
                            step="0.1"
                            value={weight}
                            onChange={(e) => handleCategoryWeight(category.id, e.target.value)}
                            className="w-32"
                          />
                          <span className="text-sm text-gray-600 w-12">
                            {(weight * 100).toFixed(0)}%
                          </span>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
              
              <div className="mt-6 text-center text-sm text-gray-600">
                Selected: {selectedCategoryCount} categories
              </div>
            </div>
          )}

          {/* Step 2: Authors */}
          {step === 2 && (
            <div>
              <h2 className="text-2xl font-bold text-gray-800 mb-4">
                ✍️ Do you have favorite authors?
              </h2>
              <p className="text-gray-600 mb-6">
                Select authors whose books you typically enjoy (optional).
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-96 overflow-y-auto">
                {options.authors.slice(0, 50).map(author => {
                  const isSelected = preferences.preferred_authors.includes(author.id);
                  
                  return (
                    <label key={author.id} className="flex items-center gap-3 p-3 border rounded-lg hover:bg-gray-50 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => handleAuthorToggle(author.id)}
                        className="w-5 h-5"
                      />
                      <span className="text-gray-800">{author.full_name}</span>
                    </label>
                  );
                })}
              </div>
              
              <div className="mt-6 text-center text-sm text-gray-600">
                Selected: {selectedAuthorCount} authors
              </div>
            </div>
          )}

          {/* Step 3: Publishers & Filters */}
          {step === 3 && (
            <div>
              <h2 className="text-2xl font-bold text-gray-800 mb-4">
                🏢 Publishers & Filters
              </h2>
              <p className="text-gray-600 mb-6">
                Optional: Choose preferred publishers and set filters.
              </p>
              
              {/* Publishers */}
              <div className="mb-6">
                <h3 className="font-semibold text-gray-800 mb-3">Preferred Publishers</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-48 overflow-y-auto">
                  {options.publishers.slice(0, 30).map(publisher => {
                    const isSelected = preferences.preferred_publishers.includes(publisher.id);
                    
                    return (
                      <label key={publisher.id} className="flex items-center gap-3 p-2 border rounded hover:bg-gray-50 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={isSelected}
                          onChange={() => handlePublisherToggle(publisher.id)}
                          className="w-4 h-4"
                        />
                        <span className="text-sm text-gray-800">{publisher.name}</span>
                      </label>
                    );
                  })}
                </div>
              </div>
              
              {/* Filters */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Minimum Rating Preference
                  </label>
                  <select
                    value={preferences.min_rating_threshold}
                    onChange={(e) => setPreferences(prev => ({
                      ...prev,
                      min_rating_threshold: parseFloat(e.target.value)
                    }))}
                    className="w-full px-3 py-2 border rounded-lg"
                  >
                    <option value={0}>Any Rating</option>
                    <option value={5}>5+ ★</option>
                    <option value={6}>6+ ★</option>
                    <option value={7}>7+ ★</option>
                    <option value={8}>8+ ★</option>
                    <option value={9}>9+ ★</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Publication Year Range
                  </label>
                  <div className="flex items-center gap-2">
                    <input
                      type="number"
                      min="1900"
                      max="2024"
                      value={preferences.preferred_year_range.min}
                      onChange={(e) => setPreferences(prev => ({
                        ...prev,
                        preferred_year_range: {
                          ...prev.preferred_year_range,
                          min: parseInt(e.target.value)
                        }
                      }))}
                      className="w-24 px-3 py-2 border rounded-lg"
                    />
                    <span>-</span>
                    <input
                      type="number"
                      min="1900"
                      max="2024"
                      value={preferences.preferred_year_range.max}
                      onChange={(e) => setPreferences(prev => ({
                        ...prev,
                        preferred_year_range: {
                          ...prev.preferred_year_range,
                          max: parseInt(e.target.value)
                        }
                      }))}
                      className="w-24 px-3 py-2 border rounded-lg"
                    />
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Navigation */}
          <div className="mt-8 flex items-center justify-between">
            <button
              onClick={handleSkip}
              className="px-6 py-2 text-gray-600 hover:text-gray-800"
            >
              Skip for now
            </button>
            
            <div className="flex gap-3">
              {step > 1 && (
                <button
                  onClick={() => setStep(s => s - 1)}
                  className="px-6 py-3 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-lg font-medium"
                >
                  ← Back
                </button>
              )}
              
              {step < totalSteps ? (
                <button
                  onClick={() => setStep(s => s + 1)}
                  disabled={step === 1 && selectedCategoryCount === 0}
                  className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next →
                </button>
              ) : (
                <button
                  onClick={handleSave}
                  disabled={saving || selectedCategoryCount === 0}
                  className="px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {saving ? 'Saving...' : '✓ Complete'}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PreferenceForm;