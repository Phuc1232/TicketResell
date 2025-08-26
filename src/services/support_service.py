from typing import List, Optional
from domain.models.support import Support
from domain.models.isupport_repository import ISupportRepository
from domain.models.iuser_repository import IUserRepository
from datetime import datetime
from services.email_service import EmailService
import logging

logger = logging.getLogger(__name__)

class SupportService:
    def __init__(self, support_repository: ISupportRepository, user_repository: IUserRepository, email_service: Optional[EmailService] = None):
        self.support_repository = support_repository
        self.user_repository = user_repository
        self.email_service = email_service or EmailService()
    
    def create_support_ticket(self, user_id: int, title: str, issue_description: str = None, recipient_type: str = 'admin', recipient_id: Optional[int] = None) -> Support:
        # Validate user exists
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Create support ticket
        support = Support(
            SupportID=None,
            UserID=user_id,
            Status='open',
            Create_at=datetime.now(),
            Updated_at=None,
            Issue_des=issue_description,
            Title=title,
            RecipientType=recipient_type,
            RecipientID=recipient_id
        )
        
        # Add the support ticket to the database
        created_support = self.support_repository.add(support)
        
        # Send notification to admin
        try:
            # Get admin users (assuming role_id 1 is admin)
            admin_users = self.user_repository.get_by_role_id(1)
            
            if admin_users:
                for admin in admin_users:
                    self._send_admin_notification(admin.email, admin.username, user.username, created_support)
            else:
                logger.warning("No admin users found to notify about new support ticket")
        except Exception as e:
            logger.error(f"Failed to send admin notification for support ticket: {e}")
        
        return created_support
    
    def get_support_ticket(self, support_id: int) -> Optional[Support]:
        return self.support_repository.get_by_id(support_id)
    
    def get_user_support_tickets(self, user_id: int) -> List[Support]:
        # Validate user exists
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        return self.support_repository.get_by_user_id(user_id)
    
    def get_all_support_tickets(self) -> List[Support]:
        """Get all support tickets (admin function)"""
        return self.support_repository.get_all()
    
    def get_support_tickets_by_status(self, status: str) -> List[Support]:
        """Get support tickets by status"""
        valid_statuses = ['open', 'in_progress', 'resolved', 'closed']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")
        
        return self.support_repository.get_by_status(status)
    
    def update_support_ticket(self, support_id: int, title: str = None, issue_description: str = None, status: str = None) -> Optional[Support]:
        support = self.support_repository.get_by_id(support_id)
        if not support:
            return None
        
        if title:
            support.Title = title
        if issue_description:
            support.Issue_des = issue_description
        if status:
            valid_statuses = ['open', 'in_progress', 'resolved', 'closed']
            if status not in valid_statuses:
                raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")
            support.Status = status
        
        support.Updated_at = datetime.now()
        
        return self.support_repository.update(support)
    
    def update_support_status(self, support_id: int, status: str) -> bool:
        """Update only the status of a support ticket"""
        valid_statuses = ['open', 'in_progress', 'resolved', 'closed']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")
        
        support = self.support_repository.get_by_id(support_id)
        if not support:
            return False
        
        return self.support_repository.update_status(support_id, status)
    
    def delete_support_ticket(self, support_id: int) -> bool:
        support = self.support_repository.get_by_id(support_id)
        if not support:
            return False
        
        return self.support_repository.delete(support_id)
    
    def close_support_ticket(self, support_id: int) -> bool:
        """Close a support ticket"""
        return self.update_support_status(support_id, 'closed')
    
    def resolve_support_ticket(self, support_id: int) -> bool:
        """Mark a support ticket as resolved"""
        return self.update_support_status(support_id, 'resolved')
    
    def _send_admin_notification(self, admin_email: str, admin_name: str, username: str, support: Support) -> bool:
        """Send notification email to admin about new support ticket"""
        subject = f"New Support Ticket: {support.Title}"
        
        # HTML email template
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>New Support Ticket</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; background-color: #f9f9f9; }}
                .ticket-info {{ padding: 15px; background-color: white; border: 1px solid #ddd; margin: 20px 0; }}
                .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>New Support Ticket</h1>
                </div>
                <div class="content">
                    <h2>Hello {admin_name},</h2>
                    <p>A new support ticket has been created and requires your attention.</p>
                    
                    <div class="ticket-info">
                        <p><strong>Ticket ID:</strong> {support.SupportID}</p>
                        <p><strong>User:</strong> {username}</p>
                        <p><strong>Title:</strong> {support.Title}</p>
                        <p><strong>Description:</strong> {support.Issue_des or 'No description provided'}</p>
                        <p><strong>Status:</strong> {support.Status}</p>
                        <p><strong>Created:</strong> {support.Create_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </div>
                    
                    <p>Please review this ticket at your earliest convenience.</p>
                    
                    <p>Best regards,<br>The TicketResell System</p>
                </div>
                <div class="footer">
                    <p>This is an automated message. Please do not reply to this email.</p>
                    <p>&copy; 2024 TicketResell. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version for email clients that don't support HTML
        text_body = f"""
        Hello {admin_name},

        A new support ticket has been created and requires your attention.

        Ticket ID: {support.SupportID}
        User: {username}
        Title: {support.Title}
        Description: {support.Issue_des or 'No description provided'}
        Status: {support.Status}
        Created: {support.Create_at.strftime('%Y-%m-%d %H:%M:%S')}

        Please review this ticket at your earliest convenience.

        Best regards,
        The TicketResell System
        """
        
        try:
            result = self.email_service._send_email(admin_email, subject, text_body, html_body)
            if result:
                logger.info(f"Admin notification sent successfully to {admin_email} for support ticket {support.SupportID}")
            else:
                logger.warning(f"Failed to send admin notification to {admin_email} for support ticket {support.SupportID}")
            return result
        except Exception as e:
            logger.error(f"Error sending admin notification: {e}")
            return False
