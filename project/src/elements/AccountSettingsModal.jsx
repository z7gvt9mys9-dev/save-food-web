import React from 'react';
import { X, Shield, User, Package, Truck } from 'lucide-react';
import './AccountSettingsModal.css';

const AccountSettingsModal = ({ user, onClose }) => {
  const getRoleIcon = (role) => {
    switch (role?.toLowerCase()) {
      case 'administrator':
      case 'admin':
        return <Shield size={20} />;
      case 'donor':
        return <Package size={20} />;
      case 'courier':
      case 'deliverer':
        return <Truck size={20} />;
      case 'recipient':
        return <User size={20} />;
      default:
        return <User size={20} />;
    }
  };

  const getRoleDescription = (role) => {
    const roleMap = {
      administrator: 'Administrator with full access to manage users, projects, and system settings',
      donor: 'Donor who can contribute products and food to communities',
      courier: 'Courier who delivers products to recipients',
      deliverer: 'Courier who delivers products to recipients',
      recipient: 'Recipient who can receive products from donors'
    };
    return roleMap[role?.toLowerCase()] || 'User role';
  };

  return (
    <div className="settings-modal-overlay" onClick={onClose}>
      <div className="settings-modal-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="settings-modal-header">
          <h2>Account Settings</h2>
          <button className="settings-modal-close" onClick={onClose} aria-label="Close">
            <X size={20} />
          </button>
        </div>

        <div className="settings-modal-body">
          <div className="settings-section">
            <h3>Account Information</h3>
            <div className="settings-row">
              <span className="settings-label">Name:</span>
              <span className="settings-value">{user?.name}</span>
            </div>
            <div className="settings-row">
              <span className="settings-label">Email:</span>
              <span className="settings-value">{user?.email}</span>
            </div>
          </div>

          <div className="settings-section">
            <h3>Role & Permissions</h3>
            <div className="role-card">
              <div className="role-icon">
                {getRoleIcon(user?.role)}
              </div>
              <div className="role-info">
                <h4>{user?.role || 'User'}</h4>
                <p>{getRoleDescription(user?.role)}</p>
              </div>
            </div>
          </div>

          <div className="settings-section">
            <h3>User Statistics</h3>
            <div className="stats-grid">
              <div className="stat-box">
                <span className="stat-value">{user?.xp || 0}</span>
                <span className="stat-label">Experience Points</span>
              </div>
              <div className="stat-box">
                <span className="stat-value">{user?.rating_level || 'Bronze'}</span>
                <span className="stat-label">Level</span>
              </div>
              {user?.rating && (
                <div className="stat-box">
                  <span className="stat-value">{user.rating}</span>
                  <span className="stat-label">Rating</span>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="settings-modal-footer">
          <button className="settings-modal-btn" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default AccountSettingsModal;
