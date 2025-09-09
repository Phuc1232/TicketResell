import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { chatAPI } from '../services/chatAPI';
import { formatDate } from '../utils/validation';

const Chat = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [searchParams] = useSearchParams();
  const messagesEndRef = useRef(null);
  
  // Get parameters from URL
  const ticketId = searchParams.get('ticketId');
  const receiverId = searchParams.get('receiverId');
  const ticketName = searchParams.get('ticketName');
  
  const [conversations, setConversations] = useState([]);
  const [currentConversation, setCurrentConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isSending, setIsSending] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [error, setError] = useState('');

  const loadReceiverInfo = useCallback(async (userId) => {
    try {
      // Try to get user info by ID (we might need to modify API to support this)
      console.log('Loading receiver info for user ID:', userId);
      
      // For now, we'll create the conversation with basic info
      // Later we can enhance this with actual user profile lookup
      setCurrentConversation({
        id: `new_${ticketId}_${userId}`,
        ticket_id: parseInt(ticketId),
        receiver_id: parseInt(userId),
        ticket_name: decodeURIComponent(ticketName || 'Vé'),
        other_user_name: `User #${userId}`, // We'll improve this
        isNew: true
      });
      
      setNewMessage(`Xin chào! Tôi quan tâm đến vé "${decodeURIComponent(ticketName || 'này')}" của bạn. Vé này vẫn còn bán không?`);
      
    } catch (error) {
      console.error('Error loading receiver info:', error);
      // Fallback to basic info
      setCurrentConversation({
        id: `new_${ticketId}_${userId}`,
        ticket_id: parseInt(ticketId),
        receiver_id: parseInt(userId),
        ticket_name: decodeURIComponent(ticketName || 'Vé'),
        other_user_name: 'Người bán',
        isNew: true
      });
      setNewMessage(`Xin chào! Tôi quan tâm đến vé "${decodeURIComponent(ticketName || 'này')}" của bạn. Vé này vẫn còn bán không?`);
    }
  }, [ticketId, ticketName]);

  useEffect(() => {
    if (user) {
      loadConversations();
    }
  }, [user]);

  useEffect(() => {
    if (currentConversation && !currentConversation.isNew && user) {
      // For existing conversations, load messages using other_user_id
      const otherUserId = currentConversation.other_user_id || currentConversation.receiver_id;
      console.log('Loading messages for conversation:', currentConversation);
      console.log('Other user ID:', otherUserId);
      
      if (otherUserId && otherUserId !== user.id) {
        loadMessages(otherUserId);
      }
    } else if (currentConversation && currentConversation.isNew) {
      // For new conversations, clear messages but still show the conversation
      console.log('New conversation detected, clearing messages');
      setMessages([]);
    }
  }, [currentConversation, user]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Auto-create conversation if parameters are provided
  useEffect(() => {
    if (ticketId && receiverId && user) {
      // Set up new conversation context and load receiver info
      loadReceiverInfo(receiverId);
    }
  }, [ticketId, receiverId, ticketName, user, loadReceiverInfo]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadConversations = async () => {
    try {
      setIsLoading(true);
      const response = await chatAPI.getConversations();
      console.log('Conversations loaded:', response.data);
      
      // Handle the API response structure
      const conversationsData = response.data?.conversations || response.data || [];
      console.log('Processing conversations data:', conversationsData);
      
      if (Array.isArray(conversationsData)) {
        // Transform the API data to match our component expectations
        const transformedConversations = conversationsData.map((conv, index) => ({
          id: conv.conversation_id || conv.user_id || `conv_${index}`,
          ticket_id: conv.ticket_id || null,
          ticket_name: conv.ticket_name || 'Vé không xác định',
          other_user_id: conv.user_id,
          other_user_name: conv.username || `User #${conv.user_id}`,
          last_message: conv.last_message || '',
          last_message_time: conv.last_message_time || new Date().toISOString(),
          unread_count: conv.unread_count || 0,
          receiver_id: conv.user_id // For compatibility
        }));
        
        console.log('Transformed conversations:', transformedConversations);
        
        // Sort conversations by last message time (most recent first for conversation list)
        const sortedConversations = transformedConversations.sort((a, b) => {
          const timeA = new Date(a.last_message_time);
          const timeB = new Date(b.last_message_time);
          return timeB - timeA; // Descending order (most recent first) for conversation list
        });
        
        setConversations(sortedConversations);
        setError(''); // Clear any previous errors
      } else {
        console.warn('Conversations data is not an array:', conversationsData);
        setConversations([]);
      }
    } catch (error) {
      console.error('Error loading conversations:', error);
      setError(`Không thể tải cuộc trò chuyện: ${error.response?.data?.message || error.message}`);
      setConversations([]);
    } finally {
      setIsLoading(false);
    }
  };

  const loadMessages = async (otherUserId) => {
    // Don't try to load messages for new conversations or invalid user IDs
    if (!otherUserId || otherUserId.toString().startsWith('new_')) {
      console.log('Skipping message load for invalid user ID:', otherUserId);
      setMessages([]);
      return;
    }
    
    try {
      console.log('Loading messages between current user and user ID:', otherUserId);
      console.log('API URL will be:', `http://localhost:6868/api/chat/messages?other_user_id=${otherUserId}&limit=50&offset=0`);
      
      const response = await chatAPI.getMessages(otherUserId);
      console.log('Messages API response:', response);
      
      // Handle different possible response structures
      let messagesData = [];
      if (response.data) {
        // Try different possible structures
        if (Array.isArray(response.data)) {
          messagesData = response.data;
        } else if (response.data.messages && Array.isArray(response.data.messages)) {
          messagesData = response.data.messages;
        } else if (response.data.data && Array.isArray(response.data.data)) {
          messagesData = response.data.data;
        } else {
          console.warn('Unexpected messages response structure:', response.data);
        }
      }
      
      console.log('Processed messages data:', messagesData);
      
      // Sort messages by timestamp (oldest first, newest last)
      const sortedMessages = messagesData.sort((a, b) => {
        const timeA = new Date(a.created_at || a.timestamp || a.sent_at);
        const timeB = new Date(b.created_at || b.timestamp || b.sent_at);
        return timeA - timeB; // Ascending order (oldest first)
      });
      
      console.log('Sorted messages:', sortedMessages);
      setMessages(sortedMessages);
      setError(''); // Clear any previous errors
      
      // Mark messages as read if there are any
      if (messagesData.length > 0) {
        try {
          await chatAPI.markMessagesAsRead(otherUserId);
          console.log('Messages marked as read for user:', otherUserId);
        } catch (readError) {
          console.warn('Failed to mark messages as read:', readError);
        }
      }
      
    } catch (error) {
      console.error('Error loading messages for user', otherUserId, ':', error);
      console.error('Error details:', error.response?.data || error.message);
      setError(`Không thể tải tin nhắn: ${error.response?.data?.message || error.message}`);
      setMessages([]);
    }
  };

  const sendMessage = async () => {
    if (!newMessage.trim()) return;

    try {
      setIsSending(true);
      
      const messageData = {
        content: newMessage.trim(),
        receiver_id: currentConversation.receiver_id,
        // ticket_id: currentConversation.ticket_id
      };

      console.log('Sending message:', messageData);
      const response = await chatAPI.sendMessage(messageData);
      console.log('Message sent response:', response.data);
      
      // Add message to current conversation immediately for better UX
      const newMsg = {
        id: response.data?.id || Date.now(),
        content: newMessage.trim(),
        sender_id: user.id,
        receiver_id: currentConversation.receiver_id,
        created_at: new Date().toISOString(),
        ...response.data
      };
      
      setMessages(prev => [...prev, newMsg]);
      setNewMessage('');
      
      // Scroll to bottom immediately after adding new message
      setTimeout(() => {
        scrollToBottom();
      }, 100);
      
      // If this was a new conversation, reload conversations to get the real conversation
      if (currentConversation.isNew) {
        console.log('New conversation created, reloading conversations...');
        
        // Update current conversation to remove the "new" flag
        setCurrentConversation(prev => ({ 
          ...prev, 
          isNew: false,
          id: response.data?.conversation_id || prev.id
        }));
        
        // Reload conversations after a delay to get updated list
        setTimeout(async () => {
          await loadConversations();
        }, 1500);
      } else {
        // For existing conversations, reload messages to get the latest
        const otherUserId = currentConversation.other_user_id || currentConversation.receiver_id;
        setTimeout(() => {
          loadMessages(otherUserId);
        }, 500);
      }
      
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Không thể gửi tin nhắn. Vui lòng thử lại.');
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Ensure conversations is always an array before filtering
  const filteredConversations = Array.isArray(conversations) 
    ? conversations.filter(conv =>
        conv.ticket_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        conv.other_user_name?.toLowerCase().includes(searchTerm.toLowerCase())
      )
    : [];

  console.log('Current conversations state:', conversations);
  console.log('Filtered conversations:', filteredConversations);
  console.log('Is loading:', isLoading);

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Vui lòng đăng nhập</h2>
          <button
            onClick={() => navigate('/login')}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-md"
          >
            Đăng nhập
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <button
                onClick={() => navigate('/homepage')}
                className="flex items-center text-gray-600 hover:text-gray-900 mr-4"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                Về trang chủ
              </button>
              <h1 className="text-2xl font-bold text-gray-900">💬 Chat</h1>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="bg-white rounded-lg shadow-lg overflow-hidden" style={{ height: '600px' }}>
          <div className="flex h-full">
            {/* Conversations Sidebar */}
            <div className="w-1/3 border-r border-gray-200 flex flex-col">
              {/* Search */}
              <div className="p-4 border-b border-gray-200">
                <input
                  type="text"
                  placeholder="Tìm kiếm cuộc trò chuyện..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                />
               
              </div>

              {/* Conversations List */}
              <div className="flex-1 overflow-y-auto">
                {isLoading ? (
                  <div className="p-4 text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="text-sm text-gray-500 mt-2">Đang tải...</p>
                  </div>
                ) : (
                  <>
                    {/* Show new conversation if we have parameters */}
                    {currentConversation && currentConversation.isNew && (
                      <div
                        className="p-4 border-b border-blue-200 cursor-pointer bg-blue-50"
                      >
                        <div className="flex items-center justify-between mb-2">
                          <h3 className="font-medium text-gray-900 truncate flex items-center">
                            <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                            {currentConversation.other_user_name}
                          </h3>
                          <span className="text-xs text-blue-600 font-medium">
                            Mới
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 truncate">
                          Vé: <span className="font-medium">{currentConversation.ticket_name}</span>
                        </p>
                        <p className="text-xs text-blue-600 mt-1">
                          Nhập tin nhắn để bắt đầu trò chuyện
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          User ID: {currentConversation.receiver_id}
                        </p>
                      </div>
                    )}
                    
                    {filteredConversations.length === 0 && !currentConversation?.isNew ? (
                      <div className="p-4 text-center text-gray-500">
                        <svg className="w-12 h-12 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                        </svg>
                        <p>Chưa có cuộc trò chuyện nào</p>
                        <p className="text-sm mt-2">Hãy nhắn tin với người bán từ trang chi tiết vé</p>
                      </div>
                    ) : (
                      <>
                       
                        
                        {filteredConversations.map((conversation) => (
                          <div
                            key={conversation.id}
                            onClick={() => {
                              console.log('Clicking on conversation:', conversation);
                              console.log('Setting current conversation with other_user_id:', conversation.other_user_id);
                              setCurrentConversation({
                                ...conversation,
                                isNew: false
                              });
                            }}
                            className={`p-4 border-b border-gray-100 cursor-pointer hover:bg-gray-50 ${
                              currentConversation?.id === conversation.id && !currentConversation.isNew ? 'bg-blue-50 border-blue-200' : ''
                            }`}
                          >
                            <div className="flex items-center justify-between mb-2">
                              <h3 className="font-medium text-gray-900 truncate">
                                {conversation.other_user_name || `User #${conversation.other_user_id}`}
                              </h3>
                              <span className="text-xs text-gray-500">
                                {formatDate(conversation.last_message_time)}
                              </span>
                            </div>
                            {/* <p className="text-sm text-gray-600 truncate">
                              Vé: <span className="font-medium">{conversation.ticket_name}</span>
                            </p> */}
                            <p className="text-sm text-gray-500 truncate mt-1">
                              {conversation.last_message}
                            </p>
                            <div className="flex items-center justify-between mt-2">
                              <span className="text-xs text-gray-400">
                                User ID: {conversation.other_user_id}
                              </span>
                              {conversation.unread_count > 0 && (
                                <span className="inline-block bg-red-500 text-white text-xs rounded-full px-2 py-1">
                                  {conversation.unread_count}
                                </span>
                              )}
                            </div>
                          </div>
                        ))}
                      </>
                    )}
                  </>
                )}
              </div>
            </div>

            {/* Chat Area */}
            <div className="flex-1 flex flex-col">
              {currentConversation ? (
                <>
                  {/* Chat Header */}
                  <div className="p-4 border-b border-gray-200 bg-gray-50">
                    <div className="flex items-center justify-between">
                      <div>
                        <h2 className="font-semibold text-gray-900">
                          {currentConversation.isNew ? (
                            <span className="flex items-center">
                              <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                              Cuộc trò chuyện mới với {currentConversation.other_user_name}
                            </span>
                          ) : (
                            `Chat với ${currentConversation.other_user_name || 'Unknown User'}`
                          )}
                        </h2>
                        {/* {currentConversation.ticket_name && <p className="text-sm text-gray-600 mt-1">
                          Về vé: <span className="font-medium text-blue-600">{currentConversation.ticket_name}</span>
                        </p>} */}
                        {currentConversation.isNew && (
                          <p className="text-xs text-blue-600 mt-1 flex items-center">
                            <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            Gửi tin nhắn đầu tiên để bắt đầu cuộc trò chuyện
                          </p>
                        )}
                      </div>
                      <div className="text-right">
                        <span className="text-xs text-gray-500">
                          ID: {currentConversation.receiver_id}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Messages */}
                  <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
                    {error && (
                      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                        {error}
                        <button 
                          onClick={() => setError('')}
                          className="ml-2 text-red-500 hover:text-red-700"
                        >
                          ✕
                        </button>
                      </div>
                    )}
                    
                    {messages.length === 0 && currentConversation.isNew ? (
                      <div className="text-center text-gray-500 py-8">
                        <svg className="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                        </svg>
                        <p className="font-medium">Bắt đầu cuộc trò chuyện mới</p>
                        <p className="text-sm mt-1">Hãy gửi tin nhắn đầu tiên của bạn</p>
                      </div>
                    ) : messages.length === 0 ? (
                      <div className="text-center text-gray-500 py-8">
                        <p>Chưa có tin nhắn nào trong cuộc trò chuyện này</p>
                        <p className="text-sm mt-1">Có thể đang tải tin nhắn...</p>
                      </div>
                    ) : (
                      messages.map((message, index) => {
                        // Debug log for message order
                        console.log(`Rendering message ${index}:`, {
                          id: message.id,
                          content: message.content.substring(0, 20) + '...',
                          time: message.created_at || message.timestamp || message.sent_at,
                          sender: message.sender_id
                        });
                        
                        return (
                        <div
                          key={message.id || index}
                          className={`flex ${message.sender_id === user.id ? 'justify-end' : 'justify-start'}`}
                        >
                          <div
                            className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg shadow-sm ${
                              message.sender_id === user.id
                                ? 'bg-blue-600 text-white'
                                : 'bg-white text-gray-900 border border-gray-200'
                            }`}
                          >
                            <div className="flex items-start justify-between mb-1">
                              <span className={`text-xs font-medium ${
                                message.sender_id === user.id ? 'text-blue-100' : 'text-gray-600'
                              }`}>
                                {message.sender_id === user.id ? 'Bạn' : currentConversation.other_user_name}
                              </span>
                            </div>
                            <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                            <p className={`text-xs mt-1 ${
                              message.sender_id === user.id ? 'text-blue-100' : 'text-gray-500'
                            }`}>
                              {formatDate(message.sent_at)}
                            </p>
                          </div>
                        </div>
                        );
                      })
                    )}
                    <div ref={messagesEndRef} />
                  </div>

                  {/* Message Input */}
                  <div className="p-4 border-t border-gray-200 bg-white">
                    <div className="flex space-x-2">
                      <textarea
                        value={newMessage}
                        onChange={(e) => setNewMessage(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Nhập tin nhắn..."
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 resize-none"
                        rows="2"
                        maxLength={1000}
                      />
                      <button
                        onClick={sendMessage}
                        disabled={!newMessage.trim() || isSending}
                        className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md transition-colors flex items-center justify-center"
                      >
                        {isSending ? (
                          <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                        ) : (
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                          </svg>
                        )}
                      </button>
                    </div>
                    <div className="text-xs text-gray-500 mt-1 flex justify-between">
                      <span>{newMessage.length}/1000 ký tự</span>
                      <span>Enter để gửi, Shift+Enter để xuống dòng</span>
                    </div>
                  </div>
                </>
              ) : (
                <div className="flex-1 flex items-center justify-center bg-gray-50">
                  <div className="text-center text-gray-500">
                    <svg className="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                    </svg>
                    <p className="text-lg font-medium mb-2">Chào mừng đến với Chat</p>
                    <p>Chọn một cuộc trò chuyện để bắt đầu</p>
                    <p className="text-sm mt-2">hoặc nhắn tin với người bán từ trang chi tiết vé</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat;
