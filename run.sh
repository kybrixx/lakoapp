#!/bin/bash

echo "🚀 Starting Lako Platform..."
echo ""

# Check if virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "📦 Creating virtual environment..."
    cd backend
    python3 -m venv venv
    cd ..
fi

# Start Backend
echo "🔧 Starting Backend on port 5000..."
cd backend
source venv/bin/activate
pip install -q -r requirements.txt
python run.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start Frontend
echo "🎨 Starting Frontend on port 3000..."
cd frontend
python3 -m http.server 3000 &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Lako is running!"
echo "   Backend:  http://localhost:5000"
echo "   Frontend: http://localhost:3000"
echo "   Admin: admin@lako.com / admin123"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait