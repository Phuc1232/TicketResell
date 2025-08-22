# Ticket Resell Platform API Documentation

## Overview

This document provides comprehensive documentation for the Ticket Resell Platform API, including all endpoints for ticket purchasing, payment processing, feedback management, notifications, and earnings tracking.

## Base URL
```
http://localhost:6868/api
```

## Authentication

All protected endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## API Endpoints

### 1. Transaction Management

#### 1.1 Initiate Transaction
**POST** `/transactions/initiate`

Initiates a new transaction for ticket purchase.

**Request Body:**
```json
{
  "event_name": "Concert ABC",
  "owner_username": "john_doe",
  "payment_method": "Credit Card",
  "amount": 150.00
}
```

**Response:**
```json
{
  "transaction_id": 456,
  "payment_id": 789,
  "status": "pending",
  "redirect_url": "/api/payments/789/process",
  "message": "Transaction initiated successfully"
}
```

#### 1.2 Complete Ticket Purchase
**POST** `/transactions/buy-ticket`

Complete end-to-end ticket purchase workflow.

**Request Body:**
```json
{
  "event_name": "Concert ABC",
  "owner_username": "john_doe",
  "payment_method": "Credit Card",
  "payment_data": {
    "card_number": "****-****-****-1234",
    "confirmation_code": "ABC123"
  }
}
```

**Response:**
```json
{
  "transaction_id": 456,
  "payment_id": 789,
  "event_name": "Concert ABC",
  "owner_username": "john_doe",
  "status": "success",
  "total_amount": 150.00,
  "seller_earnings": 142.50,
  "commission_amount": 7.50,
  "payment_reference": "CARD_A1B2C3D4",
  "message": "Successfully purchased ticket for Concert ABC"
}
```

### 2. Payment Management

#### 2.1 Create Payment
**POST** `/payments/`

Create a new payment record.

**Request Body:**
```json
{
  "methods": "Credit Card",
  "amount": 150.00,
  "title": "Ticket Purchase - Concert Event",
  "transaction_id": 456
}
```

#### 2.2 Process Payment
**POST** `/payments/{payment_id}/process`

Process payment through payment gateway.

**Request Body:**
```json
{
  "payment_method_data": {
    "card_details": "encrypted_data"
  },
  "confirmation_code": "ABC123"
}
```

#### 2.3 Get Payment History
**GET** `/payments/history?limit=20&offset=0`

Get paginated payment history for current user.

**Response:**
```json
{
  "payments": [
    {
      "payment_id": 789,
      "methods": "Credit Card",
      "status": "success",
      "amount": 150.00,
      "title": "Ticket Purchase - Concert Event",
      "paid_at": "2024-01-15T10:30:00Z",
      "transaction_id": 456
    }
  ],
  "total_count": 25,
  "limit": 20,
  "offset": 0,
  "has_more": true
}
```

#### 2.4 Get Payment Statistics
**GET** `/payments/statistics`

Get comprehensive payment statistics for current user.

**Response:**
```json
{
  "total_payments": 15,
  "successful_payments": 13,
  "failed_payments": 2,
  "pending_payments": 0,
  "total_amount": 2250.00,
  "success_rate": 86.67,
  "method_breakdown": {
    "Credit Card": {"count": 8, "amount": 1200.00},
    "Digital Wallet": {"count": 5, "amount": 750.00}
  }
}
```

### 3. Feedback Management

#### 3.1 Submit User Feedback
**POST** `/feedback/user/{user_id}`

Submit feedback for another user after a transaction.

**Request Body:**
```json
{
  "rating": 4.5,
  "comment": "Great seller, very responsive!",
  "transaction_id": 456
}
```

#### 3.2 Get User Feedback Summary
**GET** `/feedback/user/{user_id}/summary`

Get comprehensive feedback summary for a user.

**Response:**
```json
{
  "user_id": 123,
  "average_rating": 4.3,
  "total_feedback": 25,
  "rating_distribution": {
    "1": 0, "2": 1, "3": 3, "4": 8, "5": 13
  },
  "recent_feedback": [
    {
      "feedback_id": 789,
      "reviewer_name": "john_doe",
      "rating": 5.0,
      "comment": "Excellent transaction!",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "feedback_trend": "improving"
}
```

#### 3.3 Get Feedback Analytics
**GET** `/feedback/user/{user_id}/analytics`

Get detailed feedback analytics including buyer/seller breakdown.

