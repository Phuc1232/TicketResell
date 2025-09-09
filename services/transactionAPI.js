import apiClient from './authAPI';

const TRANSACTION_BASE_URL = 'http://localhost:6868/api/transactions';

export const transactionAPI = {
  // Preview transaction before purchase
  previewTransaction: async (ticketId) => {
    const response = await apiClient.post(`${TRANSACTION_BASE_URL}/preview-transaction`, {
      ticket_id: ticketId
    });
    return response;
  },

  // Initiate a new transaction
  initiateTransaction: async (transactionData) => {
    const response = await apiClient.post(`${TRANSACTION_BASE_URL}/initiate`, {
      ticket_id: transactionData.ticketId,
      payment_method: transactionData.paymentMethod,
      amount: transactionData.amount,
      payment_data: transactionData.paymentData
    });
    return response;
  },

  // Complete ticket purchase workflow
  buyTicket: async (purchaseData) => {
    const response = await apiClient.post(`${TRANSACTION_BASE_URL}/buy-ticket`, {
      ticket_id: purchaseData.ticketId,
      payment_method: purchaseData.paymentMethod,
      payment_data: purchaseData.paymentData
    });
    return response;
  },

  // Get transaction status
  getTransactionStatus: async (transactionId) => {
    const response = await apiClient.get(`${TRANSACTION_BASE_URL}/status/${transactionId}`);
    return response;
  },

  // Handle transaction callback
  handleCallback: async (callbackData) => {
    const response = await apiClient.post(`${TRANSACTION_BASE_URL}/callback`, {
      transaction_id: callbackData.transactionId,
      status: callbackData.status,
      payment_transaction_id: callbackData.paymentTransactionId,
      error_message: callbackData.errorMessage
    });
    return response;
  }
};

export default transactionAPI;
