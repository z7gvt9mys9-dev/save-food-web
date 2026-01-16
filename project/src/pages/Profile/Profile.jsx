import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { LogOut, Edit2, Eye, EyeOff, User, X, Upload } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import './Profile.css';

const EMOJI_GALLERY = [];

const Profile = () => {
  const { user, updateUser, logout, addNotification } = useAuth();
  const navigate = useNavigate();
  const [isEditing, setIsEditing] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showEmail, setShowEmail] = useState(false);
  const [showAvatarPicker, setShowAvatarPicker] = useState(false);
  const [editData, setEditData] = useState({
    name: user?.name || '',
    password: '',
    avatar: user?.avatar || ''
  });

  const isValidEmojiForAvatar = (text) => {
    if (!text) return false;
    if (text.includes('http') || text.includes('://') || text.startsWith('data:')) return false;
    const emojiRegex = /^[\p{Emoji_Presentation}\p{Extended_Pictographic}]+$/u;
    return emojiRegex.test(text);
  };

  const handleEmojiSelect = (emoji) => {
    if (!isValidEmojiForAvatar(emoji)) {
      addNotification('Только эмодзи разрешены для аватара');
      return;
    }
    setEditData(prev => ({ ...prev, avatar: emoji }));
    setShowAvatarPicker(false);
  };

  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        const base64 = event.target?.result;
        setEditData(prev => ({ ...prev, avatar: base64 }));
      };
      reader.readAsDataURL(file);
    }
  };

  const maskEmail = (email) => {
    if (!email) return '';
    const [localPart, domain] = email.split('@');
    if (localPart.length <= 3) return email;
    return localPart.substring(0, 3) + '***' + localPart[localPart.length - 1] + '@' + domain;
  };

  const handleEditChange = (e) => {
    const { name, value } = e.target;
    setEditData(prev => ({ ...prev, [name]: value }));
  };

  const handleSaveChanges = () => {
    updateUser({
      name: editData.name,
      avatar: editData.avatar || null
    });
    addNotification('Профиль обновлен');
    setIsEditing(false);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isValidEmoji = (avatar) => {
    if (!avatar) return false;
    if (avatar.includes('http') || avatar.includes('://')) return false;
    if (avatar === '' || avatar === null) return false;
    return avatar && avatar.length > 0 && !avatar.includes('/');
  };

  return (
    <div className="profile-container">
      <div className="profile-header">
        <div className="profile-avatar">
          {user?.avatar?.startsWith('data:') ? (
            <img 
              src={user.avatar} 
              alt={user?.name}
              style={{ width: '100%', height: '100%', borderRadius: '50%', objectFit: 'cover' }}
            />
          ) : isValidEmoji(user?.avatar) ? (
            <span className="avatar-emoji">{user.avatar}</span>
          ) : (
            <div className="avatar-icon">
              <User size={36} color="#8a8f98" />
            </div>
          )}
        </div>
        <div className="profile-info">
          <h1>{user?.name}</h1>
          <div className="profile-stats">
            <span className="stat">★ {user?.rating_level || 'Bronze'}</span>
            <span className="stat">[XP] {user?.xp || 0} XP</span>
          </div>
        </div>
      </div>

      <div className="profile-card">
        <div className="card-header">
          <h2>Основная информация</h2>
        </div>
        <div className="card-content">
          <div className="form-group">
            <label>Имя</label>
            {isEditing ? (
              <input
                type="text"
                name="name"
                value={editData.name}
                onChange={handleEditChange}
                className="form-input"
              />
            ) : (
              <div className="form-value">{user?.name}</div>
            )}
          </div>

          <div className="form-group">
            <label>Email</label>
            <div className="email-row">
              <div className="form-value">
                {showEmail ? user?.email : maskEmail(user?.email)}
              </div>
              <button
                className="icon-btn"
                onClick={() => setShowEmail(!showEmail)}
                title={showEmail ? 'Скрыть' : 'Показать'}
              >
                {showEmail ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>
          </div>

          {isEditing && (
            <div className="form-group">
              <label>Аватар</label>
              <div style={{ display: 'flex', gap: '10px', alignItems: 'center', marginBottom: '12px' }}>
                <label className="btn btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer', margin: 0, flex: 1 }}>
                  <Upload size={16} />
                  Загрузить фото
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleFileUpload}
                    style={{ display: 'none' }}
                  />
                </label>
              </div>

              {editData.avatar && (
                <div style={{
                  padding: '12px',
                  backgroundColor: '#1a1b1d',
                  borderRadius: '8px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px'
                }}>
                  <div style={{
                    fontSize: '2rem',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    minWidth: '50px',
                    minHeight: '50px'
                  }}>
                    {editData.avatar.startsWith('data:') ? (
                      <img 
                        src={editData.avatar} 
                        alt="preview" 
                        style={{ maxWidth: '50px', maxHeight: '50px', borderRadius: '4px' }}
                      />
                    ) : (
                      editData.avatar
                    )}
                  </div>
                  <div style={{ flex: 1 }}>
                    <p style={{ margin: '0 0 4px 0', color: '#eeeeee', fontSize: '0.9rem' }}>Выбранный аватар</p>
                    <p style={{ margin: 0, color: '#8a8f98', fontSize: '0.8rem' }}>
                      {editData.avatar.startsWith('data:') ? 'Загруженное изображение' : 'Эмодзи'}
                    </p>
                  </div>
                </div>
              )}
            </div>
          )}

          {isEditing && (
            <div className="form-group">
              <label>Новый пароль (опционально)</label>
              <div className="password-row">
                <input
                  type={showPassword ? 'text' : 'password'}
                  name="password"
                  value={editData.password}
                  onChange={handleEditChange}
                  placeholder="••••••••"
                  className="form-input"
                />
                <button
                  className="icon-btn"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>
          )}
        </div>

        <div className="card-actions">
          {!isEditing ? (
            <button className="btn btn-primary" onClick={() => setIsEditing(true)}>
              <Edit2 size={18} />
              <span>Редактировать</span>
            </button>
          ) : (
            <>
              <button className="btn btn-primary" onClick={handleSaveChanges}>
                Сохранить
              </button>
              <button className="btn btn-secondary" onClick={() => setIsEditing(false)}>
                Отмена
              </button>
            </>
          )}
        </div>
      </div>

      {user?.role === 'Deliverer' && (
        <div className="profile-card achievements-section">
          <div className="card-header">
            <h2>Статистика</h2>
          </div>
          <div className="achievements-grid">
            <div className="stat-item">
              <div className="stat-value">{user?.rating || 4.8}</div>
              <p className="stat-label">Рейтинг</p>
            </div>
            <div className="stat-item">
              <div className="stat-value">{user?.deliveries || 150}</div>
              <p className="stat-label">Доставок</p>
            </div>
            <div className="stat-item">
              <div className="stat-value">{user?.achievements?.length || 0}</div>
              <p className="stat-label">Достижений</p>
            </div>
          </div>
        </div>
      )}

      <div className="logout-container">
        <button className="btn-logout" onClick={handleLogout}>
          <LogOut size={18} />
          <span>Выход</span>
        </button>
      </div>
    </div>
  );
};

export default Profile;