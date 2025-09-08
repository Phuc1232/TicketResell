import React from 'react';
import { Link } from 'react-router-dom';
import { FiArrowRight, FiShield, FiDollarSign, FiUsers } from 'react-icons/fi';
import PublicLayout from '../components/PublicLayout';

const Home = () => {
  return (
    <PublicLayout>
      <div className="max-w-6xl w-full text-center">
        {/* Hero Section */}
        <section className="mb-20">
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6 leading-tight">
            Mua & Bán Vé Sự Kiện
            <br />
            An Toàn & Bảo Mật
          </h1>
          <p className="text-xl text-white/90 mb-10 max-w-2xl mx-auto">
            Nền tảng đáng tin cậy nhất cho việc bán lại vé. Kết nối với người mua và người bán đã được xác minh, 
            thanh toán an toàn và không bỏ lỡ sự kiện yêu thích.
          </p>
          <div className="flex gap-4 justify-center flex-wrap">
            <Link
              to="/register"
              className="inline-flex items-center gap-2 px-8 py-4 bg-white text-blue-600 rounded-xl 
                       font-semibold text-lg transition-all duration-300 hover:-translate-y-1 
                       hover:shadow-2xl shadow-lg"
            >
              Bắt Đầu
              <FiArrowRight />
            </Link>
            <Link
              to="/login"
              className="inline-flex items-center gap-2 px-8 py-4 bg-white/20 text-white rounded-xl 
                       font-semibold text-lg border-2 border-white/30 backdrop-blur-sm
                       transition-all duration-300 hover:bg-white/30"
            >
              Đăng Nhập
            </Link>
          </div>
        </section>

        {/* Features Section */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-10 mb-20">
          <div className="bg-white/10 backdrop-blur-lg border border-white/20 rounded-2xl p-8 text-center 
                         transition-transform duration-300 hover:-translate-y-2">
            <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-6">
              <FiShield className="w-8 h-8 text-white" />
            </div>
            <h3 className="text-2xl font-semibold text-white mb-4">Giao Dịch An Toàn</h3>
            <p className="text-white/80 leading-relaxed">
              Tất cả thanh toán được xử lý an toàn với bảo vệ người mua và xác minh người bán 
              để đảm bảo giao dịch an toàn.
            </p>
          </div>

          <div className="bg-white/10 backdrop-blur-lg border border-white/20 rounded-2xl p-8 text-center 
                         transition-transform duration-300 hover:-translate-y-2">
            <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-6">
              <FiDollarSign className="w-8 h-8 text-white" />
            </div>
            <h3 className="text-2xl font-semibold text-white mb-4">Giá Cạnh Tranh</h3>
            <p className="text-white/80 leading-relaxed">
              Định giá công bằng và minh bạch với phí nền tảng thấp. Theo dõi thu nhập và 
              tối đa hóa lợi nhuận của bạn.
            </p>
          </div>

          <div className="bg-white/10 backdrop-blur-lg border border-white/20 rounded-2xl p-8 text-center 
                         transition-transform duration-300 hover:-translate-y-2">
            <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-6">
              <FiUsers className="w-8 h-8 text-white" />
            </div>
            <h3 className="text-2xl font-semibold text-white mb-4">Cộng Đồng Tin Cậy</h3>
            <p className="text-white/80 leading-relaxed">
              Tham gia cùng hàng nghìn người dùng đã được xác minh. Đọc đánh giá, kiểm tra 
              xếp hạng và xây dựng uy tín trong cộng đồng.
            </p>
          </div>
        </section>

        {/* Stats Section */}
        <section className="grid grid-cols-2 md:grid-cols-4 gap-8">
          <div className="text-center">
            <div className="text-5xl font-bold text-white mb-2">10K+</div>
            <div className="text-white/80 text-lg">Người Dùng Hoạt Động</div>
          </div>
          <div className="text-center">
            <div className="text-5xl font-bold text-white mb-2">50K+</div>
            <div className="text-white/80 text-lg">Vé Đã Bán</div>
          </div>
          <div className="text-center">
            <div className="text-5xl font-bold text-white mb-2">99.9%</div>
            <div className="text-white/80 text-lg">Tỷ Lệ Thành Công</div>
          </div>
          <div className="text-center">
            <div className="text-5xl font-bold text-white mb-2">24/7</div>
            <div className="text-white/80 text-lg">Hỗ Trợ</div>
          </div>
        </section>
      </div>
    </PublicLayout>
  );
};

export default Home;
