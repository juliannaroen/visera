"""Unit tests for core config"""
import os
import pytest
from core.config import get_cors_config


class TestGetCorsConfig:
    """Test suite for get_cors_config function"""

    def test_get_cors_config_default(self):
        """Test CORS config with default values"""
        # Clear VERCEL_PROD_URL if set
        original_value = os.environ.pop("VERCEL_PROD_URL", None)
        try:
            config = get_cors_config()

            assert "allow_origins" in config
            assert "http://localhost:3000" in config["allow_origins"]
            assert config["allow_origin_regex"] == r"https://.*\.vercel\.app"
            assert config["allow_credentials"] is True
            assert "*" in config["allow_methods"]
            assert "*" in config["allow_headers"]
        finally:
            if original_value:
                os.environ["VERCEL_PROD_URL"] = original_value

    def test_get_cors_config_with_vercel_url(self):
        """Test CORS config with VERCEL_PROD_URL set"""
        original_value = os.environ.get("VERCEL_PROD_URL")
        try:
            os.environ["VERCEL_PROD_URL"] = "https://example.com,https://app.example.com"
            config = get_cors_config()

            assert "allow_origins" in config
            assert "https://example.com" in config["allow_origins"]
            assert "https://app.example.com" in config["allow_origins"]
            assert "http://localhost:3000" in config["allow_origins"]
        finally:
            if original_value:
                os.environ["VERCEL_PROD_URL"] = original_value
            else:
                os.environ.pop("VERCEL_PROD_URL", None)

    def test_get_cors_config_with_empty_vercel_url(self):
        """Test CORS config with empty VERCEL_PROD_URL"""
        original_value = os.environ.get("VERCEL_PROD_URL")
        try:
            os.environ["VERCEL_PROD_URL"] = ""
            config = get_cors_config()

            assert "allow_origins" in config
            assert "http://localhost:3000" in config["allow_origins"]
            # Empty strings should be filtered out
            assert "" not in config["allow_origins"]
        finally:
            if original_value:
                os.environ["VERCEL_PROD_URL"] = original_value
            else:
                os.environ.pop("VERCEL_PROD_URL", None)

