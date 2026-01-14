// API configuration and utilities
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const getAuthToken = () => {
  return localStorage.getItem('authToken');
};

const setAuthToken = (token) => {
  localStorage.setItem('authToken', token);
};

const clearAuthToken = () => {
  localStorage.removeItem('authToken');
};

const apiCall = async (endpoint, method = 'GET', data = null) => {
  const token = getAuthToken();
  const headers = {
    'Content-Type': 'application/json'
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const options = {
    method,
    headers
  };

  if (data) {
    options.body = JSON.stringify(data);
  }

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
    
    // Handle response
    let result;
    const contentType = response.headers.get('content-type');
    
    if (contentType && contentType.includes('application/json')) {
      result = await response.json();
    } else {
      result = await response.text();
    }

    if (!response.ok) {
      const errorMessage = 
        (typeof result === 'object' && result.detail) ||
        (typeof result === 'object' && result.error) ||
        result ||
        `HTTP Error ${response.status}`;
      throw new Error(errorMessage);
    }

    return result;
  } catch (error) {
    console.error('API Error:', {
      endpoint,
      method,
      errorMessage: error.message,
      errorStack: error.stack
    });
    throw error;
  }
};

// Auth API
export const authAPI = {
  register: (name, email, password, role) =>
    apiCall('/auth/register', 'POST', { name, email, password, role }),
  login: (email, password) =>
    apiCall('/auth/login', 'POST', { email, password }),
  verify: () =>
    apiCall('/auth/verify', 'GET'),
  logout: () => {
    clearAuthToken();
  }
};

// Users API
export const usersAPI = {
  getMe: () => apiCall('/users/me', 'GET'),
  getUser: (id) => apiCall(`/users/${id}`, 'GET'),
  updateProfile: (id, data) =>
    apiCall(`/users/${id}`, 'PUT', data),
  getAllUsers: () => apiCall('/users', 'GET'),
  updateMe: (data) =>
    apiCall('/users/me', 'PUT', data)  // Use /me endpoint for current user
};

// Projects API
export const projectsAPI = {
  getAll: () => apiCall('/projects', 'GET'),
  getById: (id) => apiCall(`/projects/${id}`, 'GET'),
  create: (data) => apiCall('/projects', 'POST', data),
  update: (id, data) => apiCall(`/projects/${id}`, 'PUT', data),
  delete: (id) => apiCall(`/projects/${id}`, 'DELETE')
};

// Issues API
export const issuesAPI = {
  getByProject: (projectId) =>
    apiCall(`/issues/project/${projectId}`, 'GET'),
  getById: (id) => apiCall(`/issues/${id}`, 'GET'),
  create: (data) => apiCall('/issues', 'POST', data),
  update: (id, data) => apiCall(`/issues/${id}`, 'PUT', data),
  updateStatus: (id, status) =>
    apiCall(`/issues/${id}/status`, 'PATCH', { status }),
  delete: (id) => apiCall(`/issues/${id}`, 'DELETE')
};

// Notifications API
export const notificationsAPI = {
  getAll: () => apiCall('/notifications', 'GET'),
  create: (data) => apiCall('/notifications', 'POST', data),
  markAsRead: (id) =>
    apiCall(`/notifications/${id}/read`, 'PATCH'),
  delete: (id) => apiCall(`/notifications/${id}`, 'DELETE')
};

// Donations/Products API
export const donationsAPI = {
  getAvailable: () => apiCall('/projects', 'GET'), // Get all active projects as available products
  getByProject: (projectId) =>
    apiCall(`/projects/${projectId}`, 'GET'),
  create: (projectId, data) =>
    apiCall(`/projects/${projectId}/donations`, 'POST', data)
};

// Admin API
export const adminAPI = {
  getAdmins: () => apiCall('/admin/admins', 'GET'),
  makeAdmin: (userId) =>
    apiCall(`/admin/users/${userId}/promote`, 'POST'),
  removeAdmin: (userId) =>
    apiCall(`/admin/users/${userId}/demote`, 'POST'),
  banUser: (userId, reason) =>
    apiCall(`/admin/users/${userId}/ban`, 'POST', { reason }),
  unbanUser: (userId) =>
    apiCall(`/admin/users/${userId}/ban`, 'DELETE'),
  getBanStatus: (userId) =>
    apiCall(`/admin/users/${userId}/ban-status`, 'GET'),
  getBannedUsers: () =>
    apiCall('/admin/users/banned/list', 'GET')
};

// Routing API
export const routingAPI = {
  health: () => apiCall('/routes/health', 'GET'),
  getRoute: (locations) => {
    console.log('[routingAPI] Requesting route for locations:', locations);
    return apiCall('/routes/route', 'POST', { locations, costing: 'auto' })
      .then(response => {
        console.log('[routingAPI] Route response:', response);
        return response;
      })
      .catch(error => {
        console.error('[routingAPI] Route request failed:', error);
        throw error;
      });
  },
  getDistanceMatrix: (locations) =>
    apiCall('/routes/distance-matrix', 'POST', { locations, costing: 'auto' }),
  optimize: (locations, numCouriers = 1) =>
    apiCall(`/routes/optimize?num_couriers=${numCouriers}`, 'POST', { locations, costing: 'auto' })
};

// Helper to set auth token after login
export const setAuth = (token) => {
  setAuthToken(token);
};

export default apiCall;