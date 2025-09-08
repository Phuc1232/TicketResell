import apiClient from './authAPI';

// Try both base URLs based on documentation inconsistency
const PAYMENT_BASE_URL = 'http://localhost:6868/api/payments';

export const paymentAPI = {
  // Create new payment
  createPayment: async (paymentData) => {
    const response = await apiClient.post(`${PAYMENT_BASE_URL}/`, {
      methods: paymentData.methods,
      amount: paymentData.amount,
      title: paymentData.title,
      transaction_id: paymentData.transactionId
    });
    return response;
  },

  // Get user payments
  getUserPayments: async () => {
    const response = await apiClient.get(`${PAYMENT_BASE_URL}/`);
    return response;
  },

  // Get payment by ID
  getPaymentById: async (paymentId) => {
    const response = await apiClient.get(`${PAYMENT_BASE_URL}/${paymentId}`);
    return response;
  },

  // Update payment status
  updatePaymentStatus: async (paymentId, status) => {
    const response = await apiClient.put(`${PAYMENT_BASE_URL}/${paymentId}/status`, {
      status: status
    });
    return response;
  },

  // Process payment
  processPayment: async (paymentId, processData) => {
    const response = await apiClient.post(`${PAYMENT_BASE_URL}/${paymentId}/process`, {
      payment_method_data: processData.paymentMethodData,
      wallet_type: processData.walletType,
      confirmation_code: processData.confirmationCode,
      gateway_response: processData.gatewayResponse
    });
    return response;
  },

  // Get payment history (paginated)
  getPaymentHistory: async (limit = 20, offset = 0) => {
    const response = await apiClient.get(`${PAYMENT_BASE_URL}/history?limit=${limit}&offset=${offset}`);
    return response;
  },

  // Get payment statistics
  getPaymentStatistics: async () => {
    const response = await apiClient.get(`${PAYMENT_BASE_URL}/statistics`);
    return response;
  },

  // MoMo specific endpoints
  momo: {
    // Handle MoMo return URL
    handleReturn: async (returnParams) => {
      const params = new URLSearchParams(returnParams).toString();
      const response = await apiClient.get(`${PAYMENT_BASE_URL}/momo/return?${params}`);
      return response;
    },

    // Handle MoMo IPN
    handleIPN: async (ipnData) => {
      const response = await apiClient.post(`${PAYMENT_BASE_URL}/momo/ipn`, ipnData);
      return response;
    },

    // Handle MoMo notification
    handleNotification: async (notificationData) => {
      const response = await apiClient.post(`${PAYMENT_BASE_URL}/momo/notify`, notificationData);
      return response;
    },

    // Process callback
    processCallback: async (callbackData) => {
      const response = await apiClient.post(`${PAYMENT_BASE_URL}/momo/callback/process`, callbackData);
      return response;
    }
  }
};

export default paymentAPI;
