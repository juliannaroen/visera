"""Email service for sending emails"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from core.config import settings


def get_smtp_config():
    """
    Get SMTP configuration.

    Supports various SMTP providers:
    - SendGrid: SMTP_HOST=smtp.sendgrid.net, SMTP_USER=apikey, SMTP_PASSWORD=your-api-key
    - Gmail: SMTP_HOST=smtp.gmail.com, SMTP_USER=your-email, SMTP_PASSWORD=app-password
    - Mailgun: SMTP_HOST=smtp.mailgun.org, SMTP_USER=your-username, SMTP_PASSWORD=your-password
    """
    return settings.get_smtp_config()


def get_verification_email_template(user_email: str, otp_code: str) -> str:
    """Generate email verification email template with OTP code"""
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
          <p>Thank you for signing up! Please verify your email address using the code below:</p>
          <div style="text-align: center; margin: 30px 0;">
            <div style="background: #fff; border: 2px solid #ec4899; border-radius: 8px; padding: 20px; display: inline-block;">
              <p style="font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #ec4899; margin: 0; font-family: 'Courier New', monospace;">
                {otp_code}
              </p>
            </div>
          </div>
          <p style="font-size: 14px; color: #666; margin-top: 30px;">
            Enter this code on the verification page to complete your email verification.
          </p>
          <p style="font-size: 14px; color: #666;">
            This code will expire in 15 minutes. If you didn't create an account, you can safely ignore this email.
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

    # Validate required configuration (safety check - config should ensure these are set)
    if not smtp_config.get("user") or not smtp_config.get("password") or not smtp_config.get("from_email"):
        raise ValueError("SMTP_USER, SMTP_PASSWORD, and SMTP_FROM_EMAIL must be set")

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


def send_verification_email(user_email: str, otp_code: str) -> bool:
    """
    Send email verification email with OTP code

    Args:
        user_email: User's email address
        otp_code: 6-character OTP code for email verification

    Returns:
        True if email sent successfully, False otherwise
    """
    html_body = get_verification_email_template(user_email, otp_code)
    subject = "Verify your email address"

    return send_email(user_email, subject, html_body)

