#!/bin/bash
set -e

# Load environment variables from .env and .env.local if they exist
if [ -f .env ]; then
    export $(grep -v '^[[:space:]]*#' .env | sed 's/[[:space:]]*#.*//' | xargs)
fi
if [ -f .env.local ]; then
    export $(grep -v '^[[:space:]]*#' .env.local | sed 's/[[:space:]]*#.*//' | xargs)
fi

# Run this script to start the server
source venv/bin/activate
alembic upgrade head
uvicorn app.main:app --reload --port ${APP_PORT:-5100}