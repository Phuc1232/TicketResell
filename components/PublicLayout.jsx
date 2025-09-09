import React from 'react';
import { Link } from 'react-router-dom';

const PublicLayout = ({ children }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-800">
      {/* Header */}
      <header className="bg-white/10 backdrop-blur-lg border-b border-white/20 py-4">
        <div className="max-w-6xl mx-auto px-6 flex justify-between items-center">
          <Link 
            to="/" 
            className="text-2xl font-bold text-white hover:text-white/90 transition-colors duration-200"
          >
            TicketResell
          </Link>
          <nav className="flex gap-6 items-center">
            <Link 
              to="/login" 
              className="text-white font-medium hover:text-white/80 transition-opacity duration-200"
            >
              Đăng Nhập
            </Link>
            <Link 
              to="/register" 
              className="text-white font-medium hover:text-white/80 transition-opacity duration-200"
            >
              Đăng Ký
            </Link>
          </nav>
        </div>
      </header>
      
      {/* Main Content */}
      <main className="min-h-[calc(100vh-80px)] flex items-center justify-center py-10 px-6">
        {children}
      </main>
    </div>
  );
};

export default PublicLayout;
