import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import RoutingComponent from './elements/RoutingComponent';
import Toast from './elements/Toast';
import './App.css';

function AppContent() {
  const { toasts, removeToast } = useAuth();
  
  return (
    <>
      <RoutingComponent />
      <Toast toasts={toasts} removeToast={removeToast} />
    </>
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </Router>
  );
}

export default App;