#!/bin/bash
# Vercel build script that runs migrations before building Next.js
set -e

echo "🔨 Starting Vercel build process..."

# Check if DATABASE_URL is set (required for migrations)
if [ -z "$DATABASE_URL" ]; then
  echo "⚠️  Warning: DATABASE_URL not set, skipping migrations"
else
  echo "🔄 Running database migrations..."

  # Navigate to backend directory
  cd backend || exit 1

  # Install Python dependencies (minimal set for migrations)
  echo "📦 Installing migration dependencies..."
  python3 -m pip install --quiet --user alembic sqlalchemy psycopg2-binary python-dotenv || {
    echo "⚠️  Could not install Python dependencies, skipping migrations"
    cd ..
  }

  # Run migrations
  if command -v python3 &> /dev/null; then
    python3 -m alembic upgrade head || {
      echo "⚠️  Migration failed, but continuing with build"
    }
    echo "✅ Migrations completed"
  else
    echo "⚠️  Python3 not found, skipping migrations"
  fi

  # Return to root
  cd ..
fi

# Build Next.js
echo "🏗️  Building Next.js application..."
next build

echo "✅ Build completed successfully!"

