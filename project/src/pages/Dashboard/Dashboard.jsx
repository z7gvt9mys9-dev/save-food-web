import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import './Dashboard.css';
import { Package, TrendingUp, Clock, AlertCircle } from 'lucide-react';
import { projectsAPI, donationsAPI } from '../../services/api';

const Dashboard = () => {
  const { user, addNotification } = useAuth();
  const navigate = useNavigate();
  const [donorForm, setDonorForm] = useState({
    productName: '',
    quantity: '',
    expiryDate: '',
    description: ''
  });
  const [projects, setProjects] = useState([]);
  const [availableProducts, setAvailableProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Prevent rendering if user data is not ready
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
        <p>Loading dashboard...</p>
      </div>
    );
  }

  // Fetch projects on component mount
  useEffect(() => {
    const fetchProjects = async () => {
      try {
        setLoading(true);
        const data = await projectsAPI.getAll();
        setProjects(data);
        
        // Convert projects to available products for display
        const products = data.map((project, index) => ({
          id: project.id,
          name: project.name,
          icon: project.icon || '',
          quantity: `${Math.floor(Math.random() * 20) + 5} шт`,
          distance: `${Math.round(Math.random() * 5) + 1} км`,
          description: project.description || 'Проект помощи',
          status: 'Доступен',
          goal_amount: project.goal_amount,
          current_amount: project.current_amount,
          is_verified: project.is_verified
        }));
        setAvailableProducts(products);
        setError(null);
      } catch (err) {
        console.error('Error fetching projects:', err);
        setError('Failed to load projects');
      } finally {
        setLoading(false);
      }
    };

    fetchProjects();
  }, []);

  // Normalize user role for rendering
  const userRole = user.role ? String(user.role).toLowerCase() : 'recipient';

  const handleDonorChange = (e) => {
    const { name, value } = e.target;
    setDonorForm(prev => ({ ...prev, [name]: value }));
  };

  const handleDonorSubmit = (e) => {
    e.preventDefault();
    addNotification(`Продукт "${donorForm.productName}" выставлен на раздачу`);
    setDonorForm({ productName: '', quantity: '', expiryDate: '', description: '' });
  };

  const handleTakeProduct = (productName) => {
    addNotification(`Вы зарезервировали: ${productName}`);
  };

  const renderDonorDashboard = () => (
    <div className="dashboard-content">
      <div className="error-banner">
        <AlertCircle size={18} />
        <span>Внимание: проверьте срок годности продуктов!</span>
      </div>

      <h2>Панель донора</h2>
      <form className="donor-form" onSubmit={handleDonorSubmit}>
        <div className="form-group">
          <label>Название продукта</label>
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
            placeholder="Дополнительная информация..."
            rows="4"
          />
        </div>
        <button type="submit" className="btn-submit">Выставить продукт</button>
      </form>

      <div className="projects-section">
        <h3>Ваши проекты</h3>
        {loading ? (
          <p style={{ color: '#8a8f98', textAlign: 'center', padding: '2rem' }}>Загрузка проектов...</p>
        ) : error ? (
          <p style={{ color: '#ef4444', textAlign: 'center', padding: '2rem' }}>{error}</p>
        ) : projects.length === 0 ? (
          <p style={{ color: '#8a8f98', textAlign: 'center', padding: '2rem' }}>Проектов нет, отдыхайте</p>
        ) : (
          <div className="products-grid">
            {projects.map((project) => (
              <div key={project.id} className="product-card">
                <div className="product-icon">{project.icon || ''}</div>
                <h4>{project.name}</h4>
                <p>{project.description || 'Проект помощи'}</p>
                <div className="progress-container">
                  <div className="progress-bar">
                    <div 
                      className="progress-fill" 
                      style={{width: `${(project.current_amount / project.goal_amount) * 100}%`}}
                    ></div>
                  </div>
                  <p className="progress-text">${project.current_amount.toFixed(0)}/${project.goal_amount.toFixed(0)}</p>
                </div>
                <span className="verified-badge">{project.is_verified ? '✓ Проверено' : 'На проверке'}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="available-products">
        <h3>Доступные продукты</h3>
        {loading ? (
          <p style={{ color: '#8a8f98', textAlign: 'center', padding: '2rem' }}>Загрузка продуктов...</p>
        ) : availableProducts.length === 0 ? (
          <p style={{ color: '#8a8f98', textAlign: 'center', padding: '2rem' }}>Продуктов нет, отдыхайте</p>
        ) : (
          <div className="products-grid">
            {availableProducts.map((product) => (
              <div key={product.id} className="product-card">
                <div className="product-icon">{product.icon}</div>
                <h4>{product.name}</h4>
                <p className="product-qty">{product.quantity}</p>
                <p className="product-location">📍 {product.distance}</p>
                <p className="product-status">{product.status}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="donation-history">
        <h3>История отдач</h3>
        <div className="donations-grid">
          <div className="donation-card">
            <div className="donation-icon">BREAD</div>
            <h4>Хлеб ржаной</h4>
            <p>10 шт</p>
            <p className="status">Получено</p>
            <p className="date">2 дня назад</p>
          </div>
          <div className="donation-card">
            <div className="donation-icon">MILK</div>
            <h4>Молоко коровье</h4>
            <p>5 л</p>
            <p className="status">Получено</p>
            <p className="date">1 неделю назад</p>
          </div>
          <div className="donation-card">
            <div className="donation-icon">SALAD</div>
            <h4>Овощная смесь</h4>
            <p>3 кг</p>
            <p className="status">Получено</p>
            <p className="date">2 недели назад</p>
          </div>
          <div className="donation-card">
            <div className="donation-icon">APPLE</div>
            <h4>Яблоки</h4>
            <p>15 шт</p>
            <p className="status">Получено</p>
            <p className="date">3 недели назад</p>
          </div>
        </div>
      </div>
    </div>
  );

  const renderDelivererDashboard = () => (
    <div className="dashboard-content">
      <div className="error-banner">
        <AlertCircle size={18} />
        <span>Внимание: у вас есть новые заказы!</span>
      </div>

      <h2>Панель доставщика</h2>
      <div className="stats-grid">
        <div className="stat-card">
          <TrendingUp size={32} />
          <h3>Всего доставок</h3>
          <p>{user?.deliveries || 150}</p>
        </div>
        <div className="stat-card">
          <Package size={32} />
          <h3>Рейтинг</h3>
          <p>{user?.rating || 4.8}</p>
        </div>
        <div className="stat-card">
          <Clock size={32} />
          <h3>На пути</h3>
          <p>2 заказа</p>
        </div>
      </div>

      <div className="orders-section">
        <h3>Доступные заказы</h3>
        <div className="orders-grid">
          <div className="order-card">
            <div className="order-status">Ожидает получения</div>
            <h4>Доставка продуктов №1</h4>
            <p>Улица Ленина, 45</p>
            <p>Сегодня 14:00 - 16:00</p>
            <button className="btn-accept">Принять</button>
          </div>
          <div className="order-card">
            <div className="order-status">Ожидает получения</div>
            <h4>Доставка продуктов №2</h4>
            <p>Пр. Мира, 12</p>
            <p>Завтра 10:00 - 12:00</p>
            <button className="btn-accept">Принять</button>
          </div>
          <div className="order-card">
            <div className="order-status">Ожидает получения</div>
            <h4>Доставка продуктов №3</h4>
            <p>Ул. Советская, 88</p>
            <p>🕐 Завтра 15:00 - 17:00</p>
            <button className="btn-accept">Принять</button>
          </div>
        </div>
      </div>
    </div>
  );

  const renderReceiverDashboard = () => (
    <div className="dashboard-content">
      <div className="error-banner">
        <AlertCircle size={18} />
        <span>Доступные продукты находятся на карте. Откройте раздел "Карта" чтобы найти ближайшие доступные продукты.</span>
      </div>

      <h2>Панель получателя</h2>
      <div className="receiver-info">
        <p>Доступные продукты находятся на карте. Откройте раздел "Карта" чтобы найти ближайшие доступные продукты.</p>
      </div>

      <div className="available-products">
        <h3>Доступные проекты</h3>
        {loading ? (
          <p style={{ color: '#8a8f98', textAlign: 'center', padding: '2rem' }}>Загрузка проектов...</p>
        ) : error ? (
          <p style={{ color: '#ef4444', textAlign: 'center', padding: '2rem' }}>{error}</p>
        ) : projects.length === 0 ? (
          <p style={{ color: '#8a8f98', textAlign: 'center', padding: '2rem' }}>Проектов нет, отдыхайте</p>
        ) : (
          <div className="products-grid">
            {projects.map((project) => (
              <button 
                key={project.id}
                className="product-card" 
                onClick={() => {
                  handleTakeProduct(project.name);
                  navigate('/map');
                }}
              >
                <div className="product-icon">{project.icon || ''}</div>
                <h4>{project.name}</h4>
                <p>{project.description || 'Проект помощи'}</p>
                <div className="progress-container">
                  <div className="progress-bar">
                    <div 
                      className="progress-fill" 
                      style={{width: `${(project.current_amount / project.goal_amount) * 100}%`}}
                    ></div>
                  </div>
                  <p className="progress-text">${project.current_amount.toFixed(0)}/${project.goal_amount.toFixed(0)}</p>
                </div>
                {project.latitude && project.longitude && (
                  <p className="location">📍 {Math.round(Math.random() * 5 + 1)} км</p>
                )}
                <span className="product-action">Перейти на карту</span>
              </button>
            ))}
          </div>
        )}
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