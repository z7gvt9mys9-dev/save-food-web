import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import AdminsTab from './components/AdminsTab';
import UsersManagementTab from './components/UsersManagementTab';
import './AdminPanel.css';
import { Shield, Users, LogOut } from 'lucide-react';

const AdminPanel = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('admins');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    if (!user?.is_admin) {
      navigate('/dashboard');
      return;
    }

    setLoading(false);
  }, [user, isAuthenticated, navigate]);

  if (loading) {
    return (
      <div className="admin-loading">
        <div className="spinner"></div>
        <p>Loading admin panel...</p>
      </div>
    );
  }

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="admin-panel">
      <div className="admin-header">
        <div className="admin-header-content">
          <div className="admin-title">
            <Shield size={32} className="admin-icon" />
            <h1>Admin Panel</h1>
          </div>
          <div className="admin-user-info">
            <span className="admin-badge">Admin</span>
            <span className="admin-name">{user?.name}</span>
            <button onClick={handleLogout} className="logout-btn">
              <LogOut size={18} />
              Logout
            </button>
          </div>
        </div>
      </div>

      <div className="admin-container">
        <div className="admin-tabs">
          <button
            className={`tab-button ${activeTab === 'admins' ? 'active' : ''}`}
            onClick={() => setActiveTab('admins')}
          >
            <Shield size={20} />
            Admins List
          </button>
          <button
            className={`tab-button ${activeTab === 'users' ? 'active' : ''}`}
            onClick={() => setActiveTab('users')}
          >
            <Users size={20} />
            User Management
          </button>
        </div>

        <div className="admin-content">
          {activeTab === 'admins' && <AdminsTab />}
          {activeTab === 'users' && <UsersManagementTab />}
        </div>
      </div>
    </div>
  );
};

export default AdminPanel;
