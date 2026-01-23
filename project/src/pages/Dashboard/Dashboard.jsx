import React, { useState, useCallback, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import './Dashboard.css';
import { Package, TrendingUp, Clock, AlertCircle, Trash2, Check, X } from 'lucide-react';
import { useProjects } from '../../hooks/useProjects';
import { projectsAPI } from '../../services/api';

const Dashboard = () => {
  const { user, addNotification, showToast } = useAuth();
  const navigate = useNavigate();
  
  const { projects, loading, error, refetch } = useProjects(user?.id);
  const [deliveries, setDeliveries] = useState([]);
  const [deliveriesLoading, setDeliveriesLoading] = useState(false);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [selectedDelivery, setSelectedDelivery] = useState(null);

  const [donorForm, setDonorForm] = useState({
    productName: '',
    quantity: '',
    expiryDate: '',
    description: '',
    location: '',
    latitude: null,
    longitude: null,
    deliveryMethod: 'courier'
  });

  const [locationSuggestions, setLocationSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);

  useEffect(() => {
    if (user && String(user.role).toLowerCase() === 'courier') {
      fetchDeliveries();
    }
  }, [user]);

  const fetchDeliveries = async () => {
    setDeliveriesLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/deliveries', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        }
      });
      const data = await response.json();
      setDeliveries(Array.isArray(data) ? data : (data?.deliveries || []));
    } catch (err) {
      console.error('Error fetching deliveries:', err);
    }
    setDeliveriesLoading(false);
  };

  if (!user) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        backgroundColor: '#0b0c0d',
        color: '#e6e7eb'
      }}>
        <p>Загружа панель...</p>
      </div>
    );
  }

  const userRole = user.role ? String(user.role).toLowerCase() : 'recipient';

  const handleDonorChange = (e) => {
    const { name, value } = e.target;
    setDonorForm(prev => ({ ...prev, [name]: value }));
    
    if (name === 'location' && value.length >= 2) {
      searchLocations(value);
    } else if (name === 'location') {
      setLocationSuggestions([]);
      setShowSuggestions(false);
    }
  };

  const searchLocations = useCallback(async (query) => {
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?` +
        `q=${encodeURIComponent(query + ', Moscow, Russia')}&` +
        `format=json&limit=10&countrycodes=ru`,
        {
          headers: {
            'User-Agent': 'SaveFood-App'
          }
        }
      );
      const data = await response.json();
      setLocationSuggestions(data);
      setShowSuggestions(true);
    } catch (err) {
      setLocationSuggestions([]);
    }
  }, []);

  const handleLocationSelect = (location) => {
    setDonorForm(prev => ({
      ...prev,
      location: location.display_name,
      latitude: parseFloat(location.lat),
      longitude: parseFloat(location.lon)
    }));
    setShowSuggestions(false);
    setLocationSuggestions([]);
  };

  const handleDonorSubmit = (e) => {
    e.preventDefault();
    
    const newProject = {
      name: donorForm.productName,
      description: donorForm.description || 'Проект помощи',
      goal_amount: 100,
      icon: 'box',
      color: '#4CAF50',
      latitude: donorForm.latitude,
      longitude: donorForm.longitude
    };

    projectsAPI.create(newProject)
      .then(() => {
        addNotification(`Product "${donorForm.productName}" posted`);
        setDonorForm({ productName: '', quantity: '', expiryDate: '', description: '', location: '', latitude: null, longitude: null });
        refetch();
      })
      .catch((err) => {
        addNotification(`Error creating project: ${err.message}`);
      });
  };

  const handleTakeProduct = (productName) => {
    addNotification(`Reserved: ${productName}`);
  };

  const handleDeleteProject = (projectId) => {
    projectsAPI.delete(projectId)
      .then(() => {
        showToast('Project deleted successfully', 'success');
        refetch();
      })
      .catch((err) => {
        showToast(`Error deleting project: ${err.message}`, 'error');
      });
  };

  const handleAcceptDelivery = (delivery) => {
    setSelectedDelivery(delivery);
    setShowConfirmModal(true);
  };

  const confirmAcceptDelivery = async () => {
    if (!selectedDelivery) return;
    
    try {
      const response = await fetch('http://localhost:5000/api/deliveries/accept', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`
        },
        body: JSON.stringify({ delivery_id: selectedDelivery.id })
      });
      
      if (response.ok) {
        showToast('Order accepted successfully', 'success');
        setShowConfirmModal(false);
        
        if (selectedDelivery.project) {
          localStorage.setItem('mapZoomLocation', JSON.stringify({
            latitude: selectedDelivery.project.latitude,
            longitude: selectedDelivery.project.longitude,
            deliveryId: selectedDelivery.id
          }));
        }
        
        setSelectedDelivery(null);
        
        navigate('/map');
      } else {
        showToast('Error accepting order', 'error');
      }
    } catch (err) {
      showToast(`Error: ${err.message}`, 'error');
    }
  };

  const renderProjectsGrid = () => {
    if (loading) {
      return (
        <p style={{ color: '#8a8f98', textAlign: 'center', padding: '2rem' }}>
          Загрузка проектов...
        </p>
      );
    }

    if (error) {
      return (
        <div style={{ 
          color: '#ef4444', 
          textAlign: 'center', 
          padding: '2rem',
          backgroundColor: '#1a1a1a',
          borderRadius: '0.5rem',
          border: '1px solid #ef4444'
        }}>
          <AlertCircle style={{ display: 'inline', marginRight: '0.5rem' }} size={18} />
          {error}
          <button 
            onClick={refetch}
            style={{
              display: 'block',
              marginTop: '1rem',
              padding: '0.5rem 1rem',
              backgroundColor: '#ef4444',
              color: 'white',
              border: 'none',
              borderRadius: '0.25rem',
              cursor: 'pointer'
            }}
          >
            Попробовать снова
          </button>
        </div>
      );
    }

    if (!projects || projects.length === 0) {
      return (
        <p style={{ color: '#8a8f98', textAlign: 'center', padding: '2rem' }}>
          Проектов нет
        </p>
      );
    }

    return (
      <div className="products-grid">
        {projects.map((project) => (
          <div key={project.id} className="product-card" style={{ position: 'relative' }}>
            {user?.id === project.owner_id && (
              <button
                onClick={() => handleDeleteProject(project.id)}
                style={{
                  position: 'absolute',
                  top: '0.5rem',
                  right: '0.5rem',
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  color: '#ef4444',
                  padding: '0.25rem',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
                title="Delete project"
              >
                <Trash2 size={16} />
              </button>
            )}
            <div className="product-icon">#{project.id}</div>
            <h4>{project.name}</h4>
            <p>{project.description || 'Проект помощи'}</p>
            {project.latitude && project.longitude && (
              <p style={{ fontSize: '0.75rem', color: '#8a8f98', marginTop: '0.5rem' }}>
                {project.latitude.toFixed(2)}, {project.longitude.toFixed(2)}
              </p>
            )}
          </div>
        ))}
      </div>
    );
  };

  const renderDonorDashboard = () => (
    <div className="dashboard-content">
      <div className="error-banner">
        <AlertCircle size={18} />
        <span>Проверьте даты истечения!</span>
      </div>

      <h2>Панель донора</h2>
      <form className="donor-form" onSubmit={handleDonorSubmit}>
        <div className="form-group">
          <label>Название товара</label>
          <input
            type="text"
            name="productName"
            value={donorForm.productName}
            onChange={handleDonorChange}
            placeholder="Хлеб, молоко, овощи..."
            required
          />
        </div>
        <div className="form-group">
          <label>Количество</label>
          <input
            type="text"
            name="quantity"
            value={donorForm.quantity}
            onChange={handleDonorChange}
            placeholder="10 шт, 2 кг..."
            required
          />
        </div>
        <div className="form-group">
          <label>Дата истечения</label>
          <input
            type="date"
            name="expiryDate"
            value={donorForm.expiryDate}
            onChange={handleDonorChange}
            required
          />
        </div>
        <div className="form-group">
          <label>Описание</label>
          <textarea
            name="description"
            value={donorForm.description}
            onChange={handleDonorChange}
            placeholder="Дополнительная инфо..."
            rows="4"
          />
        </div>
        <div className="form-group" style={{ position: 'relative' }}>
          <label>Где вы находитесь</label>
          <input
            type="text"
            name="location"
            value={donorForm.location}
            onChange={handleDonorChange}
            placeholder="Введите улицу и номер дома в Москве..."
            autoComplete="off"
          />
          {showSuggestions && locationSuggestions.length > 0 && (
            <div style={{
              position: 'absolute',
              top: '100%',
              left: 0,
              right: 0,
              backgroundColor: '#1a1a1a',
              border: '1px solid #333',
              borderRadius: '0.25rem',
              maxHeight: '200px',
              overflowY: 'auto',
              zIndex: 1000
            }}>
              {locationSuggestions.map((location, idx) => (
                <div
                  key={idx}
                  onClick={() => handleLocationSelect(location)}
                  style={{
                    padding: '0.75rem',
                    borderBottom: '1px solid #333',
                    cursor: 'pointer',
                    color: '#e6e7eb',
                    fontSize: '0.875rem'
                  }}
                  onMouseEnter={(e) => e.target.style.backgroundColor = '#2a2a2a'}
                  onMouseLeave={(e) => e.target.style.backgroundColor = 'transparent'}
                >
                  {location.display_name}
                </div>
              ))}
            </div>
          )}
          {donorForm.latitude && donorForm.longitude && (
            <p style={{ fontSize: '0.75rem', color: '#4CAF50', marginTop: '0.25rem' }}>
              Координаты: {donorForm.latitude.toFixed(4)}, {donorForm.longitude.toFixed(4)}
            </p>
          )}
        </div>
        <div className="form-group">
          <label>Способ доставки</label>
          <select name="deliveryMethod" value={donorForm.deliveryMethod} onChange={handleDonorChange}>
            <option value="courier">Курьер - доставка добровольцем</option>
            <option value="parcel_locker">Почтомат - получение через автомат</option>
            <option value="both">Оба способа - выбор получателем</option>
          </select>
        </div>
        <button type="submit" className="btn-submit">Опубликовать товар</button>
      </form>

      <div className="projects-section">
        <h3>Ваши проекты</h3>
        {renderProjectsGrid()}
      </div>
    </div>
  );

  const renderDelivererDashboard = () => (
    <div className="dashboard-content">
      <div className="error-banner">
        <AlertCircle size={18} />
        <span>У вас есть новые заказы!</span>
      </div>

      <h2>Панель курьера</h2>
      <div className="stats-grid">
        <div className="stat-card">
          <TrendingUp size={32} />
          <h3>Всего доставок</h3>
          <p>{user?.courier_deliveries || 0}</p>
        </div>
        <div className="stat-card">
          <Package size={32} />
          <h3>Рейтинг</h3>
          <p>{(user?.courier_rating || 5.0).toFixed(1)}</p>
        </div>
        <div className="stat-card">
          <Clock size={32} />
          <h3>Среднее время доставки</h3>
          <p>{(user?.courier_avg_delivery_time || 0).toFixed(0)} min</p>
        </div>
      </div>

      <div className="projects-section">
        <h3>Доступные заказы</h3>
        {deliveriesLoading ? (
          <p style={{ color: '#8a8f98', textAlign: 'center', padding: '2rem' }}>
            Загружа заказов...
          </p>
        ) : deliveries.length === 0 ? (
          <p style={{ color: '#8a8f98', textAlign: 'center', padding: '2rem' }}>
            Нет доступных заказов
          </p>
        ) : (
          <div className="products-grid">
            {deliveries.map((delivery) => (
              <div key={delivery.id} className="product-card">
                <div className="product-icon">{delivery.project.id}</div>
                <h4>{delivery.project.name}</h4>
                <p>{delivery.project.description || 'Заказ доставки'}</p>
                {delivery.project.latitude && delivery.project.longitude && (
                  <p style={{ fontSize: '0.75rem', color: '#8a8f98', marginTop: '0.5rem' }}>
                    {delivery.project.latitude.toFixed(2)}, {delivery.project.longitude.toFixed(2)}
                  </p>
                )}
                <button
                  onClick={() => handleAcceptDelivery(delivery)}
                  style={{
                    marginTop: '1rem',
                    padding: '0.5rem 1rem',
                    backgroundColor: '#4CAF50',
                    color: 'white',
                    border: 'none',
                    borderRadius: '0.25rem',
                    cursor: 'pointer',
                    width: '100%'
                  }}
                >
                  Принять заказ
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {showConfirmModal && selectedDelivery && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'flex-end',
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: '#1a1a1a',
            width: '100%',
            maxWidth: '100%',
            height: '50%',
            padding: '2rem',
            borderRadius: '1rem 1rem 0 0',
            color: '#e6e7eb',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between'
          }}>
            <div>
              <h3 style={{ marginBottom: '1rem' }}>Подтвердите принятие заказа</h3>
              <p style={{ marginBottom: '0.5rem' }}>
                <strong>Товар:</strong> {selectedDelivery.project.name}
              </p>
              <p style={{ marginBottom: '0.5rem' }}>
                <strong>Описание:</strong> {selectedDelivery.project.description || 'N/A'}
              </p>
              {selectedDelivery.project.latitude && selectedDelivery.project.longitude && (
                <p style={{ marginBottom: '1rem' }}>
                  <strong>Местоположение:</strong> {selectedDelivery.project.latitude.toFixed(4)}, {selectedDelivery.project.longitude.toFixed(4)}
                </p>
              )}
              <p style={{ color: '#8a8f98' }}>
                Вы уверены, что хотите принять этот заказ?
              </p>
            </div>

            <div style={{ display: 'flex', gap: '1rem' }}>
              <button
                onClick={confirmAcceptDelivery}
                style={{
                  flex: 1,
                  padding: '1rem',
                  backgroundColor: '#4CAF50',
                  color: 'white',
                  border: 'none',
                  borderRadius: '0.25rem',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '0.5rem',
                  fontSize: '1rem'
                }}
              >
                <Check size={20} /> Да, принять
              </button>
              <button
                onClick={() => {
                  setShowConfirmModal(false);
                  setSelectedDelivery(null);
                }}
                style={{
                  flex: 1,
                  padding: '1rem',
                  backgroundColor: '#ef4444',
                  color: 'white',
                  border: 'none',
                  borderRadius: '0.25rem',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '0.5rem',
                  fontSize: '1rem'
                }}
              >
                <X size={20} /> Отменить
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderReceiverDashboard = () => (
    <div className="dashboard-content">
      <div className="error-banner">
        <AlertCircle size={18} />
        <span>Available products on map. Open Map section to find nearby products.</span>
      </div>

      <h2>Панель получателя</h2>
      <div className="receiver-info">
        <p>Available products on map. Open Map section to find nearby products.</p>
      </div>

      <div className="available-products">
        <h3>Доступные проекты</h3>
        {renderProjectsGrid()}
      </div>
    </div>
  );

  return (
    <div className="dashboard-container">
      {userRole === 'donor' && renderDonorDashboard()}
      {userRole === 'courier' && renderDelivererDashboard()}
      {(userRole === 'recipient' || !['donor', 'courier'].includes(userRole)) && renderReceiverDashboard()}
    </div>
  );
};

export default Dashboard;