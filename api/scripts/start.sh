#!/bin/sh

echo "Running Migrations"
alembic upgrade head

SEEDS_PATH="/app/scripts/seeds"
PYTHON_FILES=$(ls $SEEDS_PATH/*.py 2>/dev/null)
if [ -z "$PYTHON_FILES" ]; then
    echo "No Python files found in $SEEDS_PATH"
    exit 1
fi
for seed in $PYTHON_FILES; do
    echo "Running $seed..."
    python "$seed"
    echo ''
done

APP_MODULE="app.main:app"
APP_PORT="8000"
UVICORN_COMMAND="uvicorn $APP_MODULE --host 0.0.0.0 --port $APP_PORT --env-file .env"

echo "Starting application"
exec $UVICORN_COMMAND