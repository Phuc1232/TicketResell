# TicketResell API - Swagger UI Setup

## 🚀 Quick Start

### 1. Kiểm tra imports
```bash
cd src
python test_imports.py
```

### 2. Chạy ứng dụng
```bash
cd src
python app.py
```

### 3. Truy cập Swagger UI
Mở trình duyệt và truy cập:
```
http://localhost:6868/docs
```

## 📋 API Endpoints Available

### Authentication
- `POST /api/auth/login` - Đăng nhập
- `POST /api/auth/register` - Đăng ký
- `POST /api/auth/verify` - Xác thực token

### User Management
- `GET /api/users/profile` - Lấy thông tin profile
- `PUT /api/users/profile` - Cập nhật profile
- `PUT /api/users/change-password` - Đổi mật khẩu

### Ticket Management
- `GET /api/tickets` - Lấy danh sách vé
- `POST /api/tickets` - Tạo vé mới
- `GET /api/tickets/{id}` - Lấy chi tiết vé
- `PUT /api/tickets/{id}` - Cập nhật vé
- `DELETE /api/tickets/{id}` - Xóa vé
- `GET /api/tickets/search` - Tìm kiếm vé
- `GET /api/tickets/my-tickets` - Vé của tôi

### Payment Processing
- `POST /api/payments/initiate` - Khởi tạo thanh toán
- `GET /api/payments/status/{payment_id}` - Kiểm tra trạng thái thanh toán
- `POST /api/payments/callback` - Callback từ payment gateway

### Chat Functionality
- `POST /api/chat/send` - Gửi tin nhắn
- `GET /api/chat/messages/{other_user_id}` - Lấy tin nhắn
- `GET /api/chat/conversations` - Lấy danh sách cuộc trò chuyện
- `POST /api/chat/mark-read/{other_user_id}` - Đánh dấu đã đọc

### Notifications
- `GET /api/notifications` - Lấy thông báo
- `POST /api/notifications/{id}/read` - Đánh dấu thông báo đã đọc
- `POST /api/notifications/read-all` - Đánh dấu tất cả đã đọc
- `GET /api/notifications/preferences` - Lấy cài đặt thông báo
- `PUT /api/notifications/preferences` - Cập nhật cài đặt thông báo

### Feedback & Ratings
- `POST /api/feedback/user/{user_id}` - Gửi đánh giá người dùng
- `POST /api/feedback/ticket/{ticket_id}` - Gửi đánh giá vé
- `GET /api/feedback/user/{user_id}` - Lấy đánh giá người dùng
- `GET /api/feedback/ticket/{ticket_id}` - Lấy đánh giá vé

## 🔧 Testing với Swagger UI

### 1. Authentication Test
1. Mở Swagger UI tại `http://localhost:6868/docs`
2. Tìm section "Authentication"
3. Test endpoint `/api/auth/register` với data:
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123",
  "phone_number": "0123456789"
}
```

4. Test endpoint `/api/auth/login` với data:
```json
{
  "email": "test@example.com",
  "password": "password123"
}
```

5. Copy access_token từ response

### 2. Authorized Endpoints Test
1. Click vào nút "Authorize" ở đầu trang Swagger
2. Nhập: `Bearer <your_access_token>`
3. Bây giờ bạn có thể test các endpoints yêu cầu authentication

### 3. Ticket Management Test
1. Test tạo vé mới với `/api/tickets`:
```json
{
  "EventName": "Concert XYZ",
  "EventDate": "2024-03-15T19:00:00Z",
  "Price": 150.00,
  "Status": "Available",
  "ContactInfo": "phone: 0123456789",
  "PaymentMethod": "Digital Wallet"
}
```

2. Test lấy danh sách vé với `/api/tickets`

### 4. Payment Test
1. Test khởi tạo thanh toán với `/api/payments/initiate`:
```json
{
  "ticket_id": 1,
  "payment_method": "Digital Wallet",
  "amount": 150.00
}
```

### 5. Chat Test
1. Test gửi tin nhắn với `/api/chat/send`:
```json
{
  "receiver_id": 2,
  "content": "Hello, is this ticket still available?",
  "ticket_id": 1
}
```

## 🐛 Troubleshooting

### Lỗi Import
Nếu gặp lỗi import, chạy:
```bash
pip install -r requirements.txt
```

### Lỗi Database
Nếu gặp lỗi database, kiểm tra:
1. SQL Server đang chạy
2. Connection string trong `config.py`
3. Database đã được tạo

### Lỗi JWT
Nếu gặp lỗi JWT, kiểm tra:
1. JWT_SECRET_KEY trong `app.py`
2. Token format: `Bearer <token>`

### Lỗi CORS
Nếu gặp lỗi CORS, kiểm tra:
1. CORS configuration trong `cors.py`
2. Allowed origins

## 📁 File Structure

```
src/
├── api/
│   ├── controllers/
│   │   ├── auth_controller.py
│   │   ├── ticket_controller.py
│   │   ├── user_controller.py
│   │   ├── payment_controller.py
│   │   ├── chat_controller.py
│   │   ├── notification_controller.py
│   │   └── feedback_controller.py
│   ├── schemas/
│   │   ├── ticket.py
│   │   └── user.py
│   ├── routes.py
│   └── swagger.py
├── domain/
│   └── models/
├── infrastructure/
│   ├── models/
│   └── repositories/
├── services/
├── app.py
├── config.py
└── requirements.txt
```

## 🔐 Security Notes

- Tất cả endpoints (trừ auth) yêu cầu JWT token
- Token có thời hạn 24 giờ
- Input validation được thực hiện với Marshmallow
- SQL injection protection với SQLAlchemy

## 📞 Support

Nếu gặp vấn đề, kiểm tra:
1. Console logs
2. Swagger UI error messages
3. Network tab trong browser developer tools
