"""Unit tests for core config"""
import os
import pytest
from unittest.mock import patch
from core.config import get_cors_config, settings


class TestGetCorsConfig:
    """Test suite for get_cors_config function"""

    def test_get_cors_config_single_origin(self):
        """Test CORS config with single origin"""
        original_value = settings.allowed_origins
        try:
            settings.allowed_origins = "https://example.com"
            config = get_cors_config()

            assert "allow_origins" in config
            assert "https://example.com" in config["allow_origins"]
            assert len(config["allow_origins"]) == 1
            assert config["allow_origin_regex"] == r"https://.*\.vercel\.app"
            assert config["allow_credentials"] is True
            assert "*" in config["allow_methods"]
            assert "*" in config["allow_headers"]
        finally:
            settings.allowed_origins = original_value

    def test_get_cors_config_multiple_origins(self):
        """Test CORS config with multiple comma-separated origins"""
        original_value = settings.allowed_origins
        try:
            settings.allowed_origins = "https://example.com,https://app.example.com,http://localhost:3000"
            config = get_cors_config()

            assert "allow_origins" in config
            assert "https://example.com" in config["allow_origins"]
            assert "https://app.example.com" in config["allow_origins"]
            assert "http://localhost:3000" in config["allow_origins"]
            assert len(config["allow_origins"]) == 3
        finally:
            settings.allowed_origins = original_value

    def test_get_cors_config_with_whitespace(self):
        """Test CORS config handles whitespace in comma-separated values"""
        original_value = settings.allowed_origins
        try:
            settings.allowed_origins = "https://example.com, https://app.example.com , http://localhost:3000"
            config = get_cors_config()

            assert "allow_origins" in config
            assert "https://example.com" in config["allow_origins"]
            assert "https://app.example.com" in config["allow_origins"]
            assert "http://localhost:3000" in config["allow_origins"]
            # Whitespace should be stripped
            assert " https://app.example.com " not in config["allow_origins"]
        finally:
            settings.allowed_origins = original_value

    def test_get_cors_config_removes_duplicates(self):
        """Test CORS config removes duplicate origins"""
        original_value = settings.allowed_origins
        try:
            settings.allowed_origins = "https://example.com,https://example.com,https://app.example.com"
            config = get_cors_config()

            assert "allow_origins" in config
            assert config["allow_origins"].count("https://example.com") == 1
            assert len(config["allow_origins"]) == 2
        finally:
            settings.allowed_origins = original_value

