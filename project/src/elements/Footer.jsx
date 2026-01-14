import React from 'react';
import { Link } from 'react-router-dom';
import { Home, Map, User, Layers } from 'lucide-react';
import './Footer.css';

const Footer = () => {
  return (
    <footer className="footer">
      <Link to="/dashboard" className="footer-link">
        <Home size={22} />
        <span>Dashboard</span>
      </Link>
      <Link to="/projects" className="footer-link">
        <Layers size={22} />
        <span>Projects</span>
      </Link>
      
      <Link to="/map" className="footer-link" title="Delivery map">
        <Map size={22} />
        <span>Map</span>
      </Link>
      
      <Link to="/profile" className="footer-link">
        <User size={22} />
        <span>Profile</span>
      </Link>
    </footer>
  );
};

export default Footer;