#!/bin/bash

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Seed the database with test users
python -c "
import asyncio
from seed_test_users import seed_users
asyncio.run(seed_users())
"

# Start the backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Serve frontend
cd ..
python -m http.server 3000 &
FRONTEND_PID=$!

echo "✅ Setup complete!"
echo "📍 Backend running at: http://localhost:8000"
echo "📍 Frontend running at: http://localhost:3000"
echo "📧 Login with: user0@example.com"
echo "🔑 Password: password123"

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
