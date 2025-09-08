import apiClient from './authAPI';

const CHAT_BASE_URL = 'http://localhost:6868/api/chat';

export const chatAPI = {
  // Send message
  sendMessage: async (messageData) => {
    const response = await apiClient.post(`${CHAT_BASE_URL}/send`, messageData);
    return response;
  },

  // Get messages between current user and another user
  getMessages: async (otherUserId, limit = 50, offset = 0) => {
    const params = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString()
    });
    const response = await apiClient.get(`${CHAT_BASE_URL}/messages/${otherUserId}?${params}`);
    return response;
  },

  // Get all conversations
  getConversations: async (limit = 20, offset = 0) => {
    const params = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString()
    });
    const response = await apiClient.get(`${CHAT_BASE_URL}/conversations?${params}`);
    return response;
  },

  // Mark messages as read
  markMessagesAsRead: async (otherUserId) => {
    const response = await apiClient.post(`${CHAT_BASE_URL}/mark-read/${otherUserId}`);
    return response;
  },

  // Get unread message count
  getUnreadCount: async () => {
    const response = await apiClient.get(`${CHAT_BASE_URL}/unread-count`);
    return response;
  },

  // Delete message
  deleteMessage: async (messageId) => {
    const response = await apiClient.delete(`${CHAT_BASE_URL}/messages/${messageId}`);
    return response;
  },

  // Search messages
  searchMessages: async (query, otherUserId = null, limit = 20, offset = 0) => {
    const params = new URLSearchParams({
      query,
      limit: limit.toString(),
      offset: offset.toString()
    });
    if (otherUserId) {
      params.append('other_user_id', otherUserId);
    }
    const response = await apiClient.get(`${CHAT_BASE_URL}/search?${params}`);
    return response;
  },

  // Get chat statistics
  getChatStats: async () => {
    const response = await apiClient.get(`${CHAT_BASE_URL}/stats`);
    return response;
  }
};

export default chatAPI;