**Response:**
```json
{
  "user_id": 123,
  "buyer_analytics": {
    "average_rating": 4.2,
    "total_feedback": 10,
    "rating_distribution": {"1": 0, "2": 0, "3": 2, "4": 3, "5": 5}
  },
  "seller_analytics": {
    "average_rating": 4.4,
    "total_feedback": 15,
    "rating_distribution": {"1": 0, "2": 1, "3": 1, "4": 5, "5": 8}
  },
  "overall_reputation_score": 87.5
}
```

### 4. Notification Management

#### 4.1 Get User Notifications
**GET** `/notifications/?limit=20&offset=0&unread_only=false`

Get notifications for current user.

**Response:**
```json
{
  "notifications": [
    {
      "notification_id": 123,
      "title": "Purchase Successful",
      "content": "You have successfully purchased a ticket for 'Concert Event' for $150.00",
      "type": "payment_confirmation",
      "is_read": false,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total_count": 45,
  "unread_count": 5
}
```

#### 4.2 Mark Notification as Read
**PUT** `/notifications/{notification_id}/read`

Mark a specific notification as read.

#### 4.3 Get Notification Statistics
**GET** `/notifications/statistics`

Get comprehensive notification statistics.

**Response:**
```json
{
  "user_id": 123,
  "total_notifications": 45,
  "unread_count": 5,
  "read_count": 40,
  "type_breakdown": {
    "payment_confirmation": {"total": 15, "unread": 2},
    "ticket_reminder": {"total": 10, "unread": 1},
    "system": {"total": 20, "unread": 2}
  },
  "recent_activity_count": 8,
  "read_percentage": 88.89
}
```

### 5. Earnings Management

#### 5.1 Get User Earnings
**GET** `/earnings/?limit=50&offset=0`

Get earnings for current user.

**Response:**
```json
{
  "earnings": [
    {
      "earning_id": 123,
      "total_amount": 142.50,
      "date": "2024-01-15T10:30:00Z"
    }
  ],
  "total_count": 25,
  "total_amount": 3562.50,
  "limit": 50,
  "offset": 0,
  "has_more": false
}
```

#### 5.2 Get Earnings Statistics
**GET** `/earnings/statistics`

Get comprehensive earnings statistics.

**Response:**
```json
{
  "user_id": 123,
  "total_earnings": 3562.50,
  "total_transactions": 25,
  "average_earning": 142.50,
  "monthly_earnings": {
    "2024-01": {"amount": 1425.00, "count": 10},
    "2023-12": {"amount": 2137.50, "count": 15}
  },
  "recent_earnings": [
    {
      "earning_id": 123,
      "amount": 142.50,
      "date": "2024-01-15T10:30:00Z"
    }
  ],
  "earnings_trend": "increasing"
}
```

#### 5.3 Get Earnings Summary
**GET** `/earnings/summary?period=month`

Get earnings summary for different time periods.

**Parameters:**
- `period`: `all`, `year`, `month`, `week`

**Response:**
```json
{
  "user_id": 123,
  "period": "month",
  "total_amount": 1425.00,
  "transaction_count": 10,
  "average_amount": 142.50,
  "highest_earning": 285.00,
  "lowest_earning": 47.50,
  "start_date": "2023-12-15T00:00:00Z",
  "end_date": "2024-01-15T00:00:00Z"
}
```

#### 5.4 Calculate Earnings
**POST** `/earnings/calculate`

Calculate potential earnings from transaction amount.

**Request Body:**
```json
{
  "transaction_amount": 150.00,
  "platform_commission": 0.05
}
```

**Response:**
```json
{
  "transaction_amount": 150.00,
  "platform_commission_rate": 0.05,
  "commission_amount": 7.50,
  "seller_earnings": 142.50,
  "net_percentage": 95.0
}
```

## Error Responses

All endpoints return consistent error responses:

```json
{
  "message": "Error description",
  "error": "Detailed error information (in development)",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Common HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Access denied
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict (e.g., ticket already sold)
- `500 Internal Server Error`: Server error

## Rate Limiting

API requests are rate-limited to prevent abuse:
- 100 requests per minute per user for general endpoints
- 10 requests per minute for payment processing endpoints

## Webhooks

The platform supports webhooks for real-time notifications:

### Payment Status Updates
```json
{
  "event": "payment.completed",
  "data": {
    "payment_id": 789,
    "transaction_id": 456,
    "status": "success",
    "amount": 150.00,
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### Transaction Updates
```json
{
  "event": "transaction.completed",
  "data": {
    "transaction_id": 456,
    "ticket_id": 123,
    "buyer_id": 789,
    "seller_id": 456,
    "status": "success",
    "amount": 150.00,
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```
