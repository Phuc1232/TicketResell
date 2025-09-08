import axios from 'axios';

const API_BASE_URL = 'http://localhost:6868/api/auth';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/refresh`, {}, {
            headers: {
              'Authorization': `Bearer ${refreshToken}`,
              'Content-Type': 'application/json',
            }
          });
          
          const { access_token } = response.data;
          localStorage.setItem('access_token', access_token);
          
          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export const authAPI = {
  // Register new user
  register: async (userData) => {
    const response = await apiClient.post('/register', userData);
    return response.data;
  },

  // Login user
  login: async (credentials) => {
    const response = await apiClient.post('/login', credentials);
    return response.data;
  },

  // Verify account
  verify: async (verificationCode, tempToken) => {
    const response = await apiClient.post('/verify', 
      { verification_code: verificationCode },
      {
        headers: {
          Authorization: `Bearer ${tempToken}`,
        }
      }
    );
    return response.data;
  },

  // Resend verification code
  resendVerification: async (token) => {
    const response = await apiClient.post('/resend-verification', {}, {
      headers: {
        Authorization: `Bearer ${token}`,
      }
    });
    return response.data;
  },

  // Refresh token
  refreshToken: async (refreshToken) => {
    const response = await apiClient.post('/refresh', {}, {
      headers: {
        Authorization: `Bearer ${refreshToken}`,
      }
    });
    return response.data;
  },
};

export default apiClient;
