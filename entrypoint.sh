#!/bin/sh

# Wait for the database to be ready
echo "Waiting for database..."
python src/wait_for_db.py

# Apply database migrations
echo "Apply database migrations"
python src/manage.py migrate

# Seed the database
echo "Seeding database..."
python src/manage.py seed_db

# Start server
echo "Starting server"
python src/manage.py runserver 0.0.0.0:8000
