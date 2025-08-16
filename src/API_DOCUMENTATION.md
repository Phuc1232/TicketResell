# TicketResell API Documentation

## Overview
TicketResell là nền tảng bán lại vé chưa sử dụng với các tính năng toàn diện để đảm bảo giao dịch an toàn và hiệu quả.

## Base URL
```
http://localhost:5000/api
```

## Authentication
Tất cả API endpoints (trừ auth) yêu cầu JWT token trong header:
```
Authorization: Bearer <your_jwt_token>
```

---

## 1. Authentication APIs

### 1.1 Đăng ký người dùng
```
POST /auth/register
```

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password",
  "phone_number": "0123456789"
}
```

### 1.2 Đăng nhập
```
POST /auth/login
```

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "secure_password"
}
```

---

## 2. User Management APIs

### 2.1 Lấy thông tin người dùng
```
GET /users/profile
```

### 2.2 Cập nhật thông tin người dùng
```
PUT /users/profile
```

**Request Body:**
```json
{
  "username": "john_doe_updated",
  "phone_number": "0987654321"
}
```

### 2.3 Đổi mật khẩu
```
PUT /users/change-password
```

**Request Body:**
```json
{
  "current_password": "old_password",
  "new_password": "new_secure_password"
}
```

---

## 3. Ticket Management APIs

### 3.1 Tạo vé mới
```
POST /tickets
```

**Request Body:**
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

### 3.2 Lấy danh sách vé
```
GET /tickets
```

**Query Parameters:**
- `limit`: Số lượng vé (default: 20)
- `offset`: Số vé bỏ qua (default: 0)

### 3.3 Lấy chi tiết vé
```
GET /tickets/{ticket_id}
```

### 3.4 Cập nhật vé
```
PUT /tickets/{ticket_id}
```

### 3.5 Xóa vé
```
DELETE /tickets/{ticket_id}
```

### 3.6 Tìm kiếm vé
```
GET /tickets/search?event_name=concert
```

### 3.7 Tìm kiếm nâng cao
```
GET /tickets/search/advanced?event_type=Concert&min_price=100&max_price=200
```

### 3.8 Lấy vé của tôi
```
GET /tickets/my-tickets
```

---

## 4. Payment Processing APIs

### 4.1 Khởi tạo thanh toán
```
POST /payments/initiate
```

**Request Body:**
```json
{
  "ticket_id": 1,
  "payment_method": "Digital Wallet",
  "amount": 150.00
}
```

### 4.2 Kiểm tra trạng thái thanh toán
```
GET /payments/status/{payment_id}
```

### 4.3 Callback từ Payment Gateway
```
POST /payments/callback
```

---

## 5. Chat Functionality APIs

### 5.1 Gửi tin nhắn
```
POST /chat/send
```

**Request Body:**
```json
{
  "receiver_id": 2,
  "content": "Hello, is this ticket still available?",
  "ticket_id": 1
}
```

### 5.2 Lấy tin nhắn với người dùng
```
GET /chat/messages/{other_user_id}
```

**Query Parameters:**
- `limit`: Số tin nhắn (default: 50)
- `offset`: Số tin nhắn bỏ qua (default: 0)

### 5.3 Lấy danh sách cuộc trò chuyện
```
GET /chat/conversations
```

### 5.4 Đánh dấu tin nhắn đã đọc
```
POST /chat/mark-read/{other_user_id}
```

---

## 6. Notification APIs

### 6.1 Lấy thông báo
```
GET /notifications
```

**Query Parameters:**
- `limit`: Số thông báo (default: 20)
- `offset`: Số thông báo bỏ qua (default: 0)
- `unread_only`: Chỉ lấy thông báo chưa đọc (default: false)

### 6.2 Đánh dấu thông báo đã đọc
```
POST /notifications/{notification_id}/read
```

### 6.3 Đánh dấu tất cả thông báo đã đọc
```
POST /notifications/read-all
```

### 6.4 Lấy cài đặt thông báo
```
GET /notifications/preferences
```

### 6.5 Cập nhật cài đặt thông báo
```
PUT /notifications/preferences
```

**Request Body:**
```json
{
  "email_notifications": true,
  "push_notifications": true,
  "ticket_reminders": true,
  "price_alerts": true,
  "chat_notifications": true
}
```

---

## 7. Feedback & Rating APIs

### 7.1 Gửi đánh giá người dùng
```
POST /feedback/user/{target_user_id}
```

**Request Body:**
```json
{
  "rating": 5.0,
  "comment": "Great seller, very responsive!",
  "transaction_id": 1
}
```

### 7.2 Gửi đánh giá vé
```
POST /feedback/ticket/{ticket_id}
```

**Request Body:**
```json
{
  "rating": 4.5,
  "comment": "Great event, ticket was as described"
}
```

### 7.3 Lấy đánh giá người dùng
```
GET /feedback/user/{user_id}
```

**Query Parameters:**
- `limit`: Số đánh giá (default: 20)
- `offset`: Số đánh giá bỏ qua (default: 0)

### 7.4 Lấy đánh giá vé
```
GET /feedback/ticket/{ticket_id}
```

---

## Response Formats

### Success Response
```json
{
  "message": "Operation completed successfully",
  "data": {...}
}
```

### Error Response
```json
{
  "message": "Error description",
  "errors": {
    "field_name": ["Error details"]
  }
}
```

---

## Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `409` - Conflict
- `500` - Internal Server Error

---

## Rate Limiting

API có giới hạn rate limiting để đảm bảo hiệu suất:
- 100 requests per minute cho authenticated users
- 20 requests per minute cho unauthenticated users

---

## WebSocket Endpoints (Real-time Features)

### Chat Real-time
```
ws://localhost:5000/ws/chat/{user_id}
```

### Notifications Real-time
```
ws://localhost:5000/ws/notifications/{user_id}
```

---

## Testing

### Swagger Documentation
```
http://localhost:5000/swagger
```

### Health Check
```
GET /health
```

---

## Security Features

1. **JWT Authentication** - Tất cả API yêu cầu token hợp lệ
2. **Input Validation** - Tất cả input được validate nghiêm ngặt
3. **SQL Injection Protection** - Sử dụng parameterized queries
4. **CORS Protection** - Chỉ cho phép domain được cấu hình
5. **Rate Limiting** - Giới hạn số request để tránh spam

---

## Error Handling

Tất cả API endpoints đều có error handling toàn diện:
- Validation errors
- Authentication errors
- Authorization errors
- Database errors
- Network errors

---

## Monitoring & Logging

- Tất cả API calls được log
- Performance metrics được track
- Error tracking và alerting
- User activity monitoring
