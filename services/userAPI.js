import apiClient from './authAPI';

const USER_BASE_URL = 'http://localhost:6868';

export const userAPI = {
  // Get current user info
  getCurrentUser: async () => {
    const response = await apiClient.get(`${USER_BASE_URL}/users/me`);
    return response;
  },

  // Update current user profile
  updateCurrentUser: async (userData) => {
    const response = await apiClient.put(`${USER_BASE_URL}/users/me`, userData);
    return response;
  },

  // Verify user account
  verifyAccount: async (verificationData) => {
    const response = await apiClient.post(`${USER_BASE_URL}/users/verify`, verificationData);
    return response;
  },

  // Get user profile by username (public)
  getUserProfile: async (username) => {
    const response = await apiClient.get(`${USER_BASE_URL}/users/profile/${username}`);
    return response;
  },

  // Get user's tickets
  getUserTickets: async (username) => {
    const response = await apiClient.get(`${USER_BASE_URL}/users/${username}/tickets`);
    return response;
  },

  // Rate user
  rateUser: async (targetUserId, ratingData) => {
    const response = await apiClient.post(`${USER_BASE_URL}/users/${targetUserId}/rate`, ratingData);
    return response;
  },

  // Search users
  searchUsers: async (params = {}) => {
    const searchParams = new URLSearchParams();
    
    if (params.q) searchParams.append('q', params.q);
    if (params.verified !== undefined) searchParams.append('verified', params.verified);
    if (params.min_rating) searchParams.append('min_rating', params.min_rating);
    if (params.status) searchParams.append('status', params.status);
    
    const response = await apiClient.get(`${USER_BASE_URL}/users/search?${searchParams}`);
    return response;
  },

  // Get all users (Admin only)
  getAllUsers: async () => {
    const response = await apiClient.get(`${USER_BASE_URL}/users/`);
    return response;
  },

  // Get user by ID (internal use)
  getUserById: async (userId) => {
    const response = await apiClient.get(`${USER_BASE_URL}/users/internal/${userId}`);
    return response;
  },

  // Delete user (Admin only)
  deleteUser: async (userId) => {
    const response = await apiClient.delete(`${USER_BASE_URL}/users/${userId}`);
    return response;
  }
};

export default apiClient;
