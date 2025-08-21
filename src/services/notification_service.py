from typing import List, Optional, Dict, Any
from domain.models.notification import Notification
from domain.models.inotification_repository import INotificationRepository
from domain.models.iuser_repository import IUserRepository
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, notification_repository: INotificationRepository, user_repository: IUserRepository):
        self.notification_repository = notification_repository
        self.user_repository = user_repository
    
    def create_notification(self, user_id: int, title: str, content: str, notification_type: str) -> Notification:
        # Validate user exists
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Validate notification type
        valid_types = ['ticket_reminder', 'price_alert', 'chat_message', 'payment_confirmation', 'system']
        if notification_type not in valid_types:
            raise ValueError(f"Invalid notification type. Must be one of: {valid_types}")
        
        # Create notification
        notification = Notification(
            NotificationID=None,
            UserID=user_id,
            Title=title,
            Content=content,
            Type=notification_type,
            IsRead=False,
            CreatedAt=datetime.now(),
            ReadAt=None
        )
        
        return self.notification_repository.add(notification)
    
    def get_user_notifications(self, user_id: int, limit: int = 20, offset: int = 0, unread_only: bool = False) -> List[Notification]:
        # Validate user exists
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        return self.notification_repository.get_by_user_id(user_id, limit, offset, unread_only)
    
    def mark_notification_as_read(self, notification_id: int, user_id: int) -> bool:
        # Validate user exists
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Check if notification belongs to user
        notification = self.notification_repository.get_by_id(notification_id)
        if not notification or notification.UserID != user_id:
            raise ValueError("Notification not found or access denied")
        
        return self.notification_repository.mark_as_read(notification_id)
    
    def mark_all_notifications_as_read(self, user_id: int) -> bool:
        # Validate user exists
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        return self.notification_repository.mark_all_as_read(user_id)
    
    def get_unread_count(self, user_id: int) -> int:
        # Validate user exists
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        return self.notification_repository.get_unread_count(user_id)
    
    def delete_notification(self, notification_id: int, user_id: int) -> bool:
        # Validate user exists
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Check if notification belongs to user
        notification = self.notification_repository.get_by_id(notification_id)
        if not notification or notification.UserID != user_id:
            raise ValueError("Notification not found or access denied")
        
        return self.notification_repository.delete(notification_id)
    
    def create_ticket_reminder(self, user_id: int, ticket_name: str, days_until_event: int) -> Notification:
        title = "Ticket Reminder"
        content = f"Your ticket for '{ticket_name}' expires in {days_until_event} days"
        return self.create_notification(user_id, title, content, "ticket_reminder")
    
    def create_price_alert(self, user_id: int, event_name: str) -> Notification:
        title = "Price Alert"
        content = f"A ticket matching your search criteria for '{event_name}' is now available"
        return self.create_notification(user_id, title, content, "price_alert")
    
    def create_chat_message_notification(self, user_id: int, sender_name: str) -> Notification:
        title = "New Message"
        content = f"You have a new message from {sender_name}"
        return self.create_notification(user_id, title, content, "chat_message")
    
    def create_payment_confirmation(self, user_id: int, amount: float, event_name: str) -> Notification:
        title = "Payment Confirmation"
        content = f"Your payment of ${amount:.2f} for '{event_name}' has been confirmed"
        return self.create_notification(user_id, title, content, "payment_confirmation")

    def create_transaction_notification(self, user_id: int, transaction_type: str, event_name: str, amount: float) -> Notification:
        """Create notification for transaction events"""
        if transaction_type == "purchase_success":
            title = "Purchase Successful"
            content = f"You have successfully purchased a ticket for '{event_name}' for ${amount:.2f}"
        elif transaction_type == "sale_success":
            title = "Ticket Sold"
            content = f"Your ticket for '{event_name}' has been sold for ${amount:.2f}"
        elif transaction_type == "purchase_failed":
            title = "Purchase Failed"
            content = f"Your purchase attempt for '{event_name}' failed. Please try again."
        elif transaction_type == "refund_processed":
            title = "Refund Processed"
            content = f"Your refund of ${amount:.2f} for '{event_name}' has been processed"
        else:
            title = "Transaction Update"
            content = f"Transaction update for '{event_name}'"

        return self.create_notification(user_id, title, content, "payment_confirmation")

    def create_feedback_notification(self, user_id: int, reviewer_name: str, rating: float) -> Notification:
        """Create notification when user receives feedback"""
        title = "New Feedback Received"
        content = f"{reviewer_name} left you a {rating}-star rating"
        return self.create_notification(user_id, title, content, "system")

    def create_ticket_status_notification(self, user_id: int, ticket_name: str, status: str) -> Notification:
        """Create notification for ticket status changes"""
        title = "Ticket Status Update"
        if status == "sold":
            content = f"Your ticket for '{ticket_name}' has been sold"
        elif status == "reserved":
            content = f"Your ticket for '{ticket_name}' has been reserved"
        elif status == "cancelled":
            content = f"Your ticket for '{ticket_name}' has been cancelled"
        else:
            content = f"Your ticket for '{ticket_name}' status has been updated to {status}"

        return self.create_notification(user_id, title, content, "system")

    def get_notification_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get notification statistics for user"""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        # Get all notifications for user
        all_notifications = self.notification_repository.get_by_user_id(user_id, limit=1000, offset=0)

        total_notifications = len(all_notifications)
        unread_count = len([n for n in all_notifications if not n.IsRead])
        read_count = total_notifications - unread_count

        # Notifications by type
        type_breakdown = {}
        for notification in all_notifications:
            notification_type = notification.Type
            if notification_type not in type_breakdown:
                type_breakdown[notification_type] = {'total': 0, 'unread': 0}
            type_breakdown[notification_type]['total'] += 1
            if not notification.IsRead:
                type_breakdown[notification_type]['unread'] += 1

        # Recent activity (last 7 days)
        seven_days_ago = datetime.now() - timedelta(days=7)
        recent_notifications = [n for n in all_notifications if n.CreatedAt >= seven_days_ago]

        return {
            'user_id': user_id,
            'total_notifications': total_notifications,
            'unread_count': unread_count,
            'read_count': read_count,
            'type_breakdown': type_breakdown,
            'recent_activity_count': len(recent_notifications),
            'read_percentage': (read_count / total_notifications * 100) if total_notifications > 0 else 0
        }

    def bulk_create_notifications(self, notifications_data: List[Dict[str, Any]]) -> List[Notification]:
        """Create multiple notifications at once"""
        created_notifications = []

        for data in notifications_data:
            try:
                notification = self.create_notification(
                    user_id=data['user_id'],
                    title=data['title'],
                    content=data['content'],
                    notification_type=data['type']
                )
                created_notifications.append(notification)
                logger.info(f"Created notification for user {data['user_id']}: {data['title']}")
            except Exception as e:
                logger.error(f"Failed to create notification for user {data.get('user_id')}: {e}")
                continue

        return created_notifications

    def cleanup_old_notifications(self, days_old: int = 30) -> int:
        """Clean up notifications older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        deleted_count = self.notification_repository.delete_older_than(cutoff_date)
        logger.info(f"Cleaned up {deleted_count} notifications older than {days_old} days")
        return deleted_count

    def get_notifications_by_type(self, user_id: int, notification_type: str, limit: int = 20, offset: int = 0) -> List[Notification]:
        """Get notifications of specific type for user"""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        return self.notification_repository.get_by_type(user_id, notification_type, limit, offset)
