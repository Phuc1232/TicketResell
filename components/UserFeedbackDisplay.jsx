import React, { useState, useEffect } from 'react';
import { FiStar, FiUser } from 'react-icons/fi';
import { feedbackAPI } from '../services/feedbackAPI';
import { formatDate } from '../utils/validation';

const UserFeedbackDisplay = ({ userId, className = '' }) => {
  const [feedbackSummary, setFeedbackSummary] = useState(null);
  const [recentFeedback, setRecentFeedback] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadUserFeedback = async () => {
      if (!userId) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        
        // Load both summary and recent feedback
        const [summaryResponse, feedbackResponse] = await Promise.all([
          feedbackAPI.getUserFeedbackSummary(userId),
          feedbackAPI.getUserFeedback(userId, 5, 0) // Get latest 5 feedback
        ]);

        setFeedbackSummary(summaryResponse.data);
        setRecentFeedback(feedbackResponse.data.feedback || []);
        setError('');
        
      } catch (err) {
        console.error('Error loading user feedback:', err);
        setError('Không thể tải đánh giá người dùng');
        setFeedbackSummary(null);
        setRecentFeedback([]);
      } finally {
        setLoading(false);
      }
    };

    loadUserFeedback();
  }, [userId]);

  const renderStars = (rating) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;

    for (let i = 1; i <= 5; i++) {
      if (i <= fullStars) {
        stars.push(
          <FiStar key={i} className="w-4 h-4 text-yellow-400" fill="currentColor" />
        );
      } else if (i === fullStars + 1 && hasHalfStar) {
        stars.push(
          <div key={i} className="relative">
            <FiStar className="w-4 h-4 text-gray-300" />
            <div className="absolute inset-0 overflow-hidden w-1/2">
              <FiStar className="w-4 h-4 text-yellow-400" fill="currentColor" />
            </div>
          </div>
        );
      } else {
        stars.push(
          <FiStar key={i} className="w-4 h-4 text-gray-300" />
        );
      }
    }
    return stars;
  };

  if (loading) {
    return (
      <div className={`bg-gray-50 rounded-lg p-4 ${className}`}>
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/3 mb-2"></div>
          <div className="h-3 bg-gray-200 rounded w-1/2"></div>
        </div>
      </div>
    );
  }

  if (error || !feedbackSummary) {
    return (
      <div className={`bg-gray-50 rounded-lg p-4 ${className}`}>
        <div className="flex items-center text-gray-500">
          <FiUser className="w-5 h-5 mr-2" />
          <span className="text-sm">Chưa có đánh giá</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white border border-gray-200 rounded-lg p-4 ${className}`}>
      {/* Header với rating tổng */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center">
          <div className="flex items-center mr-2">
            {renderStars(feedbackSummary.average_rating || 0)}
          </div>
          <span className="text-sm font-medium text-gray-900">
            {feedbackSummary.average_rating?.toFixed(1) || '0.0'}
          </span>
        </div>
        <span className="text-xs text-gray-500">
          {feedbackSummary.total_feedback || 0} đánh giá
        </span>
      </div>

      {/* Reputation trend */}
      {feedbackSummary.feedback_trend && (
        <div className="mb-3">
          <span className={`text-xs px-2 py-1 rounded-full ${
            feedbackSummary.feedback_trend === 'improving' 
              ? 'bg-green-100 text-green-700' 
              : feedbackSummary.feedback_trend === 'declining'
              ? 'bg-red-100 text-red-700'
              : 'bg-gray-100 text-gray-700'
          }`}>
            {feedbackSummary.feedback_trend === 'improving' && '📈 Đang cải thiện'}
            {feedbackSummary.feedback_trend === 'declining' && '📉 Đang giảm'}
            {feedbackSummary.feedback_trend === 'neutral' && '➡️ Ổn định'}
          </span>
        </div>
      )}

      {/* Recent feedback */}
      {recentFeedback.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-gray-900">Đánh giá gần đây:</h4>
          {recentFeedback.slice(0, 3).map((feedback) => (
            <div key={feedback.feedback_id} className="bg-gray-50 rounded p-3">
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center">
                  {renderStars(feedback.rating)}
                  <span className="text-xs text-gray-600 ml-2">
                    {feedback.reviewer_name}
                  </span>
                </div>
                <span className="text-xs text-gray-500">
                  {formatDate(feedback.submitted_at)}
                </span>
              </div>
              {feedback.comment && (
                <p className="text-sm text-gray-700 mt-1 line-clamp-2">
                  {feedback.comment}
                </p>
              )}
            </div>
          ))}
          
          {recentFeedback.length > 3 && (
            <p className="text-xs text-gray-500 text-center">
              +{recentFeedback.length - 3} đánh giá khác
            </p>
          )}
        </div>
      )}

      {/* Rating distribution */}
      {feedbackSummary.rating_distribution && (
        <div className="mt-3 pt-3 border-t border-gray-100">
          <div className="grid grid-cols-5 gap-1">
            {[5, 4, 3, 2, 1].map((star) => (
              <div key={star} className="text-center">
                <div className="text-xs text-gray-500">{star}★</div>
                <div className="h-1 bg-gray-200 rounded">
                  <div 
                    className="h-1 bg-yellow-400 rounded"
                    style={{ 
                      width: `${feedbackSummary.total_feedback > 0 
                        ? (feedbackSummary.rating_distribution[star] || 0) / feedbackSummary.total_feedback * 100 
                        : 0}%` 
                    }}
                  ></div>
                </div>
                <div className="text-xs text-gray-400">
                  {feedbackSummary.rating_distribution[star] || 0}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default UserFeedbackDisplay;
