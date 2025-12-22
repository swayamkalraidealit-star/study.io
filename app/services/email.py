import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending emails via SMTP"""
    
    @staticmethod
    async def send_verification_email(email: str, token: str) -> bool:
        """
        Send email verification link to user
        
        Args:
            email: Recipient email address
            token: Verification token
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Check if SMTP is configured
            if not all([settings.SMTP_HOST, settings.SMTP_USER, settings.SMTP_PASSWORD, settings.EMAIL_FROM]):
                logger.error("SMTP configuration is incomplete. Please set SMTP_HOST, SMTP_USER, SMTP_PASSWORD, and EMAIL_FROM in .env")
                return False
            
            # Create verification link
            verification_link = f"{settings.FRONTEND_URL}/verify-email?token={token}"
            
            # Create email message
            message = MIMEMultipart("alternative")
            message["Subject"] = "Verify Your Email - Study.io"
            message["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>"
            message["To"] = email
            
            # Create HTML content
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .button {{
                        display: inline-block;
                        padding: 12px 24px;
                        background-color: #4F46E5;
                        color: white;
                        text-decoration: none;
                        border-radius: 5px;
                        margin: 20px 0;
                    }}
                    .footer {{
                        margin-top: 30px;
                        font-size: 12px;
                        color: #666;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>Welcome to Study.io!</h2>
                    <p>Thank you for registering. Please verify your email address to complete your registration and start using Study.io.</p>
                    
                    <a href="{verification_link}" class="button">Verify Email Address</a>
                    
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #4F46E5;">{verification_link}</p>
                    
                    <p>This link will expire in 24 hours.</p>
                    
                    <div class="footer">
                        <p>If you didn't create an account with Study.io, you can safely ignore this email.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Create plain text alternative
            text_content = f"""
            Welcome to Study.io!
            
            Thank you for registering. Please verify your email address to complete your registration.
            
            Click the link below to verify your email:
            {verification_link}
            
            This link will expire in 24 hours.
            
            If you didn't create an account with Study.io, you can safely ignore this email.
            """
            
            # Attach both versions
            part1 = MIMEText(text_content, "plain")
            part2 = MIMEText(html_content, "html")
            message.attach(part1)
            message.attach(part2)
            
            # Send email
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(message)
            
            logger.info(f"Verification email sent to {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send verification email to {email}: {str(e)}")
            return False
    
    @staticmethod
    async def send_password_reset_email(email: str, token: str) -> bool:
        """
        Send password reset link to user
        
        Args:
            email: Recipient email address
            token: Password reset token
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Check if SMTP is configured
            if not all([settings.SMTP_HOST, settings.SMTP_USER, settings.SMTP_PASSWORD, settings.EMAIL_FROM]):
                logger.error("SMTP configuration is incomplete. Please set SMTP_HOST, SMTP_USER, SMTP_PASSWORD, and EMAIL_FROM in .env")
                return False
            
            # Create password reset link
            reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
            
            # Create email message
            message = MIMEMultipart("alternative")
            message["Subject"] = "Reset Your Password - Study.io"
            message["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>"
            message["To"] = email
            
            # Create HTML content
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .button {{
                        display: inline-block;
                        padding: 12px 24px;
                        background-color: #4F46E5;
                        color: white;
                        text-decoration: none;
                        border-radius: 5px;
                        margin: 20px 0;
                    }}
                    .footer {{
                        margin-top: 30px;
                        font-size: 12px;
                        color: #666;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>Reset Your Password</h2>
                    <p>We received a request to reset your password for your Study.io account.</p>
                    
                    <a href="{reset_link}" class="button">Reset Password</a>
                    
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #4F46E5;">{reset_link}</p>
                    
                    <p>This link will expire in 1 hour.</p>
                    
                    <div class="footer">
                        <p>If you didn't request a password reset, you can safely ignore this email. Your password will not be changed.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Create plain text alternative
            text_content = f"""
            Reset Your Password
            
            We received a request to reset your password for your Study.io account.
            
            Click the link below to reset your password:
            {reset_link}
            
            This link will expire in 1 hour.
            
            If you didn't request a password reset, you can safely ignore this email. Your password will not be changed.
            """
            
            # Attach both versions
            part1 = MIMEText(text_content, "plain")
            part2 = MIMEText(html_content, "html")
            message.attach(part1)
            message.attach(part2)
            
            # Send email
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(message)
            
            logger.info(f"Password reset email sent to {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send password reset email to {email}: {str(e)}")
            return False
    
    @staticmethod
    async def send_test_email(email: str) -> bool:
        """
        Send a test email to verify SMTP configuration
        
        Args:
            email: Recipient email address
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            if not all([settings.SMTP_HOST, settings.SMTP_USER, settings.SMTP_PASSWORD, settings.EMAIL_FROM]):
                logger.error("SMTP configuration is incomplete")
                return False
            
            message = MIMEText("This is a test email from Study.io. Your SMTP configuration is working correctly!")
            message["Subject"] = "Test Email - Study.io"
            message["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>"
            message["To"] = email
            
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(message)
            
            logger.info(f"Test email sent to {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send test email to {email}: {str(e)}")
            return False

email_service = EmailService()
