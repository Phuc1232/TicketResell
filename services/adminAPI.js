import axios from 'axios';

const ADMIN_BASE_URL = 'http://localhost:6868/api/admin';

// Create separate axios instance for admin API
const adminClient = axios.create({
  baseURL: ADMIN_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
adminClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log('Admin API request with token:', token.substring(0, 20) + '...');
    } else {
      console.log('No token found for admin API request');
    }
    console.log('Admin API request config:', config);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for debugging
adminClient.interceptors.response.use(
  (response) => {
    console.log('Admin API response:', response);
    return response;
  },
  (error) => {
    console.error('Admin API error:', error);
    return Promise.reject(error);
  }
);

export const adminAPI = {
  // Get all users
  getAllUsers: async () => {
    console.log('Making admin request to: /users');
    const response = await adminClient.get('/users');
    return response;
  },

  // Advanced user search
  searchUsers: async (params = {}) => {
    const searchParams = new URLSearchParams();
    
    if (params.q) searchParams.append('q', params.q);
    if (params.status) searchParams.append('status', params.status);
    if (params.role_id) searchParams.append('role_id', params.role_id);
    if (params.verified !== undefined) searchParams.append('verified', params.verified);
    
    const response = await adminClient.get(`/users/search?${searchParams}`);
    return response;
  },

  // Delete user
  deleteUser: async (userId, reason) => {
    const response = await adminClient.delete(`/users/${userId}`, {
      data: { reason }
    });
    return response;
  },

  // Update user status
  updateUserStatus: async (userId, status, reason) => {
    const response = await adminClient.put(`/users/${userId}/status`, {
      status,
      reason
    });
    return response;
  },

  // Get recent registrations
  getRecentRegistrations: async (days = 7) => {
    const response = await adminClient.get(`/users/recent?days=${days}`);
    return response;
  },

  // Get admin info
  getAdminInfo: async () => {
    const response = await adminClient.get('/me');
    return response;
  },

  // Get system statistics
  getSystemStats: async () => {
    const response = await adminClient.get('/stats');
    return response;
  }
};

export default adminAPI;
