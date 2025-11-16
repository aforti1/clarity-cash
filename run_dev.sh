#!/bin/bash

echo "Starting FastAPI backend..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000 > backend.log 2>&1 &

BACKEND_PID=$!
echo "Backend running on PID $BACKEND_PID"

echo "Starting React/Vite frontend..."
npm run dev --prefix ./frontend > frontend.log 2>&1 &

FRONTEND_PID=$!
echo "Frontend running on PID $FRONTEND_PID"

echo "Both servers launched successfully!"
echo "Use 'kill $BACKEND_PID' or 'kill $FRONTEND_PID' to stop them."
