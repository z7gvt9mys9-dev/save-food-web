import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Bell, X, User, Shield } from 'lucide-react';
import AccountSettingsModal from './AccountSettingsModal';
import AdminPanel from './AdminPanel';
import './Header.css';

const Header = () => {
  const navigate = useNavigate();
  const { user, notifications, clearNotification } = useAuth();
  const [showNotifications, setShowNotifications] = useState(false);
  const [selectedNotification, setSelectedNotification] = useState(null);
  const [showAccountSettings, setShowAccountSettings] = useState(false);
  const [showAdminMenu, setShowAdminMenu] = useState(false);
  const [showAdminPanel, setShowAdminPanel] = useState(false);

  const handleNotificationClick = (notif) => {
    setSelectedNotification(notif);
  };

  const closeModal = () => {
    setSelectedNotification(null);
  };

  const closeNotificationPanel = () => {
    setShowNotifications(false);
  };

  const isValidEmoji = (avatar) => {
    if (!avatar) return false;
    if (avatar.includes('http') || avatar.includes('://')) return false;
    if (avatar === '' || avatar === null) return false;
    return avatar && avatar.length > 0 && !avatar.includes('/');
  };

  const hasAvatar = isValidEmoji(user?.avatar);

  return (
    <>
      <header className="header">
        <div className="header-left">
          <button 
            className="notification-btn" 
            onClick={() => setShowNotifications(!showNotifications)}
            title="Уведомления"
            aria-label="Открыть уведомления"
          >
            <Bell size={20} />
            {notifications.length > 0 && (
              <span className="notification-badge">{notifications.length}</span>
            )}
          </button>
        </div>

        <div className="header-center">
          <h1>Спасаем еду</h1>
        </div>

        <div className="header-right">
          {user?.is_admin && (
            <div className="admin-menu-container">
              <button 
                className="admin-btn" 
                onClick={() => setShowAdminMenu(!showAdminMenu)}
                title="Меню администратора"
                aria-label="Меню администратора"
              >
                <Shield size={20} />
              </button>
              
              {showAdminMenu && (
                <div className="admin-dropdown-menu">
                  <button
                    className="dropdown-item"
                    onClick={() => {
                      setShowAccountSettings(true);
                      setShowAdminMenu(false);
                    }}
                  >
                    <Shield size={16} />
                    Настройки аккаунта
                  </button>
                  <button
                    className="dropdown-item"
                    onClick={() => {
                      setShowAdminPanel(true);
                      setShowAdminMenu(false);
                    }}
                  >
                    <User size={16} />
                    Управление пользователями
                  </button>
                </div>
              )}
            </div>
          )}
          <div 
            className="user-avatar" 
            title={user?.name}
            onClick={() => navigate('/profile')}
            style={{ cursor: 'pointer' }}
            role="button"
            tabIndex={0}
            onKeyPress={(e) => e.key === 'Enter' && navigate('/profile')}
          >
            {user?.avatar?.startsWith('data:') ? (
              <img 
                src={user.avatar} 
                alt={user?.name}
                style={{ width: '100%', height: '100%', borderRadius: '50%', objectFit: 'cover' }}
              />
            ) : hasAvatar ? (
              <span className="avatar-text">{user?.avatar}</span>
            ) : (
              <div className="avatar-placeholder">
                <User size={16} color="#8a8f98" />
              </div>
            )}
          </div>
        </div>
      </header>

      {showNotifications && (
        <div className="notification-overlay" onClick={closeNotificationPanel} />
      )}

      {showNotifications && (
        <div className="notification-drawer">
          <div className="drawer-header">
            <h3>Уведомления</h3>
            <button 
              onClick={closeNotificationPanel}
              className="drawer-close-btn"
              aria-label="Закрыть"
            >
              <X size={18} />
            </button>
          </div>
          <div className="drawer-content">
            {notifications.length === 0 ? (
              <p className="empty-notifications">Нет уведомлений</p>
            ) : (
              notifications.map(notif => (
                <div
                  key={notif.id}
                  className="notification-item"
                  onClick={() => handleNotificationClick(notif)}
                  role="button"
                  tabIndex={0}
                >
                  <div className="notification-text">
                    <p>{notif.message || notif.text || notif.title || 'Уведомление'}</p>
                  </div>
                  <button
                    className="notification-delete-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      clearNotification(notif.id);
                    }}
                    title="Удалить"
                  >
                    <X size={16} />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {selectedNotification && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{selectedNotification.title || 'Уведомление'}</h2>
              <button className="modal-close-btn" onClick={closeModal}>
                <X size={20} />
              </button>
            </div>
            <div className="modal-body">
              <p className="modal-text">{selectedNotification.message || selectedNotification.text || 'Нет содержания'}</p>
              {selectedNotification.order && (
                <p className="modal-detail"> Заказ: {selectedNotification.order}</p>
              )}
              {selectedNotification.street && (
                <p className="modal-detail"> Улица: {selectedNotification.street}</p>
              )}
              {selectedNotification.timestamp && (
                <p className="modal-time">
                  {typeof selectedNotification.timestamp === 'string' 
                    ? selectedNotification.timestamp 
                    : selectedNotification.timestamp.toLocaleString()}
                </p>
              )}
            </div>
            <div className="modal-footer">
              <button className="modal-btn-primary" onClick={closeModal}>
                Закрыть
              </button>
            </div>
          </div>
        </div>
      )}

      {showAccountSettings && (
        <AccountSettingsModal 
          user={user}
          onClose={() => setShowAccountSettings(false)}
        />
      )}

      {showAdminPanel && (
        <AdminPanel 
          onClose={() => setShowAdminPanel(false)}
        />
      )}
    </>
  );
};

export default Header;