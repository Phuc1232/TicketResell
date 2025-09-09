import React, { useState, useEffect } from 'react';
import { userAPI } from '../services/userAPI';
import { useAuth } from '../context/AuthContext';

// Simple notification function without external dependency
const showNotification = (message, type = 'info') => {
  alert(`${type.toUpperCase()}: ${message}`);
};

const UserProfile = () => {
  const { user, updateUser } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [showVerification, setShowVerification] = useState(false);
  
  const [profileData, setProfileData] = useState({
    username: '',
    phone_number: '',
    date_of_birth: '',
    status: 'active'
  });

  const [verificationData, setVerificationData] = useState({
    verification_code: '',
    verification_type: 'email'
  });

  const [errors, setErrors] = useState({});

  useEffect(() => {
    loadUserData();
  }, []);

  const loadUserData = async () => {
    try {
      setIsLoading(true);
      const response = await userAPI.getCurrentUser();
      const userData = response.data;
      
      setProfileData({
        username: userData.username || '',
        phone_number: userData.phone_number || '',
        date_of_birth: userData.date_of_birth ? userData.date_of_birth.split('T')[0] : '',
        status: userData.status || 'active'
      });
    } catch (error) {
      console.error('Error loading user data:', error);
      showNotification('Không thể tải thông tin người dùng', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setProfileData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (profileData.username && (profileData.username.length < 3 || profileData.username.length > 50)) {
      newErrors.username = 'Username phải có từ 3-50 ký tự';
    }

    if (profileData.username && !/^[a-zA-Z0-9_]+$/.test(profileData.username)) {
      newErrors.username = 'Username chỉ được chứa chữ cái, số và dấu gạch dưới';
    }

    if (profileData.phone_number && (profileData.phone_number.length < 10 || profileData.phone_number.length > 15)) {
      newErrors.phone_number = 'Số điện thoại phải có từ 10-15 chữ số';
    }

    if (profileData.phone_number && !/^\d+$/.test(profileData.phone_number)) {
      newErrors.phone_number = 'Số điện thoại chỉ được chứa số';
    }

    if (profileData.date_of_birth) {
      const birthDate = new Date(profileData.date_of_birth);
      const today = new Date();
      if (birthDate >= today) {
        newErrors.date_of_birth = 'Ngày sinh phải ở trong quá khứ';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    try {
      setIsLoading(true);
      
      // Prepare update data (only include non-empty fields)
      const updateData = {};
      if (profileData.username.trim()) updateData.username = profileData.username.trim();
      if (profileData.phone_number.trim()) updateData.phone_number = profileData.phone_number.trim();
      if (profileData.date_of_birth) updateData.date_of_birth = profileData.date_of_birth;
      
      const response = await userAPI.updateCurrentUser(updateData);
      
      // Update auth context with new user data
      updateUser(response.data);
      
      setIsEditing(false);
      showNotification('Cập nhật hồ sơ thành công!', 'success');
      
    } catch (error) {
      console.error('Error updating profile:', error);
      
      if (error.response?.data?.errors) {
        setErrors(error.response.data.errors);
      } else {
        showNotification(error.response?.data?.message || 'Không thể cập nhật hồ sơ', 'error');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerification = async (e) => {
    e.preventDefault();
    
    if (!verificationData.verification_code || verificationData.verification_code.length !== 6) {
      showNotification('Mã xác thực phải có 6 chữ số', 'error');
      return;
    }

    try {
      setIsLoading(true);
      
      await userAPI.verifyAccount(verificationData);
      
      showNotification('Xác thực tài khoản thành công!', 'success');
      setShowVerification(false);
      setVerificationData({
        verification_code: '',
        verification_type: 'email'
      });
      
      // Reload user data to get updated verification status
      loadUserData();
      
    } catch (error) {
      console.error('Error verifying account:', error);
      
      if (error.response?.data?.errors) {
        const errorMessages = Object.values(error.response.data.errors).flat();
        showNotification(errorMessages.join(', '), 'error');
      } else {
        showNotification(error.response?.data?.message || 'Không thể xác thực tài khoản', 'error');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Chưa cập nhật';
    return new Date(dateString).toLocaleDateString('vi-VN');
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      active: { color: 'bg-green-100 text-green-800', text: 'Hoạt động' },
      inactive: { color: 'bg-gray-100 text-gray-800', text: 'Không hoạt động' },
      suspended: { color: 'bg-red-100 text-red-800', text: 'Bị đình chỉ' }
    };
    
    const config = statusConfig[status] || statusConfig.active;
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.color}`}>
        {config.text}
      </span>
    );
  };

  const getRoleBadge = (roleId) => {
    const roleConfig = {
      1: { color: 'bg-purple-100 text-purple-800', text: 'Admin' },
      2: { color: 'bg-blue-100 text-blue-800', text: 'Người dùng' },
      3: { color: 'bg-yellow-100 text-yellow-800', text: 'Moderator' },
      4: { color: 'bg-gray-100 text-gray-800', text: 'Khách' }
    };
    
    const config = roleConfig[roleId] || roleConfig[2];
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.color}`}>
        {config.text}
      </span>
    );
  };

  if (isLoading && !user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="bg-white shadow rounded-lg mb-6">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Hồ sơ cá nhân</h1>
                <p className="text-gray-600">Quản lý thông tin tài khoản của bạn</p>
              </div>
              <div className="flex space-x-3">
                {/* {!showVerification && (
                  <button
                    onClick={() => setShowVerification(true)}
                    className="px-4 py-2 bg-yellow-600 text-white rounded-md hover:bg-yellow-700 transition-colors"
                  >
                    Xác thực tài khoản
                  </button>
                )} */}
                {!isEditing ? (
                  <button
                    onClick={() => setIsEditing(true)}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
                  >
                    Chỉnh sửa
                  </button>
                ) : (
                  <button
                    onClick={() => {
                      setIsEditing(false);
                      setErrors({});
                      loadUserData(); // Reset form
                    }}
                    className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
                  >
                    Hủy
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* User Info Display */}
          {!isEditing && (
            <div className="px-6 py-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium text-gray-500">Email</label>
                    <p className="text-lg text-gray-900">{user?.email || 'Chưa cập nhật'}</p>
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium text-gray-500">Username</label>
                    <p className="text-lg text-gray-900">{user?.username || 'Chưa cập nhật'}</p>
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium text-gray-500">Số điện thoại</label>
                    <p className="text-lg text-gray-900">{user?.phone_number || 'Chưa cập nhật'}</p>
                  </div>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium text-gray-500">Ngày sinh</label>
                    <p className="text-lg text-gray-900">{formatDate(user?.date_of_birth)}</p>
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium text-gray-500">Trạng thái</label>
                    <div className="mt-1">
                      {getStatusBadge(user?.status)}
                    </div>
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium text-gray-500">Vai trò</label>
                    <div className="mt-1">
                      {getRoleBadge(user?.role_id)}
                    </div>
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium text-gray-500">Ngày tạo tài khoản</label>
                    <p className="text-lg text-gray-900">{formatDate(user?.create_date)}</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Edit Form */}
          {isEditing && (
            <form onSubmit={handleUpdateProfile} className="px-6 py-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Email
                    </label>
                    <input
                      type="email"
                      value={user?.email || ''}
                      disabled
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">Email không thể thay đổi</p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Username <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      name="username"
                      value={profileData.username}
                      onChange={handleInputChange}
                      className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 ${
                        errors.username ? 'border-red-300' : 'border-gray-300'
                      }`}
                      placeholder="Nhập username (3-50 ký tự)"
                    />
                    {errors.username && (
                      <p className="mt-1 text-sm text-red-600">{errors.username}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Số điện thoại
                    </label>
                    <input
                      type="tel"
                      name="phone_number"
                      value={profileData.phone_number}
                      onChange={handleInputChange}
                      className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 ${
                        errors.phone_number ? 'border-red-300' : 'border-gray-300'
                      }`}
                      placeholder="Nhập số điện thoại (10-15 chữ số)"
                    />
                    {errors.phone_number && (
                      <p className="mt-1 text-sm text-red-600">{errors.phone_number}</p>
                    )}
                  </div>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Ngày sinh
                    </label>
                    <input
                      type="date"
                      name="date_of_birth"
                      value={profileData.date_of_birth}
                      onChange={handleInputChange}
                      className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 ${
                        errors.date_of_birth ? 'border-red-300' : 'border-gray-300'
                      }`}
                    />
                    {errors.date_of_birth && (
                      <p className="mt-1 text-sm text-red-600">{errors.date_of_birth}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">Trạng thái hiện tại</label>
                    <div className="mt-2">
                      {getStatusBadge(user?.status)}
                    </div>
                    <p className="text-xs text-gray-500 mt-1">Trạng thái chỉ có thể thay đổi bởi admin</p>
                  </div>
                </div>
              </div>

              <div className="mt-6 flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => {
                    setIsEditing(false);
                    setErrors({});
                    loadUserData();
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  Hủy
                </button>
                <button
                  type="submit"
                  disabled={isLoading}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 transition-colors"
                >
                  {isLoading ? 'Đang cập nhật...' : 'Cập nhật'}
                </button>
              </div>
            </form>
          )}
        </div>

        {/* Verification Modal */}
        {showVerification && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Xác thực tài khoản</h2>
              
              <form onSubmit={handleVerification}>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Loại xác thực
                    </label>
                    <select
                      name="verification_type"
                      value={verificationData.verification_type}
                      onChange={(e) => setVerificationData(prev => ({
                        ...prev,
                        verification_type: e.target.value
                      }))}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="email">Email</option>
                      <option value="phone">Số điện thoại</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Mã xác thực <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      name="verification_code"
                      value={verificationData.verification_code}
                      onChange={(e) => setVerificationData(prev => ({
                        ...prev,
                        verification_code: e.target.value
                      }))}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
                      placeholder="Nhập mã 6 chữ số"
                      maxLength={6}
                    />
                  </div>
                </div>

                <div className="mt-6 flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={() => setShowVerification(false)}
                    className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    Hủy
                  </button>
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 transition-colors"
                  >
                    {isLoading ? 'Đang xác thực...' : 'Xác thực'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default UserProfile;
