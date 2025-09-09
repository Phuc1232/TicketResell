import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { ticketAPI } from '../services/ticketAPI';
import TicketCard from '../components/TicketCard';
import TicketModal from '../components/TicketModal';
import PurchaseModal from '../components/PurchaseModal';
import SearchFilter from '../components/SearchFilter';
import { useNavigate } from 'react-router-dom';

const Homepage = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingTicket, setEditingTicket] = useState(null);
  const [showPurchaseModal, setShowPurchaseModal] = useState(false);
  const [purchasingTicket, setPurchasingTicket] = useState(null);
  const [searchParams, setSearchParams] = useState({
    search: '',
    eventType: '',
    minPrice: '',
    maxPrice: '',
    location: '',
    ticketType: '',
    isNegotiable: ''
  });

  useEffect(() => {
    loadTickets();
  }, []);

  const loadTickets = async () => {
    try {
      setLoading(true);
      const response = await ticketAPI.getAllTickets();
      console.log('Loaded tickets:', response.data);
      setTickets(response.data || []);
    } catch (err) {
      setError('Không thể tải danh sách vé');
      setTickets([]); // Ensure tickets is always an array
      console.error('Error loading tickets:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchParams.search.trim()) {
      loadTickets(); // Load all tickets if search is empty
      return;
    }
    
    try {
      setLoading(true);
      const response = await ticketAPI.searchTickets(searchParams.search);
      setTickets(response.data || []);
    } catch (err) {
      setError('Không thể tìm kiếm vé');
      setTickets([]); // Ensure tickets is always an array
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAdvancedSearch = async () => {
    try {
      setLoading(true);
      const params = {
        event_name: searchParams.search,
        event_type: searchParams.eventType,
        min_price: searchParams.minPrice,
        max_price: searchParams.maxPrice,
        location: searchParams.location,
        ticket_type: searchParams.ticketType,
        is_negotiable: searchParams.isNegotiable
      };
      const response = await ticketAPI.advancedSearch(params);
      setTickets(response.data || []);
    } catch (err) {
      setError('Không thể tìm kiếm vé');
      setTickets([]); // Ensure tickets is always an array
      console.error('Advanced search error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTicket = () => {
    setEditingTicket(null);
    setShowModal(true);
  };

  const handleEditTicket = (ticket) => {
    setEditingTicket(ticket);
    setShowModal(true);
  };

  const handleDeleteTicket = async (ticket) => {
    if (!window.confirm('Bạn có chắc chắn muốn xóa vé này?')) {
      return;
    }

    try {
      // We need EventName and owner username for the API call
      // Since we don't have owner username in ticket object, we use current user's username
      await ticketAPI.deleteTicket(ticket.EventName, user.username);
      setTickets((tickets || []).filter(t => t.TicketID !== ticket.TicketID));
    } catch (err) {
      setError('Không thể xóa vé');
      console.error('Delete error:', err);
    }
  };

  const handleTicketSaved = (savedTicket) => {
    if (editingTicket) {
      // Update existing ticket
      setTickets((tickets || []).map(ticket => 
        ticket.TicketID === savedTicket.TicketID ? savedTicket : ticket
      ));
    } else {
      // Add new ticket
      setTickets([savedTicket, ...(tickets || [])]);
    }
    setShowModal(false);
    setEditingTicket(null);
  };

  const handlePurchaseTicket = (ticket) => {
    setPurchasingTicket(ticket);
    setShowPurchaseModal(true);
  };

  const handlePurchaseSuccess = (purchaseData) => {
    setShowPurchaseModal(false);
    setPurchasingTicket(null);
    
    // Show success message
    alert(`Mua vé thành công! Mã giao dịch: ${purchaseData.transaction_id}`);
    
    // Delay reload to allow backend to complete status update
    setTimeout(() => {
      loadTickets();
    }, 2000); // Wait 2 seconds before reloading
  };

  const handlePurchaseClose = () => {
    setShowPurchaseModal(false);
    setPurchasingTicket(null);
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const resetSearch = () => {
    setSearchParams({
      search: '',
      eventType: '',
      minPrice: '',
      maxPrice: '',
      location: '',
      ticketType: '',
      isNegotiable: ''
    });
    loadTickets();
  };

  if (loading && tickets.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Đang tải...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Sàn Giao Dịch Vé
              </h1>
              <p className="text-gray-600">Chào mừng, {user?.username}</p>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={handleCreateTicket}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-colors"
              >
                Đăng Vé Mới
              </button>
              <button
                onClick={() => navigate('/payments')}
                className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-2 rounded-lg font-medium transition-colors"
              >
                Lịch sử thanh toán
              </button>
              <button
                onClick={() => navigate('/profile')}
                className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg font-medium transition-colors"
              >
                Hồ sơ cá nhân
              </button>
              <button
                onClick={() => navigate('/chat')}
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-lg font-medium transition-colors"
              >
                💬 Chat
              </button>
              {/* Admin Dashboard Button - Only show for admins */}
              {user?.role_id === 1 && (
                <button
                  onClick={() => navigate('/admin')}
                  className="bg-orange-600 hover:bg-orange-700 text-white px-6 py-2 rounded-lg font-medium transition-colors"
                >
                  Quản Trị
                </button>
              )}
              <button
                onClick={handleLogout}
                className="bg-gray-600 hover:bg-gray-700 text-white px-6 py-2 rounded-lg font-medium transition-colors"
              >
                Đăng Xuất
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Search and Filter */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <SearchFilter
          searchParams={searchParams}
          setSearchParams={setSearchParams}
          onSearch={handleSearch}
          onAdvancedSearch={handleAdvancedSearch}
          onReset={resetSearch}
          loading={loading}
        />
      </div>

      {/* Error Message */}
      {error && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-6">
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        </div>
      )}

      {/* Tickets Grid */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-12">
        {!tickets || tickets.length === 0 ? (
          <div className="text-center py-12">
            <div className="bg-white rounded-lg shadow-md p-8 max-w-md mx-auto">
              <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
              </svg>
              <h3 className="text-xl font-medium text-gray-900 mb-2">
                Chưa có vé nào
              </h3>
              <p className="text-gray-600 mb-4">
                Hãy bắt đầu bằng cách đăng vé đầu tiên của bạn
              </p>
              <button
                onClick={handleCreateTicket}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-colors"
              >
                Đăng Vé Mới
              </button>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {tickets && tickets.map((ticket) => (
              <TicketCard
                key={ticket.TicketID}
                ticket={ticket}
                onEdit={handleEditTicket}
                onDelete={handleDeleteTicket}
                onPurchase={handlePurchaseTicket}
                currentUser={user}
              />
            ))}
          </div>
        )}
      </div>

      {/* Ticket Modal */}
      {showModal && (
        <TicketModal
          ticket={editingTicket}
          onClose={() => {
            setShowModal(false);
            setEditingTicket(null);
          }}
          onSave={handleTicketSaved}
        />
      )}

      {/* Purchase Modal */}
      {showPurchaseModal && (
        <PurchaseModal
          ticket={purchasingTicket}
          onClose={handlePurchaseClose}
          onPurchaseSuccess={handlePurchaseSuccess}
        />
      )}
    </div>
  );
};

export default Homepage;
