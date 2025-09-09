import apiClient from './authAPI';

const FEEDBACK_BASE_URL = 'http://localhost:6868/api/feedback';

export const feedbackAPI = {
  // Submit user feedback after transaction
  submitUserFeedback: async (userId, feedbackData) => {
    const response = await apiClient.post(`${FEEDBACK_BASE_URL}/user/${userId}`, feedbackData);
    return response;
  },

  // Submit ticket feedback/review
  submitTicketFeedback: async (ticketId, feedbackData) => {
    const response = await apiClient.post(`${FEEDBACK_BASE_URL}/ticket/${ticketId}`, feedbackData);
    return response;
  },

  // Get user feedback
  getUserFeedback: async (userId, limit = 20, offset = 0) => {
    const params = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString()
    });
    const response = await apiClient.get(`${FEEDBACK_BASE_URL}/user/${userId}?${params}`);
    return response;
  },

  // Get ticket feedback
  getTicketFeedback: async (ticketId, limit = 20, offset = 0) => {
    const params = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString()
    });
    const response = await apiClient.get(`${FEEDBACK_BASE_URL}/ticket/${ticketId}?${params}`);
    return response;
  },

  // Get user feedback summary
  getUserFeedbackSummary: async (userId) => {
    const response = await apiClient.get(`${FEEDBACK_BASE_URL}/user/${userId}/summary`);
    return response;
  },

  // Get user feedback analytics
  getUserFeedbackAnalytics: async (userId) => {
    const response = await apiClient.get(`${FEEDBACK_BASE_URL}/user/${userId}/analytics`);
    return response;
  },

  // Get my feedback summary
  getMyFeedbackSummary: async () => {
    const response = await apiClient.get(`${FEEDBACK_BASE_URL}/my-feedback`);
    return response;
  },

  // Get my feedback analytics
  getMyFeedbackAnalytics: async () => {
    const response = await apiClient.get(`${FEEDBACK_BASE_URL}/my-analytics`);
    return response;
  }
};

export default feedbackAPI;
