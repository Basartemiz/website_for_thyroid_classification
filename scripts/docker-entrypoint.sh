#!/bin/bash
set -e

# Function to wait for database
wait_for_db() {
    if [ -n "$DATABASE_URL" ]; then
        echo "Waiting for database..."

        # Extract host and port from DATABASE_URL
        # Format: postgres://user:pass@host:port/dbname
        DB_HOST=$(echo "$DATABASE_URL" | sed -E 's/.*@([^:]+):.*/\1/')
        DB_PORT=$(echo "$DATABASE_URL" | sed -E 's/.*:([0-9]+)\/.*/\1/')

        # Default port if not specified
        DB_PORT=${DB_PORT:-5432}

        # Wait for database to be ready
        max_attempts=30
        attempt=0
        while [ $attempt -lt $max_attempts ]; do
            if python -c "import socket; s = socket.socket(); s.settimeout(1); s.connect(('$DB_HOST', $DB_PORT)); s.close()" 2>/dev/null; then
                echo "Database is ready!"
                break
            fi
            attempt=$((attempt + 1))
            echo "Waiting for database... (attempt $attempt/$max_attempts)"
            sleep 2
        done

        if [ $attempt -eq $max_attempts ]; then
            echo "Error: Could not connect to database"
            exit 1
        fi
    fi
}

# Wait for database if DATABASE_URL is set
wait_for_db

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files (for WhiteNoise)
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Initialize vector store if requested
if [ "$INIT_VECTORSTORE" = "true" ]; then
    echo "Initializing vector store..."
    if [ -d "assets" ] && [ "$(ls -A assets/*.pdf 2>/dev/null)" ]; then
        python manage.py ingest_guides
        echo "Vector store initialized successfully!"
    else
        echo "Warning: No PDF files found in assets/ directory. Skipping vector store initialization."
    fi
fi

# Start the server
echo "Starting Gunicorn server..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers ${GUNICORN_WORKERS:-2} \
    --threads ${GUNICORN_THREADS:-4} \
    --timeout ${GUNICORN_TIMEOUT:-120} \
    --access-logfile - \
    --error-logfile - \
    --capture-output \
    --enable-stdio-inheritance
