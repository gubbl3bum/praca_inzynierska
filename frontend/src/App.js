import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import PredictionForm from './components/sample/PredictionForm';
import ResultHistory from './components/sample/ResultHistory';

const Home = () => <h1>Strona startowa</h1>;

function App() {
  return (
    <Router>
      <div>
        <nav>
          <ul>
            <li><Link to="/">Home</Link></li>
            <li><Link to="/prediction">Prediction Form</Link></li>
            <li><Link to="/history">Result History</Link></li>
          </ul>
        </nav>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/prediction" element={<PredictionForm />} />
          <Route path="/history" element={<ResultHistory />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;