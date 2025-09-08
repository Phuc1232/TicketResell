import React, { useState, useEffect, useCallback } from 'react';
import { transactionAPI } from '../services/transactionAPI';
import { formatPrice } from '../utils/validation';
import Button from './Button';
import Input from './Input';

const PurchaseModal = ({ ticket, onClose, onPurchaseSuccess }) => {
  const [step, setStep] = useState(1); // 1: Preview, 2: Payment, 3: Processing, 4: Success/Error
  const [preview, setPreview] = useState(null);
  const [paymentMethod, setPaymentMethod] = useState('');
  const [paymentData, setPaymentData] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [transaction, setTransaction] = useState(null);

  const loadTransactionPreview = useCallback(async () => {
    if (!ticket) return;
    
    try {
      setLoading(true);
      const response = await transactionAPI.previewTransaction(ticket.TicketID);
      setPreview(response.data);
      
      // Debug logging
      console.log('Transaction Preview:', response.data);
      console.log('Available Payment Methods:', response.data.available_payment_methods);
    } catch (err) {
      setError('Không thể tải thông tin giao dịch: ' + (err.response?.data?.message || err.message));
    } finally {
      setLoading(false);
    }
  }, [ticket]);

  useEffect(() => {
    loadTransactionPreview();
  }, [loadTransactionPreview]);

  const handlePaymentMethodChange = (method) => {
    // Normalize payment method names to match API requirements
    let normalizedMethod = method;
    if (method === 'Momo') {
      normalizedMethod = 'Digital Wallet'; // Convert Momo to Digital Wallet for API
    }
    
    setPaymentMethod(normalizedMethod);
    setPaymentData({});
    
    // Set wallet type for Digital Wallet/Momo
    if (method === 'Momo' || normalizedMethod === 'Digital Wallet') {
      setPaymentData({ wallet_type: 'momo' });
    }
  };

  const handlePaymentDataChange = (field, value) => {
    setPaymentData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handlePurchase = async () => {
    if (!paymentMethod) {
      setError('Vui lòng chọn phương thức thanh toán');
      return;
    }

    // Validate payment method
    const validPaymentMethods = ['Cash', 'Bank Transfer', 'Digital Wallet', 'Credit Card'];
    if (!validPaymentMethods.includes(paymentMethod)) {
      setError('Phương thức thanh toán không hợp lệ');
      return;
    }

    // Validate ticket ID
    if (!ticket?.TicketID || typeof ticket.TicketID !== 'number' || ticket.TicketID <= 0) {
      setError('ID vé không hợp lệ');
      return;
    }

    try {
      setLoading(true);
      setStep(3); // Processing

      const purchaseData = {
        ticketId: ticket.TicketID,
        paymentMethod: paymentMethod,
        paymentData: paymentData
      };

      // Debug logging
      console.log('Purchase Data:', purchaseData);
      console.log('Ticket:', ticket);
      console.log('Payment Method:', paymentMethod);

      const response = await transactionAPI.buyTicket(purchaseData);
      setTransaction(response.data);

      if (response.data.payment_url) {
        // Redirect to payment gateway
        window.open(response.data.payment_url, '_blank');
        setStep(3); // Keep in processing state
        // Poll for transaction status
        pollTransactionStatus(response.data.transaction_id);
      } else if (response.data.status === 'success') {
        // Payment completed immediately
        setStep(4);
        onPurchaseSuccess && onPurchaseSuccess(response.data);
      }
    } catch (err) {
      console.error('Purchase Error:', err);
      console.error('Error Response:', err.response?.data);
      
      let errorMessage = 'Lỗi thanh toán: ';
      
      if (err.response?.status === 400) {
        if (err.response.data?.errors) {
          // Validation errors
          const errors = Object.entries(err.response.data.errors)
            .map(([field, messages]) => `${field}: ${messages.join(', ')}`)
            .join('; ');
          errorMessage += `Lỗi validation - ${errors}`;
        } else if (err.response.data?.message) {
          errorMessage += err.response.data.message;
        } else {
          errorMessage += 'Dữ liệu không hợp lệ';
        }
      } else if (err.response?.status === 409) {
        errorMessage += 'Vé không có sẵn để mua hoặc đã được bán';
      } else if (err.response?.status === 404) {
        errorMessage += 'Không tìm thấy vé';
      } else {
        errorMessage += (err.response?.data?.message || err.message);
      }
      
      setError(errorMessage);
      setStep(2); // Back to payment step
    } finally {
      setLoading(false);
    }
  };

  const pollTransactionStatus = async (transactionId, attempts = 0) => {
    if (attempts >= 60) { // 5 minutes maximum polling
      setError('Timeout: Không thể xác nhận trạng thái thanh toán');
      setStep(2);
      return;
    }

    try {
      console.log(`Polling transaction status (attempt ${attempts + 1}):`, transactionId);
      const response = await transactionAPI.getTransactionStatus(transactionId);
      const status = response.data.status;
      
      console.log(`Transaction ${transactionId} status:`, status);
      console.log('Full response:', response.data);

      if (status === 'success') {
        console.log('Transaction successful, calling onPurchaseSuccess');
        setStep(4);
        onPurchaseSuccess && onPurchaseSuccess(response.data);
      } else if (status === 'failed') {
        console.log('Transaction failed');
        setError('Thanh toán thất bại');
        setStep(2);
      } else if (status === 'pending') {
        console.log('Transaction still pending, continue polling...');
        // Continue polling
        setTimeout(() => pollTransactionStatus(transactionId, attempts + 1), 5000);
      }
    } catch (err) {
      console.error('Error polling transaction status:', err);
      setTimeout(() => pollTransactionStatus(transactionId, attempts + 1), 5000);
    }
  };

  const renderPaymentMethodFields = () => {
    switch (paymentMethod) {
      case 'Digital Wallet':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Loại ví điện tử
              </label>
              <select
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={paymentData.wallet_type || ''}
                onChange={(e) => handlePaymentDataChange('wallet_type', e.target.value)}
              >
                <option value="">Chọn ví điện tử</option>
                <option value="momo">MoMo</option>
                <option value="zalopay">ZaloPay</option>
                <option value="viettelpay">ViettelPay</option>
              </select>
            </div>
            {paymentData.wallet_type === 'momo' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Ngân hàng liên kết (tùy chọn)
                </label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={paymentData.bank_code || ''}
                  onChange={(e) => handlePaymentDataChange('bank_code', e.target.value)}
                >
                  <option value="">Sử dụng số dư MoMo</option>
                  <option value="SACOMBANK">Sacombank</option>
                  <option value="VIETCOMBANK">Vietcombank</option>
                  <option value="TECHCOMBANK">Techcombank</option>
                  <option value="AGRIBANK">Agribank</option>
                </select>
              </div>
            )}
          </div>
        );

      case 'Credit Card':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Số thẻ
              </label>
              <Input
                type="text"
                placeholder="1234 5678 9012 3456"
                value={paymentData.card_number || ''}
                onChange={(e) => handlePaymentDataChange('card_number', e.target.value)}
                maxLength={19}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tháng hết hạn
                </label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={paymentData.expiry_month || ''}
                  onChange={(e) => handlePaymentDataChange('expiry_month', e.target.value)}
                >
                  <option value="">Tháng</option>
                  {Array.from({ length: 12 }, (_, i) => (
                    <option key={i + 1} value={String(i + 1).padStart(2, '0')}>
                      {String(i + 1).padStart(2, '0')}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Năm hết hạn
                </label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={paymentData.expiry_year || ''}
                  onChange={(e) => handlePaymentDataChange('expiry_year', e.target.value)}
                >
                  <option value="">Năm</option>
                  {Array.from({ length: 10 }, (_, i) => {
                    const year = new Date().getFullYear() + i;
                    return (
                      <option key={year} value={year}>
                        {year}
                      </option>
                    );
                  })}
                </select>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                CVV
              </label>
              <Input
                type="text"
                placeholder="123"
                value={paymentData.cvv || ''}
                onChange={(e) => handlePaymentDataChange('cvv', e.target.value)}
                maxLength={4}
              />
            </div>
          </div>
        );

      case 'Bank Transfer':
        return (
          <div className="space-y-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h4 className="font-medium text-blue-900 mb-2">Thông tin chuyển khoản</h4>
              <div className="text-sm text-blue-800 space-y-1">
                <p><strong>Số tài khoản:</strong> 1234567890</p>
                <p><strong>Tên tài khoản:</strong> TICKETRESELL PLATFORM</p>
                <p><strong>Ngân hàng:</strong> Vietcombank</p>
                <p><strong>Nội dung:</strong> TICKET_{ticket?.TicketID}</p>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Mã xác nhận giao dịch
              </label>
              <Input
                type="text"
                placeholder="Nhập mã giao dịch từ ngân hàng"
                value={paymentData.confirmation_code || ''}
                onChange={(e) => handlePaymentDataChange('confirmation_code', e.target.value)}
              />
            </div>
          </div>
        );

      case 'Cash':
        return (
          <div className="space-y-4">
            <div className="bg-green-50 p-4 rounded-lg">
              <h4 className="font-medium text-green-900 mb-2">Thanh toán tiền mặt</h4>
              <p className="text-sm text-green-800">
                Vui lòng liên hệ người bán để thỏa thuận địa điểm giao dịch và thanh toán trực tiếp.
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Mã xác nhận
              </label>
              <Input
                type="text"
                placeholder="Nhập mã xác nhận từ người bán"
                value={paymentData.confirmation_code || ''}
                onChange={(e) => handlePaymentDataChange('confirmation_code', e.target.value)}
              />
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  if (!ticket) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-screen overflow-y-auto">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b">
          <h2 className="text-xl font-bold text-gray-900">
            {step === 1 && 'Xác nhận mua vé'}
            {step === 2 && 'Chọn phương thức thanh toán'}
            {step === 3 && 'Đang xử lý thanh toán...'}
            {step === 4 && (transaction?.status === 'success' ? 'Thanh toán thành công!' : 'Thanh toán thất bại')}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
            disabled={step === 3}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="p-6">
          {/* Step 1: Preview */}
          {step === 1 && (
            <div className="space-y-6">
              {loading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  <span className="ml-2">Đang tải thông tin...</span>
                </div>
              ) : preview ? (
                <>
                  {/* Ticket Info */}
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="font-medium text-gray-900 mb-2">{preview.ticket.event_name}</h3>
                    <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
                      <div>
                        <span className="font-medium">Giá vé:</span>
                        <span className="ml-2">{formatPrice(preview.ticket.price)}</span>
                      </div>
                      <div>
                        <span className="font-medium">Ngày sự kiện:</span>
                        <span className="ml-2">{new Date(preview.ticket.event_date).toLocaleDateString('vi-VN')}</span>
                      </div>
                    </div>
                  </div>

                  {/* Earnings Breakdown */}
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <h4 className="font-medium text-blue-900 mb-3">Chi tiết thanh toán</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>Giá vé:</span>
                        <span>{formatPrice(preview.earnings_breakdown.transaction_amount)}</span>
                      </div>
                      <div className="flex justify-between text-gray-600">
                        <span>Phí hệ thống ({(preview.earnings_breakdown.platform_commission_rate * 100).toFixed(1)}%):</span>
                        <span>-{formatPrice(preview.earnings_breakdown.commission_amount)}</span>
                      </div>
                      <div className="border-t pt-2 flex justify-between font-medium">
                        <span>Tổng thanh toán:</span>
                        <span>{formatPrice(preview.earnings_breakdown.transaction_amount)}</span>
                      </div>
                      <div className="text-xs text-gray-500">
                        Người bán sẽ nhận: {formatPrice(preview.earnings_breakdown.seller_earnings)}
                      </div>
                    </div>
                  </div>

                  {error && (
                    <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                      {error}
                    </div>
                  )}

                  <div className="flex space-x-4">
                    <Button
                      onClick={onClose}
                      className="flex-1 bg-gray-500 hover:bg-gray-600"
                    >
                      Hủy
                    </Button>
                    <Button
                      onClick={() => setStep(2)}
                      className="flex-1"
                    >
                      Tiếp tục thanh toán
                    </Button>
                  </div>
                </>
              ) : null}
            </div>
          )}

          {/* Step 2: Payment Method */}
          {step === 2 && preview && (
            <div className="space-y-6">
              {/* Payment Methods */}
              <div>
                <h3 className="font-medium text-gray-900 mb-4">Chọn phương thức thanh toán</h3>
                <div className="space-y-3">
                  {(preview.available_payment_methods || ['Cash', 'Bank Transfer', 'Digital Wallet', 'Credit Card']).map((method) => (
                    <label key={method} className="flex items-center p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
                      <input
                        type="radio"
                        name="paymentMethod"
                        value={method}
                        checked={paymentMethod === (method === 'Momo' ? 'Digital Wallet' : method)}
                        onChange={(e) => handlePaymentMethodChange(e.target.value)}
                        className="mr-3"
                      />
                      <div className="flex-1">
                        <div className="font-medium">
                          {method === 'Digital Wallet' && 'Ví điện tử'}
                          {method === 'Credit Card' && 'Thẻ tín dụng'}
                          {method === 'Bank Transfer' && 'Chuyển khoản ngân hàng'}
                          {method === 'Cash' && 'Tiền mặt'}
                          {method === 'Momo' && 'MoMo'}
                        </div>
                        <div className="text-sm text-gray-500">
                          {method === 'Digital Wallet' && 'MoMo, ZaloPay, ViettelPay'}
                          {method === 'Credit Card' && 'Visa, MasterCard'}
                          {method === 'Bank Transfer' && 'Chuyển khoản qua ngân hàng'}
                          {method === 'Cash' && 'Thanh toán trực tiếp'}
                          {method === 'Momo' && 'Ví điện tử MoMo'}
                        </div>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              {/* Payment Method Fields */}
              {paymentMethod && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">Thông tin thanh toán</h4>
                  {renderPaymentMethodFields()}
                </div>
              )}

              {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                  {error}
                </div>
              )}

              <div className="flex space-x-4">
                <Button
                  onClick={() => setStep(1)}
                  className="flex-1 bg-gray-500 hover:bg-gray-600"
                >
                  Quay lại
                </Button>
                <Button
                  onClick={handlePurchase}
                  disabled={loading || !paymentMethod}
                  className="flex-1"
                >
                  {loading ? (
                    <div className="flex items-center justify-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Đang xử lý...
                    </div>
                  ) : (
                    `Thanh toán ${formatPrice(preview.earnings_breakdown.transaction_amount)}`
                  )}
                </Button>
              </div>
            </div>
          )}

          {/* Step 3: Processing */}
          {step === 3 && (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Đang xử lý thanh toán</h3>
              <p className="text-gray-600">
                {transaction?.payment_url 
                  ? 'Vui lòng hoàn tất thanh toán trên trang được mở. Chúng tôi sẽ tự động cập nhật kết quả.'
                  : 'Vui lòng đợi trong giây lát...'
                }
              </p>
              {error && (
                <div className="mt-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                  {error}
                </div>
              )}
            </div>
          )}

          {/* Step 4: Result */}
          {step === 4 && (
            <div className="text-center py-8">
              {transaction?.status === 'success' ? (
                <>
                  <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100 mb-4">
                    <svg className="h-8 w-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Thanh toán thành công!</h3>
                  <p className="text-gray-600 mb-4">
                    Bạn đã mua vé thành công. Vé sẽ được chuyển vào tài khoản của bạn.
                  </p>
                  <div className="bg-gray-50 p-4 rounded-lg text-left">
                    <h4 className="font-medium mb-2">Chi tiết giao dịch:</h4>
                    <div className="text-sm space-y-1">
                      <div>Mã giao dịch: {transaction.transaction_id}</div>
                      <div>Số tiền: {formatPrice(transaction.total_amount)}</div>
                      <div>Phí hệ thống: {formatPrice(transaction.commission_amount)}</div>
                    </div>
                  </div>
                </>
              ) : (
                <>
                  <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100 mb-4">
                    <svg className="h-8 w-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Thanh toán thất bại</h3>
                  <p className="text-gray-600 mb-4">
                    Đã xảy ra lỗi trong quá trình thanh toán. Vui lòng thử lại.
                  </p>
                </>
              )}

              {error && (
                <div className="mt-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                  {error}
                </div>
              )}

              <Button
                onClick={onClose}
                className="mt-6"
              >
                Đóng
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PurchaseModal;
