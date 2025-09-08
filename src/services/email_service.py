import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class EmailService:
    """
    Email Service for sending verification emails
    Supports both SMTP and SendGrid (can be extended)
    """
    
    def __init__(self):
        # Email configuration from environment variables
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@ticketresell.com')
        self.from_name = os.getenv('FROM_NAME', 'TicketResell')
        
        # For development/testing - set to True to skip actual email sending
        # Default to True for development unless explicitly configured
        self.debug_mode = os.getenv('EMAIL_DEBUG_MODE', 'True').lower() == 'true'

        # Check if SMTP is properly configured
        self.smtp_configured = bool(self.smtp_username and self.smtp_password)

        # Auto-enable debug mode if SMTP not configured
        if not self.smtp_configured:
            self.debug_mode = True
            logger.info("SMTP not configured - enabling debug mode")
    
    def send_verification_email(self, to_email: str, username: str, verification_code: str) -> bool:
        """
        Send verification email with 6-digit code
        
        Args:
            to_email: Recipient email address
            username: User's username for personalization
            verification_code: 6-digit verification code
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        subject = "Verify Your TicketResell Account"
        
        # HTML email template
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Verify Your Account</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; background-color: #f9f9f9; }}
                .verification-code {{ 
                    font-size: 32px; 
                    font-weight: bold; 
                    color: #007bff; 
                    text-align: center; 
                    padding: 20px; 
                    background-color: white; 
                    border: 2px dashed #007bff; 
                    margin: 20px 0; 
                }}
                .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
                .warning {{ color: #dc3545; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to TicketResell!</h1>
                </div>
                <div class="content">
                    <h2>Hi {username},</h2>
                    <p>Thank you for registering with TicketResell! To complete your account setup, please verify your email address using the code below:</p>
                    
                    <div class="verification-code">
                        {verification_code}
                    </div>
                    
                    <p>Enter this code in the verification page to activate your account.</p>
                    
                    <p class="warning">WARNING: This code will expire in 5 minutes for security reasons.</p>
                    
                    <p>If you didn't create an account with TicketResell, please ignore this email.</p>
                    
                    <p>Best regards,<br>The TicketResell Team</p>
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
        Hi {username},

        Thank you for registering with TicketResell!

        Your verification code is: {verification_code}

        Please enter this code in the verification page to activate your account.
        This code will expire in 5 minutes.

        If you didn't create an account with TicketResell, please ignore this email.

        Best regards,
        The TicketResell Team
        """
        
        return self._send_email(to_email, subject, text_body, html_body)
    
    def send_password_reset_email(self, to_email: str, username: str, reset_token: str) -> bool:
        """
        Send password reset email with reset link
        
        Args:
            to_email: Recipient email address
            username: User's username
            reset_token: Password reset token
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        subject = "Reset Your TicketResell Password"
        
        # In production, this should be your frontend URL
        reset_url = f"https://ticketresell.com/reset-password?token={reset_token}"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Reset Your Password</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #dc3545; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; background-color: #f9f9f9; }}
                .button {{ 
                    display: inline-block; 
                    padding: 12px 24px; 
                    background-color: #dc3545; 
                    color: white; 
                    text-decoration: none; 
                    border-radius: 5px; 
                    margin: 20px 0; 
                }}
                .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
                .warning {{ color: #dc3545; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Password Reset Request</h1>
                </div>
                <div class="content">
                    <h2>Hi {username},</h2>
                    <p>We received a request to reset your TicketResell account password.</p>
                    
                    <p>Click the button below to reset your password:</p>
                    <a href="{reset_url}" class="button">Reset Password</a>
                    
                    <p>Or copy and paste this link into your browser:</p>
                    <p>{reset_url}</p>
                    
                    <p class="warning">This link will expire in 15 minutes for security reasons.</p>
                    
                    <p>If you didn't request a password reset, please ignore this email. Your password will remain unchanged.</p>
                    
                    <p>Best regards,<br>The TicketResell Team</p>
                </div>
                <div class="footer">
                    <p>This is an automated message. Please do not reply to this email.</p>
                    <p>&copy; 2024 TicketResell. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Hi {username},

        We received a request to reset your TicketResell account password.

        Please click the following link to reset your password:
        {reset_url}

        This link will expire in 15 minutes.

        If you didn't request a password reset, please ignore this email.

        Best regards,
        The TicketResell Team
        """
        
        return self._send_email(to_email, subject, text_body, html_body)
    
    def _send_email(self, to_email: str, subject: str, text_body: str, html_body: Optional[str] = None) -> bool:
        """
        Internal method to send email via SMTP
        
        Args:
            to_email: Recipient email
            subject: Email subject
            text_body: Plain text body
            html_body: HTML body (optional)
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        if self.debug_mode:
            logger.info(f"[EMAIL DEBUG] Would send email to {to_email}")
            logger.info(f"[EMAIL DEBUG] Subject: {subject}")
            logger.info(f"[EMAIL DEBUG] Text Body: {text_body[:200]}...")
            if html_body:
                logger.info(f"[EMAIL DEBUG] HTML Body: {len(html_body)} characters")
            logger.info("[EMAIL DEBUG] Email sending simulated successfully")
            return True

        # Log email configuration for debugging
        logger.info(f"[EMAIL] Attempting to send email to: {to_email}")
        logger.info(f"[EMAIL] SMTP Server: {self.smtp_server}:{self.smtp_port}")
        logger.info(f"[EMAIL] SMTP Username: {self.smtp_username}")
        logger.info(f"[EMAIL] From Email: {self.from_email}")
        logger.info(f"[EMAIL] Debug Mode: {self.debug_mode}")
        logger.info(f"[EMAIL] SMTP Configured: {self.smtp_configured}")

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            # Add text part
            text_part = MIMEText(text_body, 'plain')
            msg.attach(text_part)
            
            # Add HTML part if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Send email
            logger.info(f"[EMAIL] Connecting to SMTP server...")
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                logger.info(f"[EMAIL] Starting TLS...")
                server.starttls()
                logger.info(f"[EMAIL] Logging in with username: {self.smtp_username}")
                server.login(self.smtp_username, self.smtp_password)
                logger.info(f"[EMAIL] Sending message...")
                server.send_message(msg)

            logger.info(f"[EMAIL] Email sent successfully to {to_email}")
            return True

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"[EMAIL] SMTP Authentication failed: {str(e)}")
            logger.error(f"[EMAIL] Check username/password for: {self.smtp_username}")
            return False
        except smtplib.SMTPRecipientsRefused as e:
            logger.error(f"[EMAIL] Recipients refused: {str(e)}")
            return False
        except smtplib.SMTPServerDisconnected as e:
            logger.error(f"[EMAIL] SMTP server disconnected: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"[EMAIL] Failed to send email to {to_email}: {str(e)}")
            logger.error(f"[EMAIL] Error type: {type(e).__name__}")
            return False
    
    def get_config_status(self) -> dict:
        """
        Get email service configuration status

        Returns:
            dict: Configuration status information
        """
        return {
            "debug_mode": self.debug_mode,
            "smtp_configured": self.smtp_configured,
            "smtp_server": self.smtp_server,
            "smtp_port": self.smtp_port,
            "smtp_username": "***" if self.smtp_username else None,
            "smtp_password": "***" if self.smtp_password else None,
            "from_email": self.from_email,
            "from_name": self.from_name
        }

    def test_connection(self) -> bool:
        """
        Test SMTP connection

        Returns:
            bool: True if connection successful, False otherwise
        """
        if self.debug_mode:
            logger.info("[EMAIL DEBUG] Connection test - Debug mode enabled")
            return True

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
            logger.info("SMTP connection test successful")
            return True
        except Exception as e:
            logger.error(f"SMTP connection test failed: {str(e)}")
            return False
