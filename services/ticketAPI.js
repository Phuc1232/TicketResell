import apiClient from './authAPI';

const TICKET_BASE_URL = 'http://localhost:6868/tickets';

export const ticketAPI = {
  // Get all tickets
  getAllTickets: async () => {
    const response = await apiClient.get(`${TICKET_BASE_URL}/`);
    return response;
  },

  // Get ticket by ID
  getTicketById: async (ticketId) => {
    const response = await apiClient.get(`${TICKET_BASE_URL}/${ticketId}`);
    return response;
  },

  // Create new ticket (requires auth)
  createTicket: async (ticketData) => {
    const response = await apiClient.post(`${TICKET_BASE_URL}/`, ticketData);
    return response;
  },

  // Update ticket (requires auth)
  updateTicket: async (ticketId, ticketData) => {
    const response = await apiClient.put(`${TICKET_BASE_URL}/${ticketId}`, ticketData);
    return response;
  },

  // Get my tickets (requires auth)
  getMyTickets: async () => {
    const response = await apiClient.get(`${TICKET_BASE_URL}/my-tickets`);
    return response;
  },

  // Get tickets by owner
  getTicketsByOwner: async (ownerId) => {
    const response = await apiClient.get(`${TICKET_BASE_URL}/owner/${ownerId}`);
    return response;
  },

  // Search tickets by event name
  searchTickets: async (eventName) => {
    const response = await apiClient.get(`${TICKET_BASE_URL}/search?event_name=${encodeURIComponent(eventName)}`);
    return response;
  },

  // Advanced search tickets
  advancedSearch: async (filters) => {
    const params = new URLSearchParams();
    Object.keys(filters).forEach(key => {
      if (filters[key] !== undefined && filters[key] !== '') {
        params.append(key, filters[key]);
      }
    });
    const response = await apiClient.get(`${TICKET_BASE_URL}/search/advanced?${params.toString()}`);
    return response;
  },

  // Get trending tickets
  getTrendingTickets: async (limit = 10) => {
    const response = await apiClient.get(`${TICKET_BASE_URL}/trending?limit=${limit}`);
    return response;
  },

  // Get tickets by event type
  getTicketsByEventType: async (eventType, limit = 20) => {
    const response = await apiClient.get(`${TICKET_BASE_URL}/event-type/${eventType}?limit=${limit}`);
    return response;
  },

  // Increment view count
  incrementViewCount: async (ticketId) => {
    const response = await apiClient.post(`${TICKET_BASE_URL}/${ticketId}/view`);
    return response;
  },

  // Rate ticket (requires auth)
  rateTicket: async (ticketId, rating) => {
    const response = await apiClient.post(`${TICKET_BASE_URL}/${ticketId}/rate`, { rating });
    return response;
  },

  // Delete ticket (requires auth)
  deleteTicket: async (eventName, ownerUsername) => {
    const response = await apiClient.delete(`${TICKET_BASE_URL}/${encodeURIComponent(eventName)}/${encodeURIComponent(ownerUsername)}`);
    return response;
  },
};

export default apiClient;
