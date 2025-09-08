import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { validateRegisterForm, formatDateForAPI, getErrorMessage } from '../utils/validation';
import Input from '../components/Input';
import Button from '../components/Button';
import AuthLayout from '../components/AuthLayout';

const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    phone_number: '',
    date_of_birth: '',
  });
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const { register, isAuthenticated, error, clearError } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    // Clear auth error when component unmounts or form changes
    return () => {
      if (error) {
        clearError();
      }
    };
  }, [error, clearError]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear field error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const validation = validateRegisterForm(formData);
    if (!validation.isValid) {
      setErrors(validation.errors);
      return;
    }

    setIsSubmitting(true);
    setErrors({});

    try {
      // Format date for API
      const registrationData = {
        ...formData,
        date_of_birth: formatDateForAPI(formData.date_of_birth)
      };

      const response = await register(registrationData);
      
      // Navigate to verification page
      navigate('/verify', { 
        state: { 
          email: formData.email,
          message: response.message,
          fromRegistration: true
        }
      });
    } catch (error) {
      console.error('Registration error:', error);
      
      if (error.response?.data?.errors) {
        // Handle validation errors from server
        setErrors(error.response.data.errors);
      } else {
        setErrors({
          general: getErrorMessage(error)
        });
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AuthLayout 
      title="Tạo tài khoản mới"
      subtitle={
        <>
          Hoặc{' '}
          <Link
            to="/login"
            className="font-medium text-blue-600 hover:text-blue-500"
          >
            đăng nhập tài khoản có sẵn
          </Link>
        </>
      }
    >
      <form className="space-y-6" onSubmit={handleSubmit}>
        {errors.general && (
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md">
            {errors.general}
          </div>
        )}
        
        <Input
          label="Tên người dùng"
          type="text"
          name="username"
          value={formData.username}
          onChange={handleChange}
          error={errors.username}
          placeholder="Nhập tên người dùng"
          required
          autoComplete="username"
        />

        <Input
          label="Địa chỉ email"
          type="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          error={errors.email}
          placeholder="Nhập email của bạn"
          required
          autoComplete="email"
        />

        <Input
          label="Mật khẩu"
          type="password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          error={errors.password}
          placeholder="Nhập mật khẩu của bạn"
          required
          autoComplete="new-password"
        />

        <Input
          label="Số điện thoại"
          type="tel"
          name="phone_number"
          value={formData.phone_number}
          onChange={handleChange}
          error={errors.phone_number}
          placeholder="Nhập số điện thoại"
          required
          autoComplete="tel"
        />

        <Input
          label="Ngày sinh"
          type="date"
          name="date_of_birth"
          value={formData.date_of_birth}
          onChange={handleChange}
          error={errors.date_of_birth}
          required
        />

        <div className="text-sm text-gray-600 bg-blue-50 p-3 rounded-md">
          <p className="font-medium mb-2">Yêu cầu mật khẩu:</p>
          <ul className="list-disc list-inside space-y-1">
            <li>Tối thiểu 6 ký tự</li>
            <li>Phải chứa ít nhất 1 chữ cái và 1 chữ số</li>
          </ul>
        </div>

        <Button
          type="submit"
          variant="primary"
          size="lg"
          loading={isSubmitting}
          className="w-full"
        >
          {isSubmitting ? 'Đang tạo tài khoản...' : 'Tạo tài khoản'}
        </Button>
      </form>
    </AuthLayout>
  );
};

export default Register;
