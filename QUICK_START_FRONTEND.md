# Quick Start - Frontend Testing

**Date**: 2026-02-07
**Status**: Ready for Manual Testing

---

## Prerequisites Check

Before starting, ensure these are running:

```bash
# Check Docker containers
docker ps

# You should see:
# - amc-postgres-dev (port 5433)
# - amc-redis-master-1 (port 7379)
# - amc-redis-master-2 (port 7380)
# - amc-redis-master-3 (port 7381)
# - amc-redis-replica-1 (port 7382)
# - amc-redis-replica-2 (port 7383)
# - amc-redis-replica-3 (port 7384)
# - amc-vault-dev (port 8200)
```

If not running:
```bash
docker-compose up -d
```

---

## Step 1: Start Backend Server

```bash
# Terminal 1: Backend
cd /home/dev/Development/irStudy/backend

# Activate virtual environment (if using venv)
source venv/bin/activate  # or: source ../venv/bin/activate

# Start FastAPI server
uvicorn src.main:app --reload --port 8001 --host 0.0.0.0

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8001
# INFO:     Application startup complete.
```

**Verify Backend**:
```bash
# In another terminal
curl http://localhost:8001/health
# Expected: {"status": "healthy"}

curl http://localhost:8001/api/v1/permissions/all
# Expected: {"detail":"Not authenticated"} (this is correct - needs auth)
```

---

## Step 2: Start Frontend Development Server

```bash
# Terminal 2: Frontend
cd /home/dev/Development/irStudy/frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev

# Expected output:
# VITE v5.x.x  ready in xxx ms
# ➜  Local:   http://localhost:5173/
# ➜  Network: use --host to expose
```

**Access Application**: Open browser to http://localhost:5173

---

## Step 3: Create Test Users

### Option A: Using Backend API Directly

```bash
# Create Student User
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@test.com",
    "password": "Student123!",
    "full_name": "Test Student",
    "role": "student"
  }'

# Create Educator User
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "educator@test.com",
    "password": "Educator123!",
    "full_name": "Test Educator",
    "role": "educator"
  }'

# Create Admin User
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@test.com",
    "password": "Admin123!",
    "full_name": "Test Admin",
    "role": "admin"
  }'
```

### Option B: Using Frontend UI

1. Go to http://localhost:5173/register
2. Fill in registration form:
   - Email: `student@test.com`
   - Password: `Student123!`
   - Full Name: `Test Student`
   - Role: Select "Student"
3. Click "Register"
4. Repeat for educator and admin accounts

---

## Step 4: Test Authentication Flow

### Login as Student

1. Go to http://localhost:5173/login
2. Email: `student@test.com`
3. Password: `Student123!`
4. Click "Login"

**Expected Result**: Redirected to `/dashboard`

**Dashboard Should Show**:
- Welcome message: "Role: STUDENT"
- 3 cards visible:
  - MCQ Practice
  - OSCE Scenarios
  - My Progress
- NO "Create Content" card
- NO "Admin Panel" card

### Test Student Permissions

1. Click "Browse MCQs" → Go to `/mcqs`
2. MCQ Browser should show:
   - Search and filter controls
   - Grid of MCQ cards
   - Each card has "Attempt" and "View" buttons
   - NO "Edit" button
   - NO "Create MCQ" button in header

3. Click "Attempt" on any MCQ → Go to `/mcqs/{id}/attempt`
4. MCQ Attempt page should show:
   - Question text
   - 5 radio button options (A-E)
   - "Submit Answer" button
5. Select an answer → Click "Submit Answer"
6. Should see:
   - Green alert (if correct) or Red alert (if incorrect)
   - Explanation text
   - Citation (if available)
   - "Try Again" and "Back to Browser" buttons

### Logout

1. Click logout button (if implemented) or clear localStorage:
```javascript
// In browser console
localStorage.clear()
window.location.reload()
```

---

## Step 5: Test Educator Permissions

### Login as Educator

1. Go to http://localhost:5173/login
2. Email: `educator@test.com`
3. Password: `Educator123!`

**Dashboard Should Show**:
- 6 cards (3 more than student):
  - MCQ Practice
  - OSCE Scenarios
  - My Progress
  - **Create Content** (new)
  - **Student Progress** (new)

### Test Educator-Specific Features

1. MCQ Browser (`/mcqs`):
   - Should see "Edit" button on MCQ cards
   - Should see "Create MCQ" button in header

2. Click "Edit" → Should navigate to `/mcqs/{id}/edit` (will show 404 until implemented)

3. Dashboard → "Create Content" card:
   - Should see "New MCQ" button
   - Should see "New OSCE" button

---

## Step 6: Test Admin Permissions

### Login as Admin

1. Email: `admin@test.com`
2. Password: `Admin123!`

**Dashboard Should Show**:
- All 7 cards:
  - MCQ Practice
  - OSCE Scenarios
  - My Progress
  - Create Content
  - **Admin Panel** (new, highlighted in red)
  - Student Progress

### Test Admin-Specific Features

1. Dashboard → "Admin Panel" card visible
2. MCQ Browser → Full access to all features
3. All CRUD operations available

---

## Troubleshooting

### Backend Not Starting

**Error**: `ModuleNotFoundError: No module named 'fastapi'`
**Fix**:
```bash
cd backend
pip install -r requirements.txt
```

