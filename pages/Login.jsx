import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { validateLoginForm, getErrorMessage } from '../utils/validation';
import Input from '../components/Input';
import Button from '../components/Button';
import AuthLayout from '../components/AuthLayout';

const Login = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const { login, isAuthenticated, user, error, clearError } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated && user) {
      // Redirect admin to admin dashboard, regular users to homepage
      if (user.role_id === 1) {
        navigate('/admin', { replace: true });
      } else {
        navigate('/homepage', { replace: true });
      }
    }
  }, [isAuthenticated, user, navigate]);

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
    
    const validation = validateLoginForm(formData);
    if (!validation.isValid) {
      setErrors(validation.errors);
      return;
    }

    setIsSubmitting(true);
    setErrors({});

    try {
      const result = await login(formData);
      
      // Check if user is admin and redirect accordingly
      if (result && result.user && result.user.role_id === 1) {
        navigate('/admin', { replace: true });
      } else {
        navigate('/homepage', { replace: true });
      }
    } catch (error) {
      console.error('Login error:', error);
      
      if (error.response?.data?.error_code === 'ACCOUNT_NOT_VERIFIED') {
        navigate('/verify', { 
          state: { 
            email: formData.email, 
            message: 'Your account is not verified. Please check your email for the verification code.' 
          }
        });
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
      title="Đăng nhập tài khoản"
      subtitle={
        <>
          Hoặc{' '}
          <Link
            to="/register"
            className="font-medium text-blue-600 hover:text-blue-500"
          >
            tạo tài khoản mới
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
          autoComplete="current-password"
        />

        <div className="flex items-center justify-between">
          <div className="text-sm">
            <Link
              to="/forgot-password"
              className="font-medium text-blue-600 hover:text-blue-500"
            >
              Quên mật khẩu?
            </Link>
          </div>
        </div>

        <Button
          type="submit"
          variant="primary"
          size="lg"
          loading={isSubmitting}
          className="w-full"
        >
          {isSubmitting ? 'Đang đăng nhập...' : 'Đăng nhập'}
        </Button>
      </form>
    </AuthLayout>
  );
};

export default Login;
