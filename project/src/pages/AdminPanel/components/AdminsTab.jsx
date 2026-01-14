import React, { useState, useEffect } from 'react';
import { Shield, AlertCircle } from 'lucide-react';
import { adminAPI } from '../../../services/api';
import '../styles/AdminsTab.css';

const AdminsTab = () => {
  const [admins, setAdmins] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchAdmins();
  }, []);

  const fetchAdmins = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await adminAPI.getAdmins();
      setAdmins(data);
    } catch (err) {
      setError(err.message || 'Failed to load admins');
      console.error('Error fetching admins:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="admins-tab">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading admins...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="admins-tab">
      <div className="tab-header">
        <h2>
          <Shield size={24} />
          Admin Users
        </h2>
        <p className="tab-description">List of all administrators in the system</p>
      </div>

      {error && (
        <div className="error-message">
          <AlertCircle size={18} />
          {error}
        </div>
      )}

      {admins.length === 0 ? (
        <div className="no-data">
          <p>No admins found</p>
        </div>
      ) : (
        <div className="admins-grid">
          {admins.map((admin) => (
            <div key={admin.id} className="admin-card">
              <div className="admin-card-header">
                <div className="admin-avatar">
                  {admin.name.charAt(0).toUpperCase()}
                </div>
                <div className="admin-info">
                  <h3>{admin.name}</h3>
                  <p>{admin.email}</p>
                </div>
              </div>
              <div className="admin-badge">
                <Shield size={16} />
                Administrator
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AdminsTab;
