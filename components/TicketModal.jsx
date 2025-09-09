import React, { useState, useEffect } from 'react';
import Input from './Input';
import Button from './Button';
import { ticketAPI } from '../services/ticketAPI';
import { validateTicketForm, getErrorMessage } from '../utils/validation';

const TicketModal = ({ ticket, onClose, onSave }) => {
  const [formData, setFormData] = useState({
    EventName: '',
    EventDate: '',
    Price: '',
    Status: 'Available',
    PaymentMethod: '',
    ContactInfo: ''
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (ticket) {
      // Format date for input
      const eventDate = ticket.EventDate ? 
        new Date(ticket.EventDate).toISOString().slice(0, 16) : '';
      
      setFormData({
        EventName: ticket.EventName || '',
        EventDate: eventDate,
        Price: ticket.Price || '',
        Status: ticket.Status || 'Available',
        PaymentMethod: ticket.PaymentMethod || '',
        ContactInfo: ticket.ContactInfo || ''
      });
    }
  }, [ticket]);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Clear error for this field
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: ''
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validate form
    const validation = validateTicketForm(formData);
    if (!validation.isValid) {
      setErrors(validation.errors);
      return;
    }

    setLoading(true);

    try {
      // Format data for API
      const apiData = {
        EventName: formData.EventName,
        EventDate: new Date(formData.EventDate).toISOString(),
        Price: parseFloat(formData.Price),
        Status: formData.Status,
        PaymentMethod: formData.PaymentMethod,
        ContactInfo: formData.ContactInfo
      };

      let response;
      if (ticket) {
        // Update existing ticket
        response = await ticketAPI.updateTicket(ticket.TicketID, apiData);
      } else {
        // Create new ticket
        response = await ticketAPI.createTicket(apiData);
      }
      
      onSave(response.data);
    } catch (err) {
      setError(getErrorMessage(err));
      console.error('Save ticket error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-screen overflow-y-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 rounded-t-lg">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold">
              {ticket ? 'Chỉnh sửa vé' : 'Đăng vé mới'}
            </h2>
            <button
              onClick={onClose}
              className="text-white hover:text-gray-200"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6">
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          <div className="space-y-4">
            {/* Event Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Tên sự kiện *
              </label>
              <Input
                type="text"
                placeholder="Nhập tên sự kiện"
                value={formData.EventName}
                onChange={(e) => handleInputChange('EventName', e.target.value)}
                error={errors.EventName}
              />
            </div>

            {/* Event Date */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Ngày và giờ sự kiện *
              </label>
              <Input
                type="datetime-local"
                value={formData.EventDate}
                onChange={(e) => handleInputChange('EventDate', e.target.value)}
                error={errors.EventDate}
              />
            </div>

            {/* Price and Status */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Giá vé (VNĐ) *
                </label>
                <Input
                  type="number"
                  placeholder="0"
                  min="0"
                  value={formData.Price}
                  onChange={(e) => handleInputChange('Price', e.target.value)}
                  error={errors.Price}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Trạng thái *
                </label>
                <select
                  className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    errors.Status ? 'border-red-500' : 'border-gray-300'
                  }`}
                  value={formData.Status}
                  onChange={(e) => handleInputChange('Status', e.target.value)}
                >
                  <option value="Available">Có sẵn</option>
                  <option value="Sold">Đã bán</option>
                  <option value="Reserved">Đã đặt</option>
                  <option value="Cancelled">Đã hủy</option>
                </select>
                {errors.Status && (
                  <p className="text-red-500 text-sm mt-1">{errors.Status}</p>
                )}
              </div>
            </div>

            {/* Payment Method */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Phương thức thanh toán *
              </label>
              <select
                className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.PaymentMethod ? 'border-red-500' : 'border-gray-300'
                }`}
                value={formData.PaymentMethod}
                onChange={(e) => handleInputChange('PaymentMethod', e.target.value)}
              >
                <option value="">Chọn phương thức thanh toán</option>
                <option value="Cash">Tiền mặt</option>
                <option value="Bank Transfer">Chuyển khoản ngân hàng</option>
                <option value="Digital Wallet">Ví điện tử</option>
                <option value="Credit Card">Thẻ tín dụng</option>
              </select>
              {errors.PaymentMethod && (
                <p className="text-red-500 text-sm mt-1">{errors.PaymentMethod}</p>
              )}
            </div>

            {/* Contact Info */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Thông tin liên hệ *
              </label>
              <Input
                type="text"
                placeholder="Số điện thoại, email hoặc các thông tin liên hệ khác"
                value={formData.ContactInfo}
                onChange={(e) => handleInputChange('ContactInfo', e.target.value)}
                error={errors.ContactInfo}
              />
            </div>
          </div>

          {/* Buttons */}
          <div className="flex space-x-4 mt-6 pt-6 border-t border-gray-200">
            <Button
              type="button"
              variant="secondary"
              onClick={onClose}
              className="flex-1"
              disabled={loading}
            >
              Hủy
            </Button>
            <Button
              type="submit"
              className="flex-1"
              disabled={loading}
            >
              {loading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Đang lưu...
                </div>
              ) : (
                ticket ? 'Cập nhật' : 'Đăng vé'
              )}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default TicketModal;
