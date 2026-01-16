import React, { useState, useEffect } from 'react';
import { X, Shield, User, Trash2, Plus, CheckCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { adminAPI, usersAPI } from '../services/api';
import './AdminPanel.css';

const AdminPanel = ({ onClose }) => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('admins');
  const [admins, setAdmins] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const isDeveloper = user?.name === 'Developer';

  useEffect(() => {
    fetchData();
  }, [activeTab]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      if (activeTab === 'admins') {
        const adminsList = await adminAPI.getAdmins();
        setAdmins(adminsList);
      } else {
        const usersList = await usersAPI.getAllUsers();
        setUsers(usersList);
      }
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Ошибка при загрузке данных');
    } finally {
      setLoading(false);
    }
  };

  const handleMakeAdmin = async (userId) => {
    if (!isDeveloper) {
      alert('Только Developer может назначать админов');
      return;
    }

    try {
      await adminAPI.makeAdmin(userId);
      alert('Пользователь назначен администратором');
      setUsers(users.map(u => u.id === userId ? { ...u, is_admin: true } : u));
      fetchData();
    } catch (err) {
      console.error('Error making admin:', err);
      alert('Ошибка при назначении администратора');
    }
  };

  const handleRemoveAdmin = async (userId) => {
    if (!isDeveloper) {
      alert('Только Developer может снимать админов');
      return;
    }

    if (window.confirm('Вы уверены, что хотите снять админа?')) {
      try {
        await adminAPI.removeAdmin(userId);
        alert('Администратор удален');
        setAdmins(admins.filter(a => a.id !== userId));
        fetchData();
      } catch (err) {
        console.error('Error removing admin:', err);
        alert('Ошибка при удалении администратора');
      }
    }
  };

  const handleBanUser = async (userId) => {
    if (!isDeveloper) {
      alert('Только Developer может банить пользователей');
      return;
    }

    const reason = prompt('Причина блокировки:');
    if (reason) {
      try {
        await adminAPI.banUser(userId, reason);
        alert('Пользователь заблокирован');
        fetchData();
      } catch (err) {
        console.error('Error banning user:', err);
        alert('Ошибка при блокировании пользователя');
      }
    }
  };

  const handleUnbanUser = async (userId) => {
    if (!isDeveloper) {
      alert('Только Developer может разбанивать пользователей');
      return;
    }

    try {
      await adminAPI.unbanUser(userId);
      alert('Пользователь разблокирован');
      fetchData();
    } catch (err) {
      console.error('Error unbanning user:', err);
      alert('Ошибка при разблокировании пользователя');
    }
  };

  return (
    <div className="admin-panel-overlay" onClick={onClose}>
      <div className="admin-panel-dialog" onClick={(e) => e.stopPropagation()}>
        <div className="admin-panel-header">
          <h2>Административная панель</h2>
          <button className="admin-panel-close" onClick={onClose} aria-label="Close">
            <X size={20} />
          </button>
        </div>

        <div className="admin-panel-tabs">
          <button
            className={`admin-tab ${activeTab === 'admins' ? 'active' : ''}`}
            onClick={() => setActiveTab('admins')}
          >
            <Shield size={18} />
            Администраторы
          </button>
          <button
            className={`admin-tab ${activeTab === 'users' ? 'active' : ''}`}
            onClick={() => setActiveTab('users')}
          >
            <User size={18} />
            Пользователи
          </button>
        </div>

        <div className="admin-panel-content">
          {!isDeveloper && (
            <div className="access-denied">
              <Shield size={32} />
              <p>Доступ к управлению предоставлен только Developer</p>
            </div>
          )}

          {isDeveloper && loading && (
            <p className="loading-text">Загрузка...</p>
          )}

          {isDeveloper && error && (
            <p className="error-text">{error}</p>
          )}

          {isDeveloper && !loading && activeTab === 'admins' && (
            <div className="admins-list">
              {admins.length === 0 ? (
                <p className="empty-text">Администраторов нет</p>
              ) : (
                admins.map(admin => (
                  <div key={admin.id} className="admin-item">
                    <div className="admin-info">
                      <div className="admin-avatar">
                        {admin.avatar?.startsWith('data:') ? (
                          <img src={admin.avatar} alt={admin.name} />
                        ) : (
                          <Shield size={24} />
                        )}
                      </div>
                      <div className="admin-details">
                        <h4>{admin.name}</h4>
                        <p>{admin.email}</p>
                        <span className="admin-badge">
                          <CheckCircle size={14} />
                          Администратор
                        </span>
                      </div>
                    </div>
                    <button
                      className="btn-remove-admin"
                      onClick={() => handleRemoveAdmin(admin.id)}
                      title="Снять администратора"
                    >
                      <Trash2 size={18} />
                    </button>
                  </div>
                ))
              )}
            </div>
          )}

          {isDeveloper && !loading && activeTab === 'users' && (
            <div className="users-list">
              {users.length === 0 ? (
                <p className="empty-text">Пользователей нет</p>
              ) : (
                users.map(usr => (
                  <div key={usr.id} className="user-item">
                    <div className="user-info">
                      <div className="user-avatar">
                        {usr.avatar?.startsWith('data:') ? (
                          <img src={usr.avatar} alt={usr.name} />
                        ) : (
                          <User size={24} />
                        )}
                      </div>
                      <div className="user-details">
                        <h4>{usr.name}</h4>
                        <p>{usr.email}</p>
                        <span className={`role-badge ${usr.role?.toLowerCase()}`}>
                          {usr.role || 'User'}
                        </span>
                        {usr.is_admin && (
                          <span className="admin-badge">Admin</span>
                        )}
                        {usr.is_banned && (
                          <span className="banned-badge">Заблокирован</span>
                        )}
                      </div>
                    </div>
                    <div className="user-actions">
                      {!usr.is_admin && (
                        <button
                          className="btn-make-admin"
                          onClick={() => handleMakeAdmin(usr.id)}
                          title="Сделать администратором"
                        >
                          <Plus size={18} />
                        </button>
                      )}
                      {usr.is_banned ? (
                        <button
                          className="btn-unban"
                          onClick={() => handleUnbanUser(usr.id)}
                          title="Разблокировать"
                        >
                          Разблокировать
                        </button>
                      ) : (
                        <button
                          className="btn-ban"
                          onClick={() => handleBanUser(usr.id)}
                          title="Заблокировать"
                        >
                          <Trash2 size={18} />
                        </button>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminPanel;
