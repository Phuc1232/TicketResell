import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ticketAPI } from '../services/ticketAPI';
import { chatAPI } from '../services/chatAPI';
import { useAuth } from '../context/AuthContext';
import { formatPrice, formatDate } from '../utils/validation';

const TicketDetail = () => {
  const { ticketId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [ticket, setTicket] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [showChatModal, setShowChatModal] = useState(false);
  const [chatMessage, setChatMessage] = useState('');
  const [isSendingMessage, setIsSendingMessage] = useState(false);

  useEffect(() => {
    const loadTicketDetail = async () => {
      try {
        setIsLoading(true);
        setError('');
        console.log('Loading ticket detail for ID:', ticketId);
        
        // Check if ticketId is valid
        if (!ticketId) {
          throw new Error('Ticket ID không hợp lệ');
        }
        
        const response = await ticketAPI.getTicketById(ticketId);
        console.log('Ticket detail response:', response);
        
        if (response && response.data) {
          setTicket(response.data);
        } else {
          throw new Error('Không tìm thấy thông tin vé');
        }
      } catch (error) {
        console.error('Error loading ticket detail:', error);
        setError(error.message || 'Không thể tải thông tin vé');
      } finally {
        setIsLoading(false);
      }
    };

    if (ticketId) {
      loadTicketDetail();
    }
  }, [ticketId]);

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Đang tải thông tin vé...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-center">
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                <h2 className="font-bold text-lg mb-2">Lỗi</h2>
                <p>{error}</p>
              </div>
              <button
                onClick={() => navigate('/homepage')}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-md transition-colors"
              >
                ← Quay về trang chủ
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // No ticket found
  if (!ticket) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-center">
              <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded mb-4">
                <h2 className="font-bold text-lg mb-2">Không tìm thấy vé</h2>
                <p>Vé với ID {ticketId} không tồn tại hoặc đã bị xóa.</p>
              </div>
              <button
                onClick={() => navigate('/homepage')}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-md transition-colors"
              >
                ← Quay về trang chủ
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const handleStartChat = () => {
    if (!ticket || !user || ticket.OwnerID === user.id) {
      return;
    }
    
    // Navigate to chat page with parameters
    const chatUrl = `/chat?ticketId=${ticket.TicketID}&receiverId=${ticket.OwnerID}&ticketName=${encodeURIComponent(ticket.EventName)}`;
    navigate(chatUrl);
  };

  const handleSendMessage = async () => {
    if (!chatMessage.trim() || !ticket) {
      alert('Vui lòng nhập tin nhắn');
      return;
    }

    try {
      setIsSendingMessage(true);
      
      const messageData = {
        content: chatMessage.trim(),
        receiver_id: ticket.OwnerID,
        ticket_id: ticket.TicketID
      };

      await chatAPI.sendMessage(messageData);
      
      setShowChatModal(false);
      setChatMessage('');
      
      // Chuyển đến trang chat
      navigate('/chat');
      
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Không thể gửi tin nhắn. Vui lòng thử lại.');
    } finally {
      setIsSendingMessage(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'available':
        return 'bg-green-100 text-green-800';
      case 'sold':
        return 'bg-red-100 text-red-800';
      case 'reserved':
        return 'bg-yellow-100 text-yellow-800';
      case 'cancelled':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status) => {
    switch (status?.toLowerCase()) {
      case 'available':
        return 'Còn bán';
      case 'sold':
        return 'Đã bán';
      case 'reserved':
        return 'Đã đặt';
      case 'cancelled':
        return 'Đã hủy';
      default:
        return status || 'Không rõ';
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (error || !ticket) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Không tìm thấy vé</h2>
          <p className="text-gray-600 mb-4">{error || 'Vé không tồn tại hoặc đã bị xóa'}</p>
          <button
            onClick={() => navigate('/homepage')}
            className="bg-indigo-600 text-white px-6 py-2 rounded-md hover:bg-indigo-700"
          >
            Về trang chủ
          </button>
        </div>
      </div>
    );
  }

  const isOwner = user && (
    ticket.OwnerID === user.id || 
    String(ticket.OwnerID) === String(user.id) ||
    Number(ticket.OwnerID) === Number(user.id)
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center text-gray-600 hover:text-gray-900 mb-4"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Quay lại
          </button>
          <h1 className="text-3xl font-bold text-gray-900">Chi tiết vé</h1>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          {/* Ticket Header */}
          <div className="p-6 bg-gradient-to-r from-indigo-500 to-purple-600 text-white">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold mb-2">{ticket.EventName}</h2>
                <p className="text-indigo-100">Vé #{ticket.TicketID}</p>
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold">
                  {formatPrice(ticket.Price)}
                </div>
                <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(ticket.Status)}`}>
                  {getStatusText(ticket.Status)}
                </span>
              </div>
            </div>
          </div>

          {/* Ticket Details */}
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Left Column */}
              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Thông tin sự kiện</h3>
                  
                  <div className="space-y-3">
                    <div className="flex items-center">
                      <svg className="w-5 h-5 text-gray-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      <div>
                        <p className="text-sm text-gray-500">Ngày diễn ra</p>
                        <p className="font-medium text-gray-900">
                          {formatDate(ticket.EventDate)}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center">
                      <svg className="w-5 h-5 text-gray-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                      </svg>
                      <div>
                        <p className="text-sm text-gray-500">Giá vé</p>
                        <p className="font-medium text-gray-900">
                          {formatPrice(ticket.Price)}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center">
                      <svg className="w-5 h-5 text-gray-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <div>
                        <p className="text-sm text-gray-500">Trạng thái</p>
                        <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(ticket.Status)}`}>
                          {getStatusText(ticket.Status)}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Right Column */}
              <div className="space-y-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Thông tin thanh toán</h3>
                  
                  <div className="space-y-3">
                    <div className="flex items-center">
                      <svg className="w-5 h-5 text-gray-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                      </svg>
                      <div>
                        <p className="text-sm text-gray-500">Phương thức thanh toán</p>
                        <p className="font-medium text-gray-900">
                          {ticket.PaymentMethod || 'Chưa xác định'}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center">
                      <svg className="w-5 h-5 text-gray-400 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                      <div>
                        <p className="text-sm text-gray-500">Thông tin liên hệ</p>
                        <p className="font-medium text-gray-900">
                          {ticket.ContactInfo || 'Chưa có thông tin'}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="mt-8 pt-6 border-t border-gray-200">
              {isOwner ? (
                <div className="flex space-x-4">
                  <button
                    onClick={() => navigate(`/tickets/${ticket.TicketID}/edit`)}
                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-3 px-6 rounded-md font-medium transition-colors"
                  >
                    Chỉnh sửa vé
                  </button>
                  <button
                    onClick={() => {
                      if (confirm('Bạn có chắc muốn xóa vé này?')) {
                        // Handle delete logic here
                        console.log('Delete ticket:', ticket.TicketID);
                      }
                    }}
                    className="flex-1 bg-red-600 hover:bg-red-700 text-white py-3 px-6 rounded-md font-medium transition-colors"
                  >
                    Xóa vé
                  </button>
                </div>
              ) : (
                user && ticket.Status?.toLowerCase() === 'available' && (
                  <div className="space-y-4">
                    <div className="flex space-x-4">
                      <button
                        onClick={() => {
                          // Handle purchase logic here
                          console.log('Purchase ticket:', ticket.TicketID);
                        }}
                        className="flex-1 bg-green-600 hover:bg-green-700 text-white py-3 px-6 rounded-md font-medium transition-colors"
                      >
                        💳 Mua vé - {formatPrice(ticket.Price)}
                      </button>
                      <button
                        onClick={handleStartChat}
                        className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white py-3 px-6 rounded-md font-medium transition-colors"
                      >
                        💬 Nhắn tin với người bán
                      </button>
                    </div>
                    
                    <div className="text-center">
                      <p className="text-sm text-gray-500">
                        💡 Hãy nhắn tin để thỏa thuận chi tiết trước khi mua
                      </p>
                    </div>
                  </div>
                )
              )}

              {!user && (
                <div className="text-center">
                  <p className="text-gray-600 mb-4">Vui lòng đăng nhập để mua vé hoặc liên hệ người bán</p>
                  <button
                    onClick={() => navigate('/login')}
                    className="bg-indigo-600 hover:bg-indigo-700 text-white py-2 px-6 rounded-md font-medium transition-colors"
                  >
                    Đăng nhập
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Chat Modal */}
      {showChatModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg w-full max-w-md mx-4">
            <div className="p-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">
                  Nhắn tin với người bán
                </h3>
                <button
                  onClick={() => setShowChatModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            <div className="p-4">
              <div className="mb-4">
                <p className="text-sm text-gray-600 mb-2">
                  Vé: <strong>{ticket.EventName}</strong>
                </p>
                <p className="text-sm text-gray-600">
                  Giá: <strong>{formatPrice(ticket.Price)}</strong>
                </p>
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tin nhắn của bạn:
                </label>
                <textarea
                  value={chatMessage}
                  onChange={(e) => setChatMessage(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                  rows="4"
                  maxLength={1000}
                  placeholder="Nhập tin nhắn để liên hệ với người bán..."
                />
                <div className="text-xs text-gray-500 mt-1">
                  {chatMessage.length}/1000 ký tự
                </div>
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => setShowChatModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  Hủy
                </button>
                <button
                  onClick={handleSendMessage}
                  disabled={!chatMessage.trim() || isSendingMessage}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSendingMessage ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Đang gửi...
                    </>
                  ) : (
                    'Gửi tin nhắn'
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TicketDetail;
