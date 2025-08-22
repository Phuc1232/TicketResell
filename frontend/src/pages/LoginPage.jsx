import React, { useState } from 'react'
import { Facebook, Chrome, Apple } from 'lucide-react'
import toast from 'react-hot-toast'
import LoginForm from '../components/LoginForm'
import RegisterForm from '../components/RegisterForm'

const LoginPage = () => {
  const [isLogin, setIsLogin] = useState(true)

  const toggleForm = () => {
    setIsLogin(!isLogin)
  }

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
      {/* Main Container */}
      <div className="w-full max-w-4xl bg-white rounded-3xl shadow-2xl overflow-hidden">
        <div className="flex flex-col lg:flex-row min-h-[600px]">
          
          {/* Left Panel - Illustration */}
          <div className="lg:w-1/2 bg-gradient-to-br from-teal-400 via-teal-500 to-teal-600 p-8 flex flex-col justify-center items-center text-white relative overflow-hidden">
            {/* Background Pattern */}
            <div className="absolute inset-0 opacity-20">
              <div className="absolute top-10 left-10 w-20 h-20 bg-white rounded-full"></div>
              <div className="absolute top-32 right-16 w-16 h-16 bg-white rounded-full"></div>
              <div className="absolute bottom-20 left-20 w-12 h-12 bg-white rounded-full"></div>
              <div className="absolute bottom-32 right-8 w-8 h-8 bg-white rounded-full"></div>
            </div>
            
            {/* Content */}
            <div className="relative z-10 text-center">
              <h1 className="text-4xl font-bold mb-4">Welcome to TicketResell</h1>
              <p className="text-lg mb-8 opacity-90">
                Buy and sell tickets safely<br />
                Join our community today!
              </p>
              
              {/* Toggle Button */}
              <button
                onClick={toggleForm}
                className="bg-white/20 backdrop-blur-sm border border-white/30 text-white px-8 py-3 rounded-full font-medium hover:bg-white/30 transition-all duration-300"
              >
                {isLogin ? 'Register' : 'Login'}
              </button>
            </div>
          </div>

          {/* Right Panel - Form */}
          <div className="lg:w-1/2 p-8 flex flex-col justify-center">
            <div className="w-full max-w-sm mx-auto">
              
              {/* Header */}
              <div className="text-center mb-8">
                <div className="inline-block bg-teal-600 text-white px-4 py-2 rounded-full text-sm font-medium mb-6">
                  TicketResell
                </div>
                <h2 className="text-2xl font-bold text-gray-800 mb-2">
                  {isLogin ? 'Sign in to your account' : 'Create new account'}
                </h2>
                {!isLogin && (
                  <h3 className="text-xl font-semibold text-gray-700">
                    Join the ticket marketplace
                  </h3>
                )}
              </div>

              {/* Form */}
              {isLogin ? <LoginForm /> : <RegisterForm />}

              {/* Social Login */}
              <div className="mt-6">
                <p className="text-center text-gray-600 text-sm mb-4">
                  or continue with social media
                </p>
                <div className="flex justify-center space-x-4">
                  <button className="p-2 border border-gray-300 rounded-full hover:bg-gray-50 transition-colors">
                    <Facebook size={20} className="text-blue-600" />
                  </button>
                  <button className="p-2 border border-gray-300 rounded-full hover:bg-gray-50 transition-colors">
                    <Chrome size={20} className="text-red-500" />
                  </button>
                  <button className="p-2 border border-gray-300 rounded-full hover:bg-gray-50 transition-colors">
                    <Apple size={20} className="text-gray-800" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default LoginPage