**Error**: `Database password not found`
**Fix**:
```bash
# Set environment variable
export DATABASE_PASSWORD=your_password

# Or create .env file in backend/
echo "DATABASE_PASSWORD=your_password" > .env
```

### Frontend Not Starting

**Error**: `Cannot find module '@tanstack/react-query'`
**Fix**:
```bash
cd frontend
npm install
```

**Error**: Port 5173 already in use
**Fix**:
```bash
# Kill process on port 5173
lsof -ti:5173 | xargs kill -9

# Or use different port
npm run dev -- --port 5174
```

### API Connection Issues

**Error**: Network error / Cannot connect to server
**Check**:
1. Backend is running on port 8001:
   ```bash
   curl http://localhost:8001/health
   ```
2. Frontend VITE_API_BASE_URL is correct:
   ```bash
   # Check frontend/.env
   cat frontend/.env
   # Should have: VITE_API_BASE_URL=http://localhost:8001/api/v1
   ```

### Permission Errors

**Error**: "You do not have permission to access this feature"
**Check**:
1. User is logged in (check localStorage for `accessToken`)
2. JWT token is valid (not expired)
3. User has correct role
4. Backend permissions endpoint working:
   ```bash
   # Get token from localStorage
   TOKEN="your_access_token_here"

   curl http://localhost:8001/api/v1/permissions/me \
     -H "Authorization: Bearer $TOKEN"
   ```

### CORS Issues

**Error**: `CORS policy: No 'Access-Control-Allow-Origin' header`
**Fix**: Backend should already have CORS configured in `src/main.py`
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Testing Checklist

### Authentication
- [ ] Register new student user
- [ ] Login with student credentials
- [ ] Dashboard loads with correct role
- [ ] Logout (clear localStorage)
- [ ] Register educator user
- [ ] Login with educator credentials
- [ ] Dashboard shows educator-specific cards

### Student Journey
- [ ] Login as student
- [ ] Dashboard → Click "Browse MCQs"
- [ ] MCQ Browser loads with grid
- [ ] Filter by category (e.g., "Cardiology")
- [ ] Click "Attempt" on an MCQ
- [ ] MCQ Attempt page loads
- [ ] Select answer (A-E)
- [ ] Submit answer
- [ ] See correct/incorrect feedback
- [ ] See explanation and citation
- [ ] Click "Try Again" → form resets
- [ ] Click "Back to Browser" → return to list

### Educator Journey
- [ ] Login as educator
- [ ] Dashboard shows "Create Content" card
- [ ] MCQ Browser shows "Edit" button
- [ ] MCQ Browser shows "Create MCQ" in header
- [ ] Click "Create Content" → see "New MCQ" button

### Admin Journey
- [ ] Login as admin
- [ ] Dashboard shows "Admin Panel" card (red border)
- [ ] Full access to all features

### RBAC Testing
- [ ] Student CANNOT see "Create MCQ" button
- [ ] Student CANNOT see "Edit" button
- [ ] Educator CAN see "Create MCQ" button
- [ ] Educator CAN see "Edit" button
- [ ] Admin CAN see "Admin Panel" card
- [ ] Logout → Cannot access /dashboard (redirect to /login)

---

## Browser Console Checks

### Check Permissions Loaded

```javascript
// Open browser console (F12)
// After login, check React Query cache
window.__REACT_QUERY_DEVTOOLS_CACHE__

// Should see permissions data
```

### Check API Calls

```javascript
// Network tab → Filter by XHR
// Should see:
// - POST /auth/login (on login)
// - GET /permissions/me (on dashboard load)
// - GET /mcqs (on MCQ browser load)
// - POST /progress/mcq-attempts (on MCQ submit)
```

### Check localStorage

```javascript
// Console
localStorage.getItem('accessToken')
localStorage.getItem('refreshToken')
localStorage.getItem('user')

// All should return values after login
```

---

## Performance Checks

### Page Load Times

```javascript
// Open browser console
// Check Performance tab
// Metrics should be:
// - Dashboard load: <2s
// - MCQ list load: <500ms
// - MCQ attempt submit: <200ms
```

### Network Tab

- Initial page load: ~5-10 requests
- MCQ browser: 1-2 requests (cached after first load)
- MCQ attempt: 2 requests (fetch MCQ + submit attempt)

---

## Next Steps After Testing

### If Everything Works
1. ✅ Mark frontend as validated
2. 🎯 Proceed to OSCE interface (similar to MCQ)
3. 🎯 Implement MCQ creation form
4. 🎯 Build admin panel

### If Issues Found
1. 📝 Document issues
2. 🐛 Fix bugs
3. 🔄 Re-test
4. ✅ Validate fixes

---

## Quick Commands Reference

```bash
# Start everything
docker-compose up -d                                    # Infrastructure
cd backend && uvicorn src.main:app --reload --port 8001 # Backend
cd frontend && npm run dev                              # Frontend

# Stop everything
Ctrl+C in backend terminal
Ctrl+C in frontend terminal
docker-compose down

# Check status
docker ps                           # Infrastructure
curl http://localhost:8001/health   # Backend
curl http://localhost:5173          # Frontend

# Reset database (if needed)
cd backend
alembic downgrade base
alembic upgrade head

# Clear frontend cache
rm -rf frontend/node_modules/.vite
```

---

**Created**: 2026-02-07
**Status**: Ready for Testing
**Estimated Test Time**: 30-45 minutes for full checklist

🚀 **Ready to test - Start with Step 1!**
