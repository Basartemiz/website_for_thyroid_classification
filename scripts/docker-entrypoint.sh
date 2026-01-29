#!/bin/bash
set -e

# Function to wait for database
wait_for_db() {
    if [ -n "$DATABASE_URL" ]; then
        echo "Waiting for database..."

        DB_HOST=$(echo "$DATABASE_URL" | sed -E 's|.*@([^/:]+).*|\1|')
        DB_PORT=$(echo "$DATABASE_URL" | sed -E 's|.*:([0-9]+)/.*|\1|')
        DB_PORT=${DB_PORT:-5432}

        echo "Connecting to database at $DB_HOST:$DB_PORT"

        max_attempts=30
        attempt=0
        while [ $attempt -lt $max_attempts ]; do
            if python -c "import socket; s = socket.socket(); s.settimeout(3); s.connect(('$DB_HOST', $DB_PORT)); s.close()" 2>/dev/null; then
                echo "Database is ready!"
                break
            fi
            attempt=$((attempt + 1))
            echo "Waiting for database... (attempt $attempt/$max_attempts)"
            sleep 2
        done

        if [ $attempt -eq $max_attempts ]; then
            echo "Warning: Could not verify database connection, proceeding anyway..."
        fi
    fi
}

wait_for_db

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Creating cache table..."
python manage.py createcachetable 2>/dev/null || true

echo "Collecting static files..."
python manage.py collectstatic --noinput

# Only initialize vector store when EXPLICITLY requested
if [ "$INIT_VECTORSTORE" = "true" ]; then
    echo "Initializing vector store..."
    if [ -d "assets" ] && [ "$(ls -A assets/*.pdf 2>/dev/null)" ]; then
        python manage.py ingest_guides
        echo "Vector store initialized successfully!"
    else
        echo "Warning: No PDF files found in assets/ directory."
    fi
else
    echo "Skipping vector store initialization (INIT_VECTORSTORE != true)"
fi

echo "Starting Gunicorn server..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers ${GUNICORN_WORKERS:-1} \
    --threads ${GUNICORN_THREADS:-2} \
    --timeout ${GUNICORN_TIMEOUT:-120} \
    --access-logfile - \
    --error-logfile - \
    --capture-output \
    --enable-stdio-inheritance
