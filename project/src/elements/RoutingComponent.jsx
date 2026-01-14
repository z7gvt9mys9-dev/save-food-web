import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Header from './Header';
import Footer from './Footer';
import Login from '../pages/Auth/Login';
import Register from '../pages/Auth/Register';
import Dashboard from '../pages/Dashboard/Dashboard';
import Profile from '../pages/Profile/Profile';
import MapPage from '../pages/MapPage/MapPage';
import Projects from '../pages/Projects/Projects';
import AdminPanel from '../pages/AdminPanel/AdminPanel';

const RoutingComponent = () => {
  const { isAuthenticated, loading, isInitializing } = useAuth();

  // During initialization, show loading screen
  if (loading || isInitializing) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        backgroundColor: '#0b0c0d',
        color: '#eeeeee'
      }}>
        <div style={{
          textAlign: 'center'
        }}>
          <div style={{
            width: '40px',
            height: '40px',
            border: '3px solid rgba(107, 114, 128, 0.2)',
            borderTop: '3px solid #6b7280',
            borderRadius: '50%',
            margin: '0 auto 16px',
            animation: 'spin 1s linear infinite'
          }} />
          <p>Loading...</p>
          <style>{`
            @keyframes spin {
              to { transform: rotate(360deg); }
            }
          `}</style>
        </div>
      </div>
    );
  }

  return (
    <div className="app-wrapper">
      {isAuthenticated && <Header />}
      <main className="main-content">
        <Routes>
          <Route path="/login" element={!isAuthenticated ? <Login /> : <Navigate to="/dashboard" replace />} />
          <Route path="/register" element={!isAuthenticated ? <Register /> : <Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={isAuthenticated ? <Dashboard /> : <Navigate to="/login" replace />} />
          <Route path="/profile" element={isAuthenticated ? <Profile /> : <Navigate to="/login" replace />} />
          <Route path="/projects" element={isAuthenticated ? <Projects /> : <Navigate to="/login" replace />} />
          <Route path="/map" element={isAuthenticated ? <MapPage /> : <Navigate to="/login" replace />} />
          <Route path="/admin" element={isAuthenticated ? <AdminPanel /> : <Navigate to="/login" replace />} />
          <Route path="/" element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Navigate to="/login" replace />} />
        </Routes>
      </main>
      {isAuthenticated && <Footer />}
    </div>
  );
};

export default RoutingComponent;