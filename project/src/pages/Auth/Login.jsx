import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import './Auth.css';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (!email || !password) {
      setError('Заполните все поля');
      return;
    }
    const result = await login(email, password);
    if (result.success) {
      navigate('/dashboard');
    } else {
      // Display specific error message for wrong credentials
      if (result.message && result.message.includes('Invalid email or password')) {
        setError('Неправильный пароль или email');
      } else {
        setError(result.message || 'Ошибка при входе');
      }
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1>Save Food</h1>
        <h2>Вход</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your@email.com"
            />
          </div>
          <div className="form-group">
            <label>Пароль</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
            />
          </div>
          {error && <p className="error-message">{error}</p>}
          <button type="submit" className="btn-submit">
            Войти
          </button>
        </form>
        <p className="auth-footer">
          Нет аккаунта? <Link to="/register">Зарегистрируйтесь</Link>
        </p>
        <div className="test-credentials">
          <p><strong>Демо-аккаунты:</strong></p>
          <p><em>Developer (полный доступ):</em></p>
          <p>Email: developer@savefood.local</p>
          <p>Password: Developer123!@#</p>
          <p><em>Администратор:</em></p>
          <p>Email: admin@savefood.local</p>
          <p>Password: Admin123!@#</p>
          <p><em>Пользователь:</em></p>
          <p>Email: donor@example.com</p>
          <p>Password: password123</p>
        </div>
      </div>
    </div>
  );
};

export default Login;