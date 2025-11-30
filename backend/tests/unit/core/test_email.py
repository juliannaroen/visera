"""Unit tests for core email"""
import pytest
import os
from unittest.mock import patch, MagicMock
from core.email import (
    get_smtp_config,
    get_verification_email_template,
    send_email,
    send_verification_email
)
from core.config import settings


class TestGetSmtpConfig:
    """Test suite for get_smtp_config function"""

    def test_get_smtp_config_custom(self):
        """Test SMTP config with custom values"""
        original_values = {
            "smtp_host": settings.smtp_host,
            "smtp_port": settings.smtp_port,
            "smtp_user": settings.smtp_user,
            "smtp_password": settings.smtp_password,
            "smtp_from_email": settings.smtp_from_email,
        }

        try:
            settings.smtp_host = "smtp.example.com"
            settings.smtp_port = 465
            settings.smtp_user = "testuser"
            settings.smtp_password = "testpass"
            settings.smtp_from_email = "from@example.com"

            config = get_smtp_config()

            assert config["host"] == "smtp.example.com"
            assert config["port"] == 465
            assert config["user"] == "testuser"
            assert config["password"] == "testpass"
            assert config["from_email"] == "from@example.com"
        finally:
            # Restore original values
            settings.smtp_host = original_values["smtp_host"]
            settings.smtp_port = original_values["smtp_port"]
            settings.smtp_user = original_values["smtp_user"]
            settings.smtp_password = original_values["smtp_password"]
            settings.smtp_from_email = original_values["smtp_from_email"]


class TestGetVerificationEmailTemplate:
    """Test suite for get_verification_email_template function"""

    def test_get_verification_email_template(self):
        """Test email template generation with OTP code"""
        user_email = "test@example.com"
        otp_code = "ABC123"

        template = get_verification_email_template(user_email, otp_code)

        # Check that OTP code is in the template
        assert otp_code in template
        assert "Verify Your Email" in template
        assert "15 minutes" in template
        assert "Enter this code" in template


class TestSendEmail:
    """Test suite for send_email function"""

    def test_send_email_success(self):
        """Test successfully sending email"""
        smtp_config = {
            "host": "smtp.example.com",
            "port": 587,
            "user": "testuser",
            "password": "testpass",
            "from_email": "from@example.com"
        }

        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server

            result = send_email(
                "to@example.com",
                "Test Subject",
                "<html>Test Body</html>",
                smtp_config
            )

            assert result is True
            mock_server.starttls.assert_called_once()
            mock_server.login.assert_called_once_with("testuser", "testpass")
            mock_server.send_message.assert_called_once()

    def test_send_email_missing_config(self):
        """Test sending email with missing SMTP config"""
        smtp_config = {
            "host": "smtp.example.com",
            "port": 587,
            "user": None,
            "password": "testpass",
            "from_email": "from@example.com"
        }

        with pytest.raises(ValueError) as exc_info:
            send_email("to@example.com", "Test Subject", "<html>Test Body</html>", smtp_config)

        assert "SMTP_USER" in str(exc_info.value) or "password" in str(exc_info.value).lower()

    def test_send_email_authentication_error(self):
        """Test sending email with authentication error"""
        smtp_config = {
            "host": "smtp.example.com",
            "port": 587,
            "user": "testuser",
            "password": "wrongpass",
            "from_email": "from@example.com"
        }

        import smtplib

        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, "Authentication failed")

            result = send_email(
                "to@example.com",
                "Test Subject",
                "<html>Test Body</html>",
                smtp_config
            )

            assert result is False

    def test_send_email_smtp_error(self):
        """Test sending email with SMTP error"""
        smtp_config = {
            "host": "smtp.example.com",
            "port": 587,
            "user": "testuser",
            "password": "testpass",
            "from_email": "from@example.com"
        }

        import smtplib

        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            mock_server.send_message.side_effect = smtplib.SMTPException("SMTP error")

            result = send_email(
                "to@example.com",
                "Test Subject",
                "<html>Test Body</html>",
                smtp_config
            )

            assert result is False

    def test_send_email_general_exception(self):
        """Test sending email with general exception"""
        smtp_config = {
            "host": "smtp.example.com",
            "port": 587,
            "user": "testuser",
            "password": "testpass",
            "from_email": "from@example.com"
        }

        with patch('smtplib.SMTP') as mock_smtp:
            mock_smtp.side_effect = Exception("Connection error")

            result = send_email(
                "to@example.com",
                "Test Subject",
                "<html>Test Body</html>",
                smtp_config
            )

            assert result is False

    def test_send_email_uses_default_config(self):
        """Test sending email uses default SMTP config when not provided"""
        original_values = {
            "SMTP_HOST": os.environ.get("SMTP_HOST"),
            "SMTP_PORT": os.environ.get("SMTP_PORT"),
            "SMTP_USER": os.environ.get("SMTP_USER"),
            "SMTP_PASSWORD": os.environ.get("SMTP_PASSWORD"),
        }

        try:
            os.environ["SMTP_USER"] = "testuser"
            os.environ["SMTP_PASSWORD"] = "testpass"

            with patch('core.email.get_smtp_config') as mock_get_config:
                mock_config = {
                    "host": "smtp.example.com",
                    "port": 587,
                    "user": "testuser",
                    "password": "testpass",
                    "from_email": "from@example.com"
                }
                mock_get_config.return_value = mock_config

                with patch('smtplib.SMTP') as mock_smtp:
                    mock_server = MagicMock()
                    mock_smtp.return_value.__enter__.return_value = mock_server

                    result = send_email("to@example.com", "Test Subject", "<html>Test Body</html>")

                    assert result is True
                    mock_get_config.assert_called_once()
        finally:
            # Restore original values
            for key, value in original_values.items():
                if value:
                    os.environ[key] = value
                else:
                    os.environ.pop(key, None)


class TestSendVerificationEmail:
    """Test suite for send_verification_email function"""

    def test_send_verification_email_success(self):
        """Test successfully sending verification email with OTP code"""
        with patch('core.email.send_email', return_value=True):
            result = send_verification_email("test@example.com", "ABC123")

            assert result is True

    def test_send_verification_email_failure(self):
        """Test sending verification email when email sending fails"""
        with patch('core.email.send_email', return_value=False):
            result = send_verification_email("test@example.com", "ABC123")

            assert result is False

