"""Email service module for the Foodshare backend.

This module provides asynchronous email sending capabilities using various providers
(Gmail, Console, and Mock) to support production, development, and testing environments.
"""

import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Protocol

import aiosmtplib

logger = logging.getLogger(__name__)


class EmailServiceProvider(Protocol):
    """Protocol defining the interface for email service providers."""

    async def send_otp(self, email: str, otp: str) -> bool:
        """Send a one-time password to the specified email address.

        Args:
            email (str): The recipient's email address.
            otp (str): The one-time password to send.

        Returns:
            bool: True if the email was sent successfully, False otherwise.
        """
        ...


class GmailService:
    """Gmail implementation of the EmailServiceProvider using aiosmtplib."""

    def __init__(self, user: str, password: str, logo_url: str | None = None):
        """Initialize the Gmail service with credentials.

        Args:
            user (str): Gmail username/email.
            password (str): Gmail app password.
            logo_url (str | None): Optional URL for the app logo in the email.
        """
        self.user = user
        self.password = password
        self.logo_url = logo_url or "https://via.placeholder.com/150x50?text=Black+Bear+Foodshare"

    async def send_otp(self, email: str, otp: str) -> bool:
        """Send an HTML-formatted OTP email via Gmail SMTP."""
        message = MIMEMultipart("alternative")
        message["From"] = self.user
        message["To"] = email
        message["Subject"] = f"{otp} is your Black Bear Foodshare code"

        div_style = "max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;"
        code_style = (
            "background-color: #f8f9fa; padding: 20px; text-align: center; "
            "font-size: 32px; font-weight: bold; letter-spacing: 5px; "
            "color: #000; border-radius: 5px; margin: 20px 0;"
        )

        html_content = f"""
        <html>
            <body style="font-family: sans-serif; color: #333;">
                <div style="{div_style}">
                    <div style="text-align: center; margin-bottom: 20px;">
                        <img src="{self.logo_url}" alt="Black Bear Foodshare Logo" style="max-width: 200px;">
                    </div>
                    <h2 style="color: #007bff; text-align: center;">Verification Code</h2>
                    <p>Hello,</p>
                    <p>Your one-time password for Black Bear Foodshare is:</p>
                    <div style="{code_style}">
                        {otp}
                    </div>
                    <p>This code will expire in 10 minutes. If you did not request this code,
                       please ignore this email.</p>
                    <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
                    <p style="font-size: 12px; color: #777; text-align: center;">
                        &copy; 2026 Black Bear Foodshare. All rights reserved.
                    </p>
                </div>
            </body>
        </html>
        """
        message.attach(MIMEText(f"Your Black Bear Foodshare verification code is: {otp}", "plain"))
        message.attach(MIMEText(html_content, "html"))

        try:
            await aiosmtplib.send(
                message,
                hostname="smtp.gmail.com",
                port=587,
                username=self.user,
                password=self.password,
                start_tls=True,
            )
            logger.info(f"OTP email sent successfully to {email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send OTP email to {email}: {e}", exc_info=True)
            return False


class ConsoleService:
    """Development implementation that logs the OTP to the console."""

    async def send_otp(self, email: str, otp: str) -> bool:
        """Log the OTP to the console for easy development."""
        print("\n" + "=" * 40)
        print("EMAIL BYPASS (ConsoleService)")
        print(f"To:      {email}")
        print(f"Subject: {otp} is your code")
        print(f"Code:    {otp}")
        print("=" * 40 + "\n")
        logger.info(f"OTP {otp} logged to console for {email}")
        return True


class MockService:
    """Testing implementation that stores sent messages in memory."""

    def __init__(self):
        """Initialize the Mock Service."""
        self.sent_messages = []

    async def send_otp(self, email: str, otp: str) -> bool:
        """Store the OTP message in an internal list for test verification."""
        self.sent_messages.append({"email": email, "otp": otp})
        logger.info(f"Mock OTP {otp} stored for {email}")
        return True
