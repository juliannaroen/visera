#!/bin/sh
# Run database migrations
echo "Running database migrations..."
pdm run alembic upgrade head
echo "Migrations complete!"

