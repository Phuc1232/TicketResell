import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getErrorMessage } from '../utils/validation';
import Input from '../components/Input';
import Button from '../components/Button';
import AuthLayout from '../components/AuthLayout';

const Verify = () => {
  const [verificationCode, setVerificationCode] = useState('');
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isResending, setIsResending] = useState(false);
  const [resendMessage, setResendMessage] = useState('');
  const [canResend, setCanResend] = useState(true);
  const [resendCooldown, setResendCooldown] = useState(0);
  
  const { verify, resendVerification, isAuthenticated, tempToken, error, clearError } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  
  const email = location.state?.email || '';
  const message = location.state?.message || '';
  const fromRegistration = location.state?.fromRegistration || false;

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  useEffect(() => {
    // If no temp token and not from registration, redirect to login
    if (!tempToken && !fromRegistration) {
      navigate('/login', { replace: true });
    }
  }, [tempToken, fromRegistration, navigate]);

  useEffect(() => {
    // Handle cooldown timer
    let timer;
    if (resendCooldown > 0) {
      timer = setTimeout(() => {
        setResendCooldown(prev => prev - 1);
      }, 1000);
    } else {
      setCanResend(true);
    }
    
    return () => {
      if (timer) clearTimeout(timer);
    };
  }, [resendCooldown]);

  useEffect(() => {
    // Clear auth error when component unmounts
    return () => {
      if (error) {
        clearError();
      }
    };
  }, [error, clearError]);

  const handleChange = (e) => {
    const value = e.target.value.replace(/\D/g, '').slice(0, 6); // Only digits, max 6
    setVerificationCode(value);
    
    // Clear errors when user starts typing
    if (errors.verification_code) {
      setErrors(prev => ({
        ...prev,
        verification_code: ''
      }));
    }
    setResendMessage('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!verificationCode) {
      setErrors({ verification_code: 'Mã xác thực là bắt buộc' });
      return;
    }
    
    if (verificationCode.length !== 6) {
      setErrors({ verification_code: 'Mã xác thực phải có 6 chữ số' });
      return;
    }

    setIsSubmitting(true);
    setErrors({});

    try {
      await verify(verificationCode);
      navigate('/dashboard', { replace: true });
    } catch (error) {
      console.error('Verification error:', error);
      
      const errorData = error.response?.data;
      const errorCode = errorData?.error_code;
      
      if (errorCode === 'VERIFICATION_CODE_EXPIRED') {
        setCanResend(errorData?.can_resend !== false);
        setErrors({
          verification_code: 'Mã xác thực đã hết hạn. Vui lòng yêu cầu mã mới.'
        });
      } else if (errorCode === 'VERIFICATION_CODE_INVALID') {
        setErrors({
          verification_code: 'Mã xác thực không đúng. Vui lòng thử lại.'
        });
      } else if (errorCode === 'USER_ALREADY_VERIFIED') {
        navigate('/login', { 
          state: { 
            message: 'Tài khoản của bạn đã được xác thực. Vui lòng đăng nhập.' 
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

  const handleResend = async () => {
    if (!canResend || isResending) return;

    setIsResending(true);
    setErrors({});
    setResendMessage('');

    try {
      const response = await resendVerification();
      setResendMessage(response.message || 'Verification code sent successfully!');
      setCanResend(false);
      setResendCooldown(60); // 60 seconds cooldown
    } catch (error) {
      console.error('Resend error:', error);
      
      const errorData = error.response?.data;
      const errorCode = errorData?.error_code;
      
      if (errorCode === 'USER_ALREADY_VERIFIED') {
        navigate('/login', { 
          state: { 
            message: 'Your account is already verified. Please login.' 
          }
        });
      } else {
        setErrors({
          general: getErrorMessage(error)
        });
      }
    } finally {
      setIsResending(false);
    }
  };

  return (
    <AuthLayout 
      title="Xác thực tài khoản"
      subtitle={
        <div className="space-y-2">
          <p>
            Chúng tôi đã gửi mã xác thực đến{' '}
            <span className="font-medium text-gray-900">{email}</span>
          </p>
          {message && (
            <p className="text-blue-600">
              {message}
            </p>
          )}
        </div>
      }
    >
      <form className="space-y-6" onSubmit={handleSubmit}>
        {errors.general && (
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md">
            {errors.general}
          </div>
        )}
        
        {resendMessage && (
          <div className="bg-green-50 border border-green-200 text-green-600 px-4 py-3 rounded-md">
            {resendMessage}
          </div>
        )}
        
        <Input
          label="Mã xác thực"
          type="text"
          name="verification_code"
          value={verificationCode}
          onChange={handleChange}
          error={errors.verification_code}
          placeholder="Nhập mã 6 chữ số"
          required
          className="text-center text-2xl tracking-widest font-mono"
          maxLength={6}
          autoComplete="one-time-code"
        />

        <Button
          type="submit"
          variant="primary"
          size="lg"
          loading={isSubmitting}
          className="w-full"
        >
          {isSubmitting ? 'Đang xác thực...' : 'Xác thực tài khoản'}
        </Button>
        
        <div className="text-center space-y-3">
          <p className="text-sm text-gray-600">
            Không nhận được mã?{' '}
            <button
              type="button"
              onClick={handleResend}
              disabled={!canResend || isResending}
              className={`font-medium ${
                canResend && !isResending
                  ? 'text-blue-600 hover:text-blue-500 cursor-pointer'
                  : 'text-gray-400 cursor-not-allowed'
              }`}
            >
              {isResending 
                ? 'Đang gửi...' 
                : resendCooldown > 0 
                  ? `Gửi lại sau ${resendCooldown}s`
                  : 'Gửi lại mã'
              }
            </button>
          </p>
          
          <Link
            to="/login"
            className="block text-sm font-medium text-blue-600 hover:text-blue-500"
          >
            Quay lại đăng nhập
          </Link>
        </div>
      </form>
    </AuthLayout>
  );
};

export default Verify;
