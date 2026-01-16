import React from 'react';
import { Link } from 'react-router-dom';
import { Home, Map, User, Layers } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import './Footer.css';

const Footer = () => {
  const { user } = useAuth();

  return (
    <footer className="footer">
      <Link to="/dashboard" className="footer-link">
        <Home size={22} />
        <span>Панель</span>
      </Link>
      
      {user?.role !== 'Recipient' && (
        <Link to="/map" className="footer-link" title="Карта доставки">
          <Map size={22} />
          <span>Карта</span>
        </Link>
      )}
      
      <Link to="/profile" className="footer-link">
        <User size={22} />
        <span>Профиль</span>
      </Link>
    </footer>
  );
};

export default Footer;