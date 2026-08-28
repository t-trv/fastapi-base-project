# Run this script to start the server
# Make sure you have activated your virtual environment
# .venv\Scripts\Activate
alembic upgrade head
uvicorn app.main:app --reload --port 5100