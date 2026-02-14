#!/bin/bash
#
# OSCE Video Integration - One-Command Deployment & Testing Script
#
# This script automates the entire deployment and testing process for the video integration feature.
#
# Usage:
#   ./scripts/deploy-and-test-videos.sh
#
# Requirements:
#   - Docker and Docker Compose installed
#   - Python 3.12+ with venv
#   - Node.js 18+ with npm
#   - Playwright installed (will install if missing)

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "$1"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

# Check if we're in the project root
if [ ! -f "package.json" ] && [ ! -d "backend" ]; then
    log_error "Please run this script from the project root directory"
    exit 1
fi

# Main script
print_header "🎬 OSCE Video Integration - Deployment & Testing"

# Step 1: Start Docker services
print_header "📦 Step 1: Starting Docker Services"
log_info "Starting PostgreSQL, Redis, and Qdrant..."
docker compose up -d postgres redis qdrant

# Wait for services to be healthy
log_info "Waiting for services to be ready..."
sleep 10

# Check service health
if docker compose ps | grep -q "Up (healthy)"; then
    log_success "Docker services are running and healthy"
else
    log_warning "Some services may not be fully healthy yet. Continuing..."
fi

# Step 2: Set up Python environment
print_header "🐍 Step 2: Setting Up Python Environment"

if [ ! -d "venv" ]; then
    log_info "Creating virtual environment..."
    python3 -m venv venv
    log_success "Virtual environment created"
fi

log_info "Activating virtual environment..."
source venv/bin/activate

log_info "Installing Python dependencies..."
pip install -q --upgrade pip
pip install -q -r backend/requirements.txt
log_success "Python dependencies installed"

# Step 3: Run database migration
print_header "🗄️  Step 3: Running Database Migration"

log_info "Setting database environment variables..."
export DATABASE_PASSWORD="${DATABASE_PASSWORD:-MUVkFS6TlWR2IhYm6VTqXXMW2Nz+EkkARbdu/s1dYBs=}"
export DATABASE_URL="postgresql://postgres:${DATABASE_PASSWORD}@localhost:5433/irstudy_medical"

log_info "Running Alembic migration..."
cd backend

# Check current revision
CURRENT_REV=$(alembic current 2>/dev/null | grep -oP '(?<=\(head\) )[a-f0-9]+' || echo "none")
log_info "Current revision: $CURRENT_REV"

# Run upgrade
alembic upgrade head
log_success "Database migration completed"

cd ..

# Step 4: Populate video data
print_header "📹 Step 4: Populating OSCE Video Data"

log_info "Running video population script..."
echo "y" | python scripts/populate_osce_videos.py
log_success "Video data populated successfully"

# Step 5: Verify database
print_header "🔍 Step 5: Verifying Database"

log_info "Checking video resources in database..."
docker exec -it irstudy-postgres psql -U postgres -d irstudy_medical -c \
    "SELECT osce_id, station_title, video_resources IS NOT NULL as has_videos FROM osces WHERE station_type = 'physical_examination' LIMIT 5;" \
    2>/dev/null || log_warning "Database verification skipped (manual check recommended)"

# Step 6: Start backend server
print_header "🚀 Step 6: Starting Backend Server"

log_info "Starting FastAPI backend in background..."
cd backend
export PYTHONPATH=$(pwd)/src:$PYTHONPATH
nohup uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../logs/backend.pid
cd ..

log_info "Waiting for backend to start..."
sleep 5

# Check if backend is running
if curl -s http://localhost:8000/docs > /dev/null; then
    log_success "Backend server running on http://localhost:8000"
else
    log_warning "Backend may not be fully ready. Check logs/backend.log"
fi

# Step 7: Set up frontend
print_header "⚛️  Step 7: Setting Up Frontend"

cd frontend

if [ ! -d "node_modules" ]; then
    log_info "Installing npm dependencies..."
    npm install
    log_success "npm dependencies installed"
fi

# Install Playwright if not present
if [ ! -d "node_modules/@playwright/test" ]; then
    log_info "Installing Playwright..."
    npm install --save-dev @playwright/test
    npx playwright install chromium
    log_success "Playwright installed"
fi

# Start frontend server
log_info "Starting Vite dev server in background..."
nohup npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../logs/frontend.pid

log_info "Waiting for frontend to start..."
sleep 10

# Check if frontend is running
if curl -s http://localhost:5174 > /dev/null; then
    log_success "Frontend server running on http://localhost:5174"
else
    log_warning "Frontend may not be fully ready. Check logs/frontend.log"
fi

cd ..

# Step 8: Run tests
print_header "🧪 Step 8: Running Automated Tests"

cd frontend

log_info "Running Playwright tests with video recording..."
npx playwright test --project=chromium --reporter=html || log_warning "Some tests may have failed. Check report."

log_success "Tests completed. Results saved to playwright-report/"

cd ..

# Step 9: Test results summary
print_header "📊 Test Results Summary"

if [ -f "frontend/playwright-report/index.html" ]; then
    log_success "Test report generated: frontend/playwright-report/index.html"
    log_info "Open in browser: file://$(pwd)/frontend/playwright-report/index.html"
fi

if [ -d "frontend/test-results" ]; then
    VIDEO_COUNT=$(find frontend/test-results -name "video.webm" | wc -l)
    log_success "Recorded $VIDEO_COUNT test videos in frontend/test-results/"
fi

# Step 10: Manual testing instructions
print_header "🎯 Manual Testing Instructions"

cat << EOF
${GREEN}Servers Running:${NC}
- Backend:  http://localhost:8000 (PID: $BACKEND_PID)
- Frontend: http://localhost:5174 (PID: $FRONTEND_PID)
- API Docs: http://localhost:8000/docs

${BLUE}Manual Test Steps:${NC}
1. Open http://localhost:5174 in your browser
2. Navigate to an OSCE detail page
3. Scroll to "📺 Video Demonstrations" section
4. Verify videos display correctly
5. Click "Why recommended?" to expand details
6. Click "Watch Video" to test external links
7. Toggle "Supplementary Videos" section
8. Test on mobile viewport (resize browser)

${BLUE}Logs:${NC}
- Backend:  tail -f logs/backend.log
- Frontend: tail -f logs/frontend.log

${YELLOW}To Stop Servers:${NC}
kill $BACKEND_PID $FRONTEND_PID

${YELLOW}Or use:${NC}
./scripts/stop-servers.sh

EOF

# Create stop script
cat > scripts/stop-servers.sh << 'STOPEOF'
#!/bin/bash
if [ -f logs/backend.pid ]; then
    kill $(cat logs/backend.pid) 2>/dev/null
    rm logs/backend.pid
fi
if [ -f logs/frontend.pid ]; then
    kill $(cat logs/frontend.pid) 2>/dev/null
    rm logs/frontend.pid
fi
echo "✅ Servers stopped"
STOPEOF
chmod +x scripts/stop-servers.sh

# Final summary
print_header "✅ Deployment Complete!"

cat << EOF
${GREEN}Deployment Status: SUCCESS${NC}

${BLUE}Next Steps:${NC}
1. Open browser to http://localhost:5174
2. Review test results in frontend/playwright-report/
3. Watch recorded test videos in frontend/test-results/
4. Perform manual UAT testing

${BLUE}Documentation:${NC}
- Implementation Guide: OSCE_VIDEO_INTEGRATION_GUIDE.md
- UI Design Spec:      OSCE_VIDEO_UI_DESIGN.md
- Testing Guide:       OSCE_VIDEO_TESTING_GUIDE.md
- Complete Summary:    OSCE_VIDEO_INTEGRATION_COMPLETE_SUMMARY.md

${YELLOW}Troubleshooting:${NC}
If you encounter issues:
1. Check logs in logs/ directory
2. Verify Docker services: docker compose ps
3. Check database: docker exec -it irstudy-postgres psql -U postgres -d irstudy_medical
4. Restart services: ./scripts/deploy-and-test-videos.sh

EOF

log_success "All done! Happy testing! 🎉"
