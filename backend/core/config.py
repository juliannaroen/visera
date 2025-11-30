"""Centralized configuration management"""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


def _get_required_env(key: str) -> str:
    """Get required environment variable, raise error if not set"""
    value = os.getenv(key)
    if value is None:
        raise ValueError(f"Required environment variable {key} is not set")
    return value


def _get_optional_env(key: str) -> Optional[str]:
    """Get optional environment variable"""
    return os.getenv(key)


def _get_required_int_env(key: str) -> int:
    """Get required integer environment variable, raise error if not set or invalid"""
    value = os.getenv(key)
    if value is None:
        raise ValueError(f"Required environment variable {key} is not set")
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"Environment variable {key} must be a valid integer, got: {value}")


class Settings:
    """Application settings loaded from environment variables"""

    # Auth Configuration
    auth_cookie_name: str = _get_required_env("AUTH_COOKIE_NAME")
    auth_cookie_max_age: int = _get_required_int_env("AUTH_COOKIE_MAX_AGE")
    jwt_secret_key: str = _get_required_env("JWT_SECRET_KEY")
    jwt_algorithm: str = "HS256"  # Not configurable, always HS256
    jwt_expire_minutes: int = _get_required_int_env("JWT_EXPIRE_MINUTES")

    # Database Configuration
    database_url: str = _get_required_env("DATABASE_URL")

    # Email Configuration
    smtp_host: str = _get_required_env("SMTP_HOST")
    smtp_port: int = _get_required_int_env("SMTP_PORT")
    smtp_user: str = _get_required_env("SMTP_USER")
    smtp_password: str = _get_required_env("SMTP_PASSWORD")
    smtp_from_email: str = _get_required_env("SMTP_FROM_EMAIL")
    frontend_url: str = _get_required_env("FRONTEND_URL")

    # CORS Configuration
    allowed_origins: str = _get_required_env("ALLOWED_ORIGINS")

    # App Configuration
    environment: str = _get_required_env("ENVIRONMENT")
    port: int = _get_required_int_env("PORT")

    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment == "production"

    def get_cors_config(self) -> dict:
        """Get CORS configuration for FastAPI middleware"""
        # Parse comma-separated origins from environment variable
        origins = [origin.strip() for origin in self.allowed_origins.split(",")]

        # Remove empty strings and duplicates
        origins = list(set([origin for origin in origins if origin]))

        # Use regex to allow all Vercel preview deployments (*.vercel.app)
        allow_origin_regex = r"https://.*\.vercel\.app"

        return {
            "allow_origins": origins,
            "allow_origin_regex": allow_origin_regex,
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
        }

    def get_smtp_config(self) -> dict:
        """
        Get SMTP configuration.

        Supports various SMTP providers:
        - SendGrid: SMTP_HOST=smtp.sendgrid.net, SMTP_USER=apikey, SMTP_PASSWORD=your-api-key
        - Gmail: SMTP_HOST=smtp.gmail.com, SMTP_USER=your-email, SMTP_PASSWORD=app-password
        - Mailgun: SMTP_HOST=smtp.mailgun.org, SMTP_USER=your-username, SMTP_PASSWORD=your-password
        """
        return {
            "host": self.smtp_host,
            "port": self.smtp_port,
            "user": self.smtp_user,
            "password": self.smtp_password,
            "from_email": self.smtp_from_email,
        }


# Global settings instance
settings = Settings()


# Backwards compatibility function (can be removed if not needed)
def get_cors_config() -> dict:
    """Get CORS configuration (backwards compatibility)"""
    return settings.get_cors_config()
