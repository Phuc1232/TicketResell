import React, { useState } from 'react';
import { FiStar, FiX } from 'react-icons/fi';
import { feedbackAPI } from '../services/feedbackAPI';

const FeedbackModal = ({ isOpen, onClose, transaction, onSubmitSuccess }) => {
  const [rating, setRating] = useState(0);
  const [hoveredRating, setHoveredRating] = useState(0);
  const [comment, setComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen || !transaction) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (rating === 0) {
      setError('Vui lòng chọn số sao đánh giá');
      return;
    }

    try {
      setIsSubmitting(true);
      setError('');

      const feedbackData = {
        rating: rating,
        comment: comment.trim(),
        transaction_id: transaction.transaction_id
      };

      // Determine who to give feedback to (seller or buyer)
      const targetUserId = transaction.seller_id === transaction.current_user_id 
        ? transaction.buyer_id 
        : transaction.seller_id;

      const response = await feedbackAPI.submitUserFeedback(targetUserId, feedbackData);
      
      console.log('Feedback submitted:', response.data);
      onSubmitSuccess && onSubmitSuccess(response.data);
      onClose();
      
      // Reset form
      setRating(0);
      setHoveredRating(0);
      setComment('');
      
    } catch (err) {
      console.error('Error submitting feedback:', err);
      const errorMessage = err.response?.data?.message || err.message || 'Có lỗi xảy ra khi gửi đánh giá';
      setError(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleStarClick = (starValue) => {
    setRating(starValue);
  };

  const handleStarHover = (starValue) => {
    setHoveredRating(starValue);
  };

  const handleStarLeave = () => {
    setHoveredRating(0);
  };

  const renderStars = () => {
    const stars = [];
    for (let i = 1; i <= 5; i++) {
      const isFilled = i <= (hoveredRating || rating);
      stars.push(
        <button
          key={i}
          type="button"
          onClick={() => handleStarClick(i)}
          onMouseEnter={() => handleStarHover(i)}
          onMouseLeave={handleStarLeave}
          className={`p-1 transition-colors duration-200 ${
            isFilled ? 'text-yellow-400' : 'text-gray-300 hover:text-yellow-300'
          }`}
        >
          <FiStar className="w-8 h-8" fill={isFilled ? 'currentColor' : 'none'} />
        </button>
      );
    }
    return stars;
  };

  const getRatingText = () => {
    const currentRating = hoveredRating || rating;
    switch (currentRating) {
      case 1: return 'Rất tệ';
      case 2: return 'Tệ';
      case 3: return 'Bình thường';
      case 4: return 'Tốt';
      case 5: return 'Xuất sắc';
      default: return 'Chọn số sao';
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">
            Đánh giá giao dịch
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <FiX className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="p-6">
          {/* Transaction Info */}
          <div className="mb-6 p-4 bg-gray-50 rounded-lg">
            <h3 className="font-medium text-gray-900 mb-2">Thông tin giao dịch</h3>
            <p className="text-sm text-gray-600">
              <span className="font-medium">Vé:</span> {transaction.ticket_name || 'N/A'}
            </p>
            <p className="text-sm text-gray-600">
              <span className="font-medium">Số tiền:</span> {transaction.amount?.toLocaleString() || 0} VNĐ
            </p>
            {/* <p className="text-sm text-gray-600">
              <span className="font-medium">Ngày:</span> {new Date(transaction.created_at).toLocaleDateString('vi-VN')}
            </p> */}
          </div>

          {/* Rating */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Đánh giá của bạn *
            </label>
            <div className="flex items-center gap-1 mb-2">
              {renderStars()}
            </div>
            <p className="text-sm text-gray-600">
              {getRatingText()}
            </p>
          </div>

          {/* Comment */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nhận xét (tùy chọn)
            </label>
            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              rows={4}
              maxLength={500}
              placeholder="Chia sẻ trải nghiệm của bạn về giao dịch này..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            />
            <div className="text-right text-xs text-gray-500 mt-1">
              {comment.length}/500 ký tự
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          {/* Submit Button */}
          <div className="flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Hủy
            </button>
            <button
              type="submit"
              disabled={isSubmitting || rating === 0}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 
                       disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              {isSubmitting ? 'Đang gửi...' : 'Gửi đánh giá'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default FeedbackModal;
