#!/bin/sh
# Run database migrations
echo "Running database migrations..."
python -m alembic upgrade head
echo "Migrations complete!"

