// Validation utilities
export const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const validatePassword = (password) => {
  // At least 6 characters, must contain at least 1 letter and 1 number
  const hasLetter = /[a-zA-Z]/.test(password);
  const hasNumber = /\d/.test(password);
  return password.length >= 6 && hasLetter && hasNumber;
};

export const validateUsername = (username) => {
  // 3-50 characters, only letters, numbers, and underscores
  const usernameRegex = /^[a-zA-Z0-9_]{3,50}$/;
  return usernameRegex.test(username);
};

export const validatePhoneNumber = (phoneNumber) => {
  // 10-15 digits only
  const phoneRegex = /^\d{10,15}$/;
  return phoneRegex.test(phoneNumber);
};

export const validateDateOfBirth = (dateString) => {
  try {
    const date = new Date(dateString);
    const now = new Date();
    
    // Check if date is valid and not in the future
    if (isNaN(date.getTime()) || date > now) {
      return false;
    }
    
    // Check if user is at least 13 years old
    const age = now.getFullYear() - date.getFullYear();
    const monthDiff = now.getMonth() - date.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && now.getDate() < date.getDate())) {
      return age - 1 >= 13;
    }
    
    return age >= 13;
  } catch {
    return false;
  }
};

// Form validation
export const validateRegisterForm = (formData) => {
  const errors = {};

  if (!formData.username) {
    errors.username = 'Tên người dùng là bắt buộc';
  } else if (!validateUsername(formData.username)) {
    errors.username = 'Tên người dùng phải có 3-50 ký tự và chỉ chứa chữ cái, số và dấu gạch dưới';
  }

  if (!formData.email) {
    errors.email = 'Email là bắt buộc';
  } else if (!validateEmail(formData.email)) {
    errors.email = 'Vui lòng nhập địa chỉ email hợp lệ';
  }

  if (!formData.password) {
    errors.password = 'Mật khẩu là bắt buộc';
  } else if (!validatePassword(formData.password)) {
    errors.password = 'Mật khẩu phải có ít nhất 6 ký tự và chứa ít nhất 1 chữ cái và 1 chữ số';
  }

  if (!formData.phone_number) {
    errors.phone_number = 'Số điện thoại là bắt buộc';
  } else if (!validatePhoneNumber(formData.phone_number)) {
    errors.phone_number = 'Số điện thoại phải có 10-15 chữ số';
  }

  if (!formData.date_of_birth) {
    errors.date_of_birth = 'Ngày sinh là bắt buộc';
  } else if (!validateDateOfBirth(formData.date_of_birth)) {
    errors.date_of_birth = 'Vui lòng nhập ngày sinh hợp lệ (phải đủ 13 tuổi)';
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
};

export const validateLoginForm = (formData) => {
  const errors = {};

  if (!formData.email) {
    errors.email = 'Email là bắt buộc';
  } else if (!validateEmail(formData.email)) {
    errors.email = 'Vui lòng nhập địa chỉ email hợp lệ';
  }

  if (!formData.password) {
    errors.password = 'Mật khẩu là bắt buộc';
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
};

// Ticket validation
export const validateTicketForm = (formData) => {
  const errors = {};

  if (!formData.EventName) {
    errors.EventName = 'Tên sự kiện là bắt buộc';
  } else if (formData.EventName.length < 1 || formData.EventName.length > 100) {
    errors.EventName = 'Tên sự kiện phải có 1-100 ký tự';
  }

  if (!formData.EventDate) {
    errors.EventDate = 'Ngày sự kiện là bắt buộc';
  } else {
    const eventDate = new Date(formData.EventDate);
    const now = new Date();
    if (eventDate <= now) {
      errors.EventDate = 'Ngày sự kiện phải sau thời điểm hiện tại';
    }
  }

  if (!formData.Price && formData.Price !== 0) {
    errors.Price = 'Giá vé là bắt buộc';
  } else if (formData.Price < 0) {
    errors.Price = 'Giá vé phải lớn hơn hoặc bằng 0';
  }

  if (!formData.Status) {
    errors.Status = 'Trạng thái vé là bắt buộc';
  }

  if (!formData.PaymentMethod) {
    errors.PaymentMethod = 'Phương thức thanh toán là bắt buộc';
  }

  if (!formData.ContactInfo) {
    errors.ContactInfo = 'Thông tin liên hệ là bắt buộc';
  } else if (formData.ContactInfo.length < 1 || formData.ContactInfo.length > 200) {
    errors.ContactInfo = 'Thông tin liên hệ phải có 1-200 ký tự';
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
};

// Date formatting
export const formatDateForAPI = (dateString) => {
  const date = new Date(dateString);
  return date.toISOString();
};

// Format price to VND
export const formatPrice = (price) => {
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND'
  }).format(price);
};

// Format date to Vietnamese
export const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('vi-VN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// Error handling
export const getErrorMessage = (error) => {
  if (error.response?.data?.message) {
    return error.response.data.message;
  }
  
  if (error.response?.data?.errors) {
    const errors = error.response.data.errors;
    const firstError = Object.values(errors)[0];
    return Array.isArray(firstError) ? firstError[0] : firstError;
  }
  
  return error.message || 'Đã xảy ra lỗi không mong muốn';
};
