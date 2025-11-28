"""Core configuration settings"""
import os


def get_cors_config():
    """Get CORS configuration for FastAPI middleware"""
    vercel_prod_url = os.getenv("VERCEL_PROD_URL", "")
    allowed_origins = []

    # Add production URL if provided
    if vercel_prod_url:
        allowed_origins.extend([origin.strip() for origin in vercel_prod_url.split(",")])

    # Always allow localhost for development
    allowed_origins.append("http://localhost:3000")

    # Remove duplicates and empty strings
    allowed_origins = list(set([origin for origin in allowed_origins if origin]))

    # Use regex to allow all Vercel preview deployments (*.vercel.app)
    allow_origin_regex = r"https://.*\.vercel\.app"

    return {
        "allow_origins": allowed_origins,
        "allow_origin_regex": allow_origin_regex,
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    }

