import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';

const PredictionForm = () => {
  console.log('Rendering PredictionForm');
  const [features, setFeatures] = useState({
    feature1: 0,
    feature2: 0,
    feature3: 0,
    feature4: 0
  });
  const [result, setResult] = useState(null);
  
  const queryClient = useQueryClient();
  
  const mutation = useMutation(
    (data) => axios.post('http://backend:8000/api/predict/', data), 
    {
      onSuccess: (response) => {
        setResult(response.data);
        queryClient.invalidateQueries('predictionHistory');
      }
    }
  );
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFeatures((prev) => ({
      ...prev,
      [name]: parseFloat(value)
    }));
  };
  
  const handleSubmit = (e) => {
    e.preventDefault();
    mutation.mutate(features);
  };
  
  return (
    <div className="prediction-form">
      <h2>Wykonaj nową predykcję</h2>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="feature1">Cecha 1:</label>
          <input
            type="number"
            step="0.1"
            id="feature1"
            name="feature1"
            value={features.feature1}
            onChange={handleChange}
            className="form-control"
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="feature2">Cecha 2:</label>
          <input
            type="number"
            step="0.1"
            id="feature2"
            name="feature2"
            value={features.feature2}
            onChange={handleChange}
            className="form-control"
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="feature3">Cecha 3:</label>
          <input
            type="number"
            step="0.1"
            id="feature3"
            name="feature3"
            value={features.feature3}
            onChange={handleChange}
            className="form-control"
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="feature4">Cecha 4:</label>
          <input
            type="number"
            step="0.1"
            id="feature4"
            name="feature4"
            value={features.feature4}
            onChange={handleChange}
            className="form-control"
          />
        </div>
        
        <button 
          type="submit" 
          className="btn btn-primary" 
          disabled={mutation.isLoading}
        >
          {mutation.isLoading ? 'Przetwarzanie...' : 'Przewiduj'}
        </button>
      </form>
      
      {mutation.isError && (
        <div className="alert alert-danger mt-3">
          Wystąpił błąd: {mutation.error.message}
        </div>
      )}
      
      {result && (
        <div className="prediction-result mt-3">
          <h3>Wynik predykcji</h3>
          <p><strong>Wartość:</strong> {result.prediction.toFixed(4)}</p>
          <p><strong>Pewność:</strong> {(result.confidence * 100).toFixed(2)}%</p>
        </div>
      )}
    </div>
  );
};

export default PredictionForm;