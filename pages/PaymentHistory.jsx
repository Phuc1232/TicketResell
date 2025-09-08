import React, { useState, useEffect, useCallback } from 'react';
import { paymentAPI } from '../services/paymentAPI';
import { formatPrice, formatDate } from '../utils/validation';
import FeedbackModal from '../components/FeedbackModal';

const PaymentHistory = () => {
  const [payments, setPayments] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [currentPage, setCurrentPage] = useState(0);
  const [limit] = useState(20);
  const [hasMore, setHasMore] = useState(true);
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  const [selectedTransaction, setSelectedTransaction] = useState(null);

  const loadPaymentData = useCallback(async () => {
    try {
      setLoading(true);
      setError(''); // Clear previous errors
      
      // Load payment history and statistics in parallel
      const [historyResponse, statsResponse] = await Promise.all([
        paymentAPI.getPaymentHistory(limit, 0),
        paymentAPI.getPaymentStatistics()
      ]);

      setPayments(historyResponse.data.payments || []);
      setStatistics(statsResponse.data);
      setHasMore(historyResponse.data.has_more || false);
      setCurrentPage(0);
      
      // Debug logging
      console.log('Payment History Data:', historyResponse.data);
      console.log('Statistics Data:', statsResponse.data);
    } catch (err) {
      console.error('Payment API Error:', err);
      setError('Không thể tải lịch sử thanh toán: ' + (err.response?.data?.message || err.message));
      
      // Set empty states on error
      setPayments([]);
      setStatistics(null);
      setHasMore(false);
      setCurrentPage(0);
    } finally {
      setLoading(false);
    }
  }, [limit]);

  useEffect(() => {
    loadPaymentData();
  }, [loadPaymentData]);

  const loadMorePayments = async () => {
    if (loading || !hasMore) return;

    try {
      setLoading(true);
      const offset = (currentPage + 1) * limit;
      const response = await paymentAPI.getPaymentHistory(limit, offset);
      
      setPayments(prev => [...prev, ...(response.data.payments || [])]);
      setHasMore(response.data.has_more || false);
      setCurrentPage(prev => prev + 1);
    } catch (err) {
      setError('Không thể tải thêm dữ liệu: ' + (err.response?.data?.message || err.message));
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'success':
        return 'bg-green-100 text-green-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'cancelled':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status) => {
    console.log('Mapping status:', status); // Debug log
    switch (status?.toLowerCase()) {
      case 'success':
      case 'completed':
        return 'Thành công';
      case 'pending':
        return 'Đang xử lý';
      case 'failed':
        return 'Thất bại';
      case 'cancelled':
        return 'Đã hủy';
      default:
        return status || 'Không xác định';
    }
  };

  const getMethodText = (method) => {
    switch (method) {
      case 'Digital Wallet':
        return 'Ví điện tử';
      case 'Credit Card':
        return 'Thẻ tín dụng';
      case 'Bank Transfer':
        return 'Chuyển khoản';
      case 'Cash':
        return 'Tiền mặt';
      default:
        return method;
    }
  };

  const handleFeedbackClick = (payment) => {
    // Transform payment data to transaction format for FeedbackModal
    const transactionData = {
      transaction_id: payment.payment_id,
      ticket_name: payment.title,
      amount: payment.amount,
      created_at: payment.paid_at || payment.created_at,
      seller_id: payment.seller_id || payment.target_user_id,
      buyer_id: payment.buyer_id || payment.user_id,
      current_user_id: payment.user_id // Assuming current user ID
    };
    
    setSelectedTransaction(transactionData);
    console.log("Selected Transaction for Feedback:", transactionData);
    setShowFeedbackModal(true);
  };

  const handleFeedbackSubmitSuccess = (feedbackData) => {
    console.log('Feedback submitted successfully:', feedbackData);
    // Optionally update the payment list to show feedback has been given
    setPayments(prev => prev.map(payment => 
      payment.payment_id === selectedTransaction.transaction_id 
        ? { ...payment, feedback_given: true }
        : payment
    ));
  };

  const handleCloseFeedbackModal = () => {
    setShowFeedbackModal(false);
    setSelectedTransaction(null);
  };

  if (loading && payments.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Đang tải lịch sử thanh toán...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Lịch sử thanh toán</h1>
          <p className="text-gray-600">Quản lý và theo dõi các giao dịch thanh toán của bạn</p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-6 py-4 rounded-lg mb-8">
            <div className="flex items-center">
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{error}</span>
            </div>
            <p className="mt-2 text-sm">
              Có thể API Payment chưa được khởi động. Hãy đảm bảo rằng server Payment đang chạy trên port 5000.
            </p>
          </div>
        )}

        {/* Statistics */}
        {statistics && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center">
                <div className="p-3 bg-blue-100 rounded-full">
                  <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Tổng giao dịch</p>
                  <p className="text-2xl font-bold text-gray-900">{statistics.total_payments || 0}</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center">
                <div className="p-3 bg-green-100 rounded-full">
                  <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Thành công</p>
                  <p className="text-2xl font-bold text-gray-900">{statistics.successful_payments || 0}</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center">
                <div className="p-3 bg-yellow-100 rounded-full">
                  <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Đang xử lý</p>
                  <p className="text-2xl font-bold text-gray-900">{statistics.pending_payments || 0}</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center">
                <div className="p-3 bg-purple-100 rounded-full">
                  <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                  </svg>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Tổng số tiền</p>
                  <p className="text-2xl font-bold text-gray-900">{formatPrice(statistics.total_amount || 0)}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Success Rate */}
        {statistics && statistics.success_rate !== undefined && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Tỷ lệ thành công: {(statistics.success_rate || 0).toFixed(1)}%</h3>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-green-600 h-2 rounded-full" 
                style={{ width: `${statistics.success_rate || 0}%` }}
              ></div>
            </div>
            
            {/* Method Breakdown */}
            {statistics.method_breakdown && (
              <div className="mt-6">
                <h4 className="text-md font-medium text-gray-900 mb-3">Phân tích theo phương thức</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  {Object.entries(statistics.method_breakdown).map(([method, data]) => (
                    <div key={method} className="bg-gray-50 p-4 rounded-lg">
                      <p className="font-medium text-gray-900">{getMethodText(method)}</p>
                      <p className="text-sm text-gray-600">{data?.count || 0} giao dịch</p>
                      <p className="text-sm font-medium text-blue-600">{formatPrice(data?.amount || 0)}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Payment List */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Lịch sử giao dịch</h3>
          </div>

          {error && (
            <div className="m-6 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {payments.length === 0 ? (
            <div className="text-center py-12">
              <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Chưa có giao dịch nào</h3>
              <p className="text-gray-600">Bạn chưa thực hiện giao dịch thanh toán nào.</p>
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Mã thanh toán
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Tiêu đề
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Phương thức
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Số tiền
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Trạng thái
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Ngày thanh toán
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Thao tác
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {payments.map((payment) => (
                      <tr key={payment.payment_id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          #{payment.payment_id}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          <div className="max-w-xs truncate" title={payment.title}>
                            {payment.title}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {getMethodText(payment.methods)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {formatPrice(payment.amount)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(payment.status)}`}>
                            {getStatusText(payment.status)}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {payment.paid_at ? formatDate(payment.paid_at) : '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {/* Debug payment object */}
                          {console.log('Payment object:', payment)}
                          {console.log('Payment status:', payment.status)}
                          {console.log('Payment feedback_given:', payment.feedback_given)}
                          
                          {(payment.status?.toLowerCase() === 'completed' || 
                            payment.status?.toLowerCase() === 'success') && !payment.feedback_given ? (
                            <button
                              onClick={() => handleFeedbackClick(payment)}
                              className="inline-flex items-center px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium rounded-md transition-colors"
                            >
                              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                              </svg>
                              Đánh giá
                            </button>
                          ) : payment.feedback_given ? (
                            <span className="inline-flex items-center px-2 py-1 text-xs text-green-600 bg-green-100 rounded-md">
                              <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                              </svg>
                              Đã đánh giá
                            </span>
                          ) : (
                            <span className="text-gray-400 text-xs">
                              {payment.status ? `Status: ${payment.status}` : '-'}
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Load More Button */}
              {hasMore && (
                <div className="px-6 py-4 border-t border-gray-200 text-center">
                  <button
                    onClick={loadMorePayments}
                    disabled={loading}
                    className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white px-6 py-2 rounded-md text-sm font-medium transition-colors"
                  >
                    {loading ? (
                      <div className="flex items-center justify-center">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Đang tải...
                      </div>
                    ) : (
                      'Tải thêm'
                    )}
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Feedback Modal */}
      <FeedbackModal
        isOpen={showFeedbackModal}
        onClose={handleCloseFeedbackModal}
        transaction={selectedTransaction}
        onSubmitSuccess={handleFeedbackSubmitSuccess}
      />
    </div>
  );
};

export default PaymentHistory;
