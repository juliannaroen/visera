"""Email service for sending emails"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import os


def get_smtp_config():
    """
    Get SMTP configuration from environment variables.

    Supports various SMTP providers:
    - SendGrid: SMTP_HOST=smtp.sendgrid.net, SMTP_USER=apikey, SMTP_PASSWORD=your-api-key
    - Gmail: SMTP_HOST=smtp.gmail.com, SMTP_USER=your-email, SMTP_PASSWORD=app-password
    - Mailgun: SMTP_HOST=smtp.mailgun.org, SMTP_USER=your-username, SMTP_PASSWORD=your-password
    """
    return {
        "host": os.getenv("SMTP_HOST", "smtp.sendgrid.net"),  # Default to SendGrid
        "port": int(os.getenv("SMTP_PORT", "587")),
        "user": os.getenv("SMTP_USER"),
        "password": os.getenv("SMTP_PASSWORD"),
        "from_email": os.getenv("SMTP_FROM_EMAIL", os.getenv("SMTP_USER")),
    }


def get_verification_email_template(user_email: str, verification_link: str) -> str:
    """Generate email verification email template using f-strings"""
    return f"""
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
      </head>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(to right, #ec4899, #f97316); padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
          <h1 style="color: white; margin: 0;">Verify Your Email</h1>
        </div>
        <div style="background: #f9fafb; padding: 30px; border-radius: 0 0 8px 8px;">
          <p>Hi there,</p>
          <p>Thank you for signing up! Please verify your email address by clicking the button below:</p>
          <div style="text-align: center; margin: 30px 0;">
            <a href="{verification_link}"
               style="background: #ec4899; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold;">
              Verify Email Address
            </a>
          </div>
          <p style="font-size: 14px; color: #666;">Or copy and paste this link into your browser:</p>
          <p style="font-size: 12px; color: #999; word-break: break-all; background: #fff; padding: 10px; border-radius: 4px;">
            {verification_link}
          </p>
          <p style="font-size: 14px; color: #666; margin-top: 30px;">
            This link will expire in 24 hours. If you didn't create an account, you can safely ignore this email.
          </p>
        </div>
      </body>
    </html>
    """


def send_email(
    to_email: str,
    subject: str,
    html_body: str,
    smtp_config: Optional[dict] = None
) -> bool:
    """
    Send an email using SMTP

    Args:
        to_email: Recipient email address
        subject: Email subject
        html_body: HTML email body
        smtp_config: Optional SMTP configuration dict

    Returns:
        True if email sent successfully, False otherwise
    """
    if smtp_config is None:
        smtp_config = get_smtp_config()

    # Validate required configuration
    if not smtp_config.get("user") or not smtp_config.get("password"):
        raise ValueError("SMTP_USER and SMTP_PASSWORD must be set")

    try:
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = smtp_config["from_email"]
        msg["To"] = to_email

        # Add HTML body
        html_part = MIMEText(html_body, "html")
        msg.attach(html_part)

        # Send email
        with smtplib.SMTP(smtp_config["host"], smtp_config["port"]) as server:
            server.starttls()
            server.login(smtp_config["user"], smtp_config["password"])
            server.send_message(msg)

        return True
    except smtplib.SMTPAuthenticationError as e:
        # Authentication failed - check credentials
        print(f"SMTP authentication failed: {e}")
        print("Check that SMTP_USER and SMTP_PASSWORD are correct")
        return False
    except smtplib.SMTPException as e:
        # SMTP-specific errors
        print(f"SMTP error occurred: {e}")
        return False
    except Exception as e:
        # Other errors (connection, etc.)
        print(f"Failed to send email: {e}")
        return False


def send_verification_email(user_email: str, verification_token: str) -> bool:
    """
    Send email verification email

    Args:
        user_email: User's email address
        verification_token: JWT token for email verification

    Returns:
        True if email sent successfully, False otherwise
    """
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    verification_link = f"{frontend_url}/verify-email?token={verification_token}"

    html_body = get_verification_email_template(user_email, verification_link)
    subject = "Verify your email address"

    return send_email(user_email, subject, html_body)

