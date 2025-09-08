import { useNavigate } from 'react-router-dom';
import { formatPrice, formatDate } from '../utils/validation';

const TicketCard = ({ ticket, onEdit, onDelete, onPurchase, currentUser }) => {
  const navigate = useNavigate();
  
  // Type-safe ownership check
  const isOwner = currentUser && (
    ticket.OwnerID === currentUser.id || 
    String(ticket.OwnerID) === String(currentUser.id) ||
    Number(ticket.OwnerID) === Number(currentUser.id)
  );
  
  // Debug logging
  console.log('TicketCard Debug:', {
    eventName: ticket.EventName,
    ticketID: ticket.TicketID,
    ownerID: ticket.OwnerID,
    ownerIDType: typeof ticket.OwnerID,
    currentUser: currentUser,
    currentUserID: currentUser?.id,
    currentUserIDType: typeof currentUser?.id,
    isOwner: isOwner,
    comparison: `${ticket.OwnerID} === ${currentUser?.id}`,
    stringComparison: `"${ticket.OwnerID}" === "${currentUser?.id}"`,
    numberComparison: `${Number(ticket.OwnerID)} === ${Number(currentUser?.id)}`
  });

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
        return 'Có sẵn';
      case 'sold':
        return 'Đã bán';
      case 'reserved':
        return 'Đã đặt';
      case 'cancelled':
        return 'Đã hủy';
      default:
        return status;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300 overflow-hidden">
      {/* Event Name Header */}
      <div 
        className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 cursor-pointer hover:from-blue-700 hover:to-purple-700 transition-colors"
        onClick={(e) => {
          e.preventDefault();
          e.stopPropagation();
          console.log('Clicking ticket card:', ticket.TicketID);
          console.log('Navigating to:', `/tickets/${ticket.TicketID}`);
          navigate(`/tickets/${ticket.TicketID}`);
        }}
      >
        <h3 className="text-lg font-semibold truncate pointer-events-none" title={ticket.EventName}>
          {ticket.EventName}
        </h3>
        <div className="flex justify-between items-center mt-2 pointer-events-none">
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(ticket.Status)}`}>
            {getStatusText(ticket.Status)}
          </span>
          <span className="text-white text-lg font-bold">
            {formatPrice(ticket.Price)}
          </span>
        </div>
        <div className="mt-2 text-xs text-blue-100 pointer-events-none">
          👆 Click để xem chi tiết
        </div>
      </div>

      {/* Event Details */}
      <div className="p-4">
        <div className="space-y-3">
          {/* Event Date */}
          <div className="flex items-center text-sm text-gray-600">
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <span>{formatDate(ticket.EventDate)}</span>
          </div>

          {/* Location */}
          {ticket.Location && (
            <div className="flex items-center text-sm text-gray-600">
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <span className="truncate">{ticket.Location}</span>
            </div>
          )}

          {/* Payment Method */}
          <div className="flex items-center text-sm text-gray-600">
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
            </svg>
            <span>{ticket.PaymentMethod}</span>
          </div>

          {/* Contact Info */}
          <div className="flex items-start text-sm text-gray-600">
            <svg className="w-4 h-4 mr-2 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
            </svg>
            <span className="break-words">{ticket.ContactInfo}</span>
          </div>

          {/* Description */}
          {ticket.Description && (
            <div className="text-sm text-gray-700 bg-gray-50 p-3 rounded-md">
              <p className="line-clamp-3">{ticket.Description}</p>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        {isOwner ? (
          <div className="flex space-x-2 mt-4 pt-4 border-t border-gray-200">
            <button
              onClick={() => onEdit(ticket)}
              className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md text-sm font-medium transition-colors"
            >
              Chỉnh sửa
            </button>
            <button
              onClick={() => onDelete(ticket)}
              className="flex-1 bg-red-600 hover:bg-red-700 text-white py-2 px-4 rounded-md text-sm font-medium transition-colors"
            >
              Xóa
            </button>
          </div>
        ) : (
          // Purchase and chat buttons for non-owners
          currentUser && ticket.Status?.toLowerCase() === 'available' && (
            <div className="mt-4 pt-4 border-t border-gray-200 space-y-2">
              <button
                onClick={() => onPurchase(ticket)}
                className="w-full bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded-md text-sm font-medium transition-colors"
              >
                Mua vé - {formatPrice(ticket.Price)}
              </button>
              
            </div>
          )
        )}

        
        
      </div>
    </div>
  );
};

export default TicketCard;
