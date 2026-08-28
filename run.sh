#!/bin/bash
set -e

# Load environment variables from .env and .env.local if they exist
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi
if [ -f .env.local ]; then
    export $(cat .env.local | grep -v '^#' | xargs)
fi

# Run this script to start the server
source venv/bin/activate
alembic upgrade head
uvicorn app.main:app --reload --port ${APP_PORT:-5100}