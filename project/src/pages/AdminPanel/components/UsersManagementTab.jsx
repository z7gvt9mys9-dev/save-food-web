import React, { useState, useEffect } from 'react';
import { Users, Ban, CheckCircle, AlertCircle, Search, Trash2 } from 'lucide-react';
import { adminAPI } from '../../../services/api';
import '../styles/UsersManagementTab.css';

const UsersManagementTab = () => {
  const [users, setUsers] = useState([]);
  const [bannedUsers, setBannedUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [activeView, setActiveView] = useState('all');
  const [banReason, setBanReason] = useState('');
  const [selectedUserId, setSelectedUserId] = useState(null);
  const [showBanModal, setShowBanModal] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      setError('');
      const banned = await adminAPI.getBannedUsers();
      setBannedUsers(banned);
    } catch (err) {
      setError(err.message || 'Failed to load users');
      console.error('Error fetching users:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleBanClick = (userId) => {
    setSelectedUserId(userId);
    setBanReason('');
    setShowBanModal(true);
  };

  const handleBan = async () => {
    if (!selectedUserId) return;

    try {
      setActionLoading(true);
      await adminAPI.banUser(selectedUserId, banReason);
      setShowBanModal(false);
      setSelectedUserId(null);
      setBanReason('');
      await fetchUsers();
      setError('');
    } catch (err) {
      setError(err.message || 'Failed to ban user');
      console.error('Error banning user:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleUnban = async (userId) => {
    try {
      setActionLoading(true);
      await adminAPI.unbanUser(userId);
      await fetchUsers();
      setError('');
    } catch (err) {
      setError(err.message || 'Failed to unban user');
      console.error('Error unbanning user:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const filteredUsers = activeView === 'banned' 
    ? bannedUsers.filter(user =>
        user.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        user.email.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : users.filter(user =>
        user.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        user.email.toLowerCase().includes(searchQuery.toLowerCase())
      );

  if (loading) {
    return (
      <div className="users-management-tab">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading users...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="users-management-tab">
      <div className="tab-header">
        <h2>
          <Users size={24} />
          User Management
        </h2>
        <p className="tab-description">Manage and ban/unban users</p>
      </div>

      {error && (
        <div className="error-message">
          <AlertCircle size={18} />
          {error}
        </div>
      )}

      <div className="users-controls">
        <div className="search-box">
          <Search size={18} />
          <input
            type="text"
            placeholder="Search users by name or email..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="view-toggle">
          <button
            className={`toggle-button ${activeView === 'all' ? 'active' : ''}`}
            onClick={() => setActiveView('all')}
          >
            <Users size={16} />
            All Users ({users.length})
          </button>
          <button
            className={`toggle-button ${activeView === 'banned' ? 'active' : ''}`}
            onClick={() => setActiveView('banned')}
          >
            <Ban size={16} />
            Banned ({bannedUsers.length})
          </button>
        </div>
      </div>

      {filteredUsers.length === 0 ? (
        <div className="no-data">
          <p>No users found</p>
        </div>
      ) : (
        <div className="users-table">
          <div className="table-header">
            <div className="col-id">ID</div>
            <div className="col-name">Name</div>
            <div className="col-email">Email</div>
            <div className="col-status">Status</div>
            <div className="col-actions">Actions</div>
          </div>
          {filteredUsers.map((user) => (
            <div key={user.id} className="table-row">
              <div className="col-id">{user.id}</div>
              <div className="col-name">
                <div className="user-avatar">
                  {user.name.charAt(0).toUpperCase()}
                </div>
                {user.name}
              </div>
              <div className="col-email">{user.email}</div>
              <div className="col-status">
                {user.is_banned ? (
                  <span className="status-banned">
                    <Ban size={14} />
                    Banned
                  </span>
                ) : (
                  <span className="status-active">
                    <CheckCircle size={14} />
                    Active
                  </span>
                )}
              </div>
              <div className="col-actions">
                {user.is_banned ? (
                  <button
                    className="btn-unban"
                    onClick={() => handleUnban(user.id)}
                    disabled={actionLoading}
                  >
                    <CheckCircle size={14} />
                    Unban
                  </button>
                ) : (
                  <button
                    className="btn-ban"
                    onClick={() => handleBanClick(user.id)}
                    disabled={actionLoading}
                  >
                    <Ban size={14} />
                    Ban
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {showBanModal && (
        <div className="modal-overlay" onClick={() => !actionLoading && setShowBanModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Ban User</h3>
              <button
                className="close-btn"
                onClick={() => !actionLoading && setShowBanModal(false)}
                disabled={actionLoading}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <p className="warning">
                <AlertCircle size={18} />
                Are you sure you want to ban this user?
              </p>
              <div className="form-group">
                <label>Ban Reason (optional)</label>
                <textarea
                  value={banReason}
                  onChange={(e) => setBanReason(e.target.value)}
                  placeholder="Enter reason for banning this user..."
                  rows="4"
                  disabled={actionLoading}
                />
              </div>
            </div>
            <div className="modal-footer">
              <button
                className="btn-cancel"
                onClick={() => setShowBanModal(false)}
                disabled={actionLoading}
              >
                Cancel
              </button>
              <button
                className="btn-confirm-ban"
                onClick={handleBan}
                disabled={actionLoading}
              >
                {actionLoading ? 'Banning...' : 'Ban User'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UsersManagementTab;
