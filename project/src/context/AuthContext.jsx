// src/context/AuthContext.jsx

import React, { createContext, useState, useContext, useEffect } from 'react';
import { authAPI, usersAPI, notificationsAPI, setAuth } from '../services/api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isInitializing, setIsInitializing] = useState(true);

  // Initialize auth state on mount
  useEffect(() => {
    let isMounted = true;

    const initAuth = async () => {
      try {
        const token = localStorage.getItem('authToken');
        if (token) {
          try {
            const userData = await authAPI.verify();
            if (isMounted) {
              setUser(userData.user);
              setIsAuthenticated(true);
              
              // Fetch notifications
              const notifs = await notificationsAPI.getAll();
              if (isMounted) {
                setNotifications(notifs);
              }
            }
          } catch (error) {
            // Only logout on explicit 401 from backend
            if (error.message && error.message.includes('401')) {
              if (isMounted) {
                localStorage.removeItem('authToken');
                setIsAuthenticated(false);
              }
            }
            // Other errors: keep auth state, let user try again
          }
        }
      } finally {
        if (isMounted) {
          setLoading(false);
          setIsInitializing(false);
        }
      }
    };

    initAuth();

    return () => {
      isMounted = false;
    };
  }, []);

  const register = async (name, email, password, role) => {
    try {
      const result = await authAPI.register(name, email, password, role);
      setAuth(result.token);
      setUser(result.user);
      setIsAuthenticated(true);
      return { success: true, message: 'Registration successful' };
    } catch (error) {
      return { success: false, message: error.message };
    }
  };

  const login = async (email, password) => {
    try {
      const result = await authAPI.login(email, password);
      setAuth(result.token);
      setUser(result.user);
      setIsAuthenticated(true);
      
      // Fetch notifications after login
      const notifs = await notificationsAPI.getAll();
      setNotifications(notifs);
      
      return { success: true, message: 'Login successful' };
    } catch (error) {
      return { success: false, message: error.message };
    }
  };

  const logout = async () => {
    try {
      authAPI.logout();
      setUser(null);
      setIsAuthenticated(false);
      setNotifications([]);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const updateUser = async (updates) => {
    if (user) {
      try {
        const updated = await usersAPI.updateProfile(user.id, updates);
        setUser(updated);
      } catch (error) {
        console.error('Update user error:', error);
      }
    }
  };

  const addNotification = async (messageOrData, message, type) => {
    try {
      // Handle both string message and object data
      let notifData;
      if (typeof messageOrData === 'string') {
        notifData = {
          title: messageOrData,
          message: message || messageOrData,
          type: type || 'info'
        };
      } else {
        notifData = messageOrData;
      }
      
      const newNotif = await notificationsAPI.create(notifData);
      // Ensure notification has all fields needed
      const notifWithDefaults = {
        id: newNotif.id || Math.random(),
        title: newNotif.title || 'Уведомление',
        message: newNotif.message || newNotif.text || '',
        text: newNotif.message || newNotif.text || '',
        type: newNotif.type || 'info',
        order: newNotif.order || '',
        street: newNotif.street || '',
        timestamp: new Date(),
        ...newNotif
      };
      setNotifications([notifWithDefaults, ...notifications]);
    } catch (error) {
      console.error('Add notification error:', error);
    }
  };

  const clearNotification = async (id) => {
    try {
      await notificationsAPI.delete(id);
      setNotifications(notifications.filter(n => n.id !== id));
    } catch (error) {
      console.error('Delete notification error:', error);
    }
  };

  const markNotificationAsRead = async (id) => {
    try {
      await notificationsAPI.markAsRead(id);
      setNotifications(notifications.map(n =>
        n.id === id ? { ...n, read: true } : n
      ));
    } catch (error) {
      console.error('Mark read error:', error);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        notifications,
        loading,
        isInitializing,
        register,
        login,
        logout,
        updateUser,
        addNotification,
        clearNotification,
        markNotificationAsRead
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);