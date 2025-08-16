from typing import List, Optional
from domain.models.notification import Notification
from domain.models.inotification_repository import INotificationRepository
from domain.models.iuser_repository import IUserRepository
from datetime import datetime

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
