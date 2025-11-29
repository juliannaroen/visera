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


class TestGetSmtpConfig:
    """Test suite for get_smtp_config function"""

    def test_get_smtp_config_default(self):
        """Test SMTP config with default values"""
        original_values = {
            "SMTP_HOST": os.environ.get("SMTP_HOST"),
            "SMTP_PORT": os.environ.get("SMTP_PORT"),
            "SMTP_USER": os.environ.get("SMTP_USER"),
            "SMTP_PASSWORD": os.environ.get("SMTP_PASSWORD"),
            "SMTP_FROM_EMAIL": os.environ.get("SMTP_FROM_EMAIL"),
        }

        try:
            # Clear environment variables
            for key in original_values:
                os.environ.pop(key, None)

            config = get_smtp_config()

            assert config["host"] == "smtp.sendgrid.net"
            assert config["port"] == 587
        finally:
            # Restore original values
            for key, value in original_values.items():
                if value:
                    os.environ[key] = value
                else:
                    os.environ.pop(key, None)

    def test_get_smtp_config_custom(self):
        """Test SMTP config with custom values"""
        original_values = {
            "SMTP_HOST": os.environ.get("SMTP_HOST"),
            "SMTP_PORT": os.environ.get("SMTP_PORT"),
            "SMTP_USER": os.environ.get("SMTP_USER"),
            "SMTP_PASSWORD": os.environ.get("SMTP_PASSWORD"),
            "SMTP_FROM_EMAIL": os.environ.get("SMTP_FROM_EMAIL"),
        }

        try:
            os.environ["SMTP_HOST"] = "smtp.example.com"
            os.environ["SMTP_PORT"] = "465"
            os.environ["SMTP_USER"] = "testuser"
            os.environ["SMTP_PASSWORD"] = "testpass"
            os.environ["SMTP_FROM_EMAIL"] = "from@example.com"

            config = get_smtp_config()

            assert config["host"] == "smtp.example.com"
            assert config["port"] == 465
            assert config["user"] == "testuser"
            assert config["password"] == "testpass"
            assert config["from_email"] == "from@example.com"
        finally:
            # Restore original values
            for key, value in original_values.items():
                if value:
                    os.environ[key] = value
                else:
                    os.environ.pop(key, None)

    def test_get_smtp_config_from_email_fallback(self):
        """Test SMTP config where from_email falls back to SMTP_USER"""
        original_values = {
            "SMTP_USER": os.environ.get("SMTP_USER"),
            "SMTP_FROM_EMAIL": os.environ.get("SMTP_FROM_EMAIL"),
        }

        try:
            os.environ["SMTP_USER"] = "testuser@example.com"
            os.environ.pop("SMTP_FROM_EMAIL", None)

            config = get_smtp_config()

            assert config["from_email"] == "testuser@example.com"
        finally:
            # Restore original values
            for key, value in original_values.items():
                if value:
                    os.environ[key] = value
                else:
                    os.environ.pop(key, None)


class TestGetVerificationEmailTemplate:
    """Test suite for get_verification_email_template function"""

    def test_get_verification_email_template(self):
        """Test email template generation"""
        user_email = "test@example.com"
        verification_link = "https://example.com/verify?token=abc123"

        template = get_verification_email_template(user_email, verification_link)

        # Note: user_email is not directly in the template, but verification_link is
        assert verification_link in template
        assert "Verify Your Email" in template
        assert "Verify Email Address" in template
        assert "24 hours" in template


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
        """Test successfully sending verification email"""
        original_values = {
            "FRONTEND_URL": os.environ.get("FRONTEND_URL"),
        }

        try:
            os.environ["FRONTEND_URL"] = "https://example.com"

            with patch('core.email.send_email', return_value=True):
                result = send_verification_email("test@example.com", "token123")

                assert result is True
        finally:
            if original_values["FRONTEND_URL"]:
                os.environ["FRONTEND_URL"] = original_values["FRONTEND_URL"]
            else:
                os.environ.pop("FRONTEND_URL", None)

    def test_send_verification_email_default_frontend_url(self):
        """Test sending verification email with default FRONTEND_URL"""
        original_value = os.environ.get("FRONTEND_URL")
        try:
            os.environ.pop("FRONTEND_URL", None)

            with patch('core.email.send_email', return_value=True):
                result = send_verification_email("test@example.com", "token123")

                assert result is True
        finally:
            if original_value:
                os.environ["FRONTEND_URL"] = original_value

