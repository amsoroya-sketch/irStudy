#!/bin/bash
# Start Complete Test Environment for Autonomous Playwright Testing

echo "🚀 Starting irStudy Test Environment..."
echo ""

# Check if backend is already running
if curl -s http://localhost:8001/docs > /dev/null 2>&1; then
    echo "✅ Backend already running on http://localhost:8001"
else
    echo "📦 Starting Backend..."
    cd /home/dev/Development/irStudy/backend

    # Start backend in background
    bash start-backend.sh > /tmp/irstudy-backend.log 2>&1 &
    BACKEND_PID=$!
    echo "   Backend PID: $BACKEND_PID"

    # Wait for backend to be ready
    echo "   Waiting for backend..."
    for i in {1..30}; do
        if curl -s http://localhost:8001/docs > /dev/null 2>&1; then
            echo "   ✅ Backend ready!"
            break
        fi
        sleep 1
    done
fi

echo ""

# Check if frontend is already running
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo "✅ Frontend already running on http://localhost:5173"
else
    echo "🎨 Starting Frontend..."
    cd /home/dev/Development/irStudy/frontend

    # Start frontend in background
    npm run dev > /tmp/irstudy-frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "   Frontend PID: $FRONTEND_PID"

    # Wait for frontend to be ready
    echo "   Waiting for frontend..."
    for i in {1..30}; do
        if curl -s http://localhost:5173 > /dev/null 2>&1; then
            echo "   ✅ Frontend ready!"
            break
        fi
        sleep 1
    done
fi

echo ""
echo "✨ Test Environment Ready!"
echo ""
echo "📍 URLs:"
echo "   Backend API: http://localhost:8001/docs"
echo "   Frontend:    http://localhost:5173"
echo ""
echo "📋 Logs:"
echo "   Backend:  tail -f /tmp/irstudy-backend.log"
echo "   Frontend: tail -f /tmp/irstudy-frontend.log"
echo ""
echo "🎭 Next Steps:"
echo "   1. Configure Claude Desktop MCP (see QUICKSTART_AUTONOMOUS_TESTING.md)"
echo "   2. Restart Claude Desktop"
echo "   3. In Claude Desktop, say:"
echo "      'Run OSCE video sample tests in headed mode and fix any bugs'"
echo ""
echo "🛑 To stop:"
echo "   pkill -f 'uvicorn src.main:app'"
echo "   pkill -f 'vite'"
echo ""
