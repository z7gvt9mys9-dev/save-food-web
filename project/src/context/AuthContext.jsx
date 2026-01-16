import React, { createContext, useState, useContext, useEffect } from 'react';
import { authAPI, usersAPI, notificationsAPI, setAuth } from '../services/api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [toasts, setToasts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isInitializing, setIsInitializing] = useState(true);

  useEffect(() => {
    let isMounted = true;

    const initAuth = async () => {
      try {
        const token = localStorage.getItem('authToken');
        if (token) {
          try {
            const timeoutPromise = new Promise((_, reject) =>
              setTimeout(() => reject(new Error('Verification timeout')), 5000)
            );
            
            const userData = await Promise.race([
              authAPI.verify(),
              timeoutPromise
            ]);
            
            if (isMounted) {
              setUser(userData.user);
              setIsAuthenticated(true);
              try {
                const notifs = await Promise.race([
                  notificationsAPI.getAll(),
                  new Promise((_, reject) =>
                    setTimeout(() => reject(new Error('Timeout')), 3000)
                  )
                ]);
                if (isMounted) {
                  setNotifications(notifs);
                }
              } catch (notifError) {
                console.error('Notifications error:', notifError);
                if (isMounted) {
                  setNotifications([]);
                }
              }
            }
          } catch (error) {
            if (isMounted) {
              localStorage.removeItem('authToken');
              setIsAuthenticated(false);
              setUser(null);
            }
            console.error('Auth verification error:', error);
          }
        }
      } catch (error) {
        console.error(error);
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

  const showToast = (message, type = 'info', duration = 3000) => {
    const id = Math.random().toString(36).substr(2, 9);
    const newToast = { id, message, type };
    setToasts(prev => [...prev, newToast]);
    
    if (duration > 0) {
      setTimeout(() => {
        removeToast(id);
      }, duration);
    }
  };

  const removeToast = (id) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        notifications,
        toasts,
        loading,
        isInitializing,
        register,
        login,
        logout,
        updateUser,
        addNotification,
        clearNotification,
        markNotificationAsRead,
        showToast,
        removeToast
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);