import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import RoutingComponent from './elements/RoutingComponent';
import './App.css';

function App() {
  return (
    <Router> {/* Router должен быть ТОЛЬКО ЗДЕСЬ */}
      <AuthProvider>
        <RoutingComponent />
      </AuthProvider>
    </Router>
  );
}

export default App;