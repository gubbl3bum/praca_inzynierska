import React from 'react';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const ResultHistory = () => {
  console.log('Rendering ResultHistory');
  const { data, isLoading, isError, error } = useQuery('predictionHistory', 
    () => axios.get('http://localhost:8000/api/history/').then(res => res.data),
    {
      refetchInterval: 5000 
    }
  );
  
  if (isLoading) {
    return <div>Ładowanie historii...</div>;
  }
  
  if (isError) {
    return <div>Błąd: {error.message}</div>;
  }
  
  const chartData = data.map(item => ({
    id: item.id,
    prediction: item.prediction,
    confidence: item.confidence,
    feature1: item.request.feature1,
    feature2: item.request.feature2,
    feature3: item.request.feature3,
    feature4: item.request.feature4,
  }));
  
  return (
    <div className="result-history">
      <h2>Historia predykcji</h2>
      
      {data.length === 0 ? (
        <p>Brak historii predykcji</p>
      ) : (
        <>
          <div className="chart-container" style={{ width: '100%', height: 300 }}>
            <ResponsiveContainer>
              <LineChart data={chartData.reverse()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="id" label={{ value: 'ID Predykcji', position: 'insideBottomRight', offset: 0 }} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="prediction" stroke="#8884d8" name="Predykcja" />
                <Line type="monotone" dataKey="confidence" stroke="#82ca9d" name="Pewność" />
              </LineChart>
            </ResponsiveContainer>
          </div>
          
          <h3>Ostatnie wyniki</h3>
          <div className="table-responsive">
            <table className="table table-striped">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Predykcja</th>
                  <th>Pewność</th>
                  <th>Cecha 1</th>
                  <th>Cecha 2</th>
                  <th>Cecha 3</th>
                  <th>Cecha 4</th>
                </tr>
              </thead>
              <tbody>
                {data.map(item => (
                  <tr key={item.id}>
                    <td>{item.id}</td>
                    <td>{item.prediction.toFixed(4)}</td>
                    <td>{(item.confidence * 100).toFixed(2)}%</td>
                    <td>{item.request.feature1}</td>
                    <td>{item.request.feature2}</td>
                    <td>{item.request.feature3}</td>
                    <td>{item.request.feature4}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
};

export default ResultHistory;