# CORS Error Debugging Guide - `net::ERR_FAILED`

**Error**: `net::ERR_FAILED` when submitting MCQ attempt
**Date**: 2026-05-27
**Status**: Backend works with curl, browser request fails

---

## Verified Working Components ✅

1. **Backend is healthy**: Port 8001, uvicorn running
2. **CORS configured correctly**:
   ```
   access-control-allow-origin: http://localhost:5173
   access-control-allow-credentials: true
   access-control-allow-methods: GET, POST, PUT, DELETE, PATCH
   ```
3. **Endpoint exists**: `POST /api/v1/mcqs/{id}/attempt` returns 401 (auth required)
4. **MCQ data exists**: MCQ ID 899 confirmed in database
5. **Curl test passes**: Returns correct CORS headers

---

## The Problem: `net::ERR_FAILED`

This error means the browser is **blocking the request before it's sent**. Common causes:

### 1. Browser Extensions Blocking Requests
- Ad blockers (uBlock Origin, AdBlock Plus)
- Privacy extensions (Privacy Badger, Ghostery)
- CORS extensions (Allow CORS, CORS Unblock)
- Antivirus browser extensions

**Solution**: Test in Incognito/Private mode with all extensions disabled.

### 2. Browser Security Policy
- Content Security Policy (CSP) violations
- Mixed content (HTTPS → HTTP)
- Invalid request headers

**Solution**: Check browser console for CSP warnings.

### 3. Invalid Request Payload
- Malformed JSON
- Missing required headers
- Request size too large

**Solution**: Inspect the actual request in Network tab.

### 4. CORS Preflight Failing Silently
- OPTIONS request returns non-200 status
- OPTIONS request has incorrect headers
- OPTIONS request blocked by middleware

**Solution**: Check if OPTIONS request appears in Network tab.

---

## Diagnostic Steps (DO THESE IN ORDER)

### Step 1: Open Browser Developer Tools
```
Press F12 or Ctrl+Shift+I
Go to Network tab
Check "Preserve log"
```

### Step 2: Attempt MCQ Submission
1. Answer an MCQ question
2. Click Submit
3. Watch Network tab for requests

### Step 3: Find the Failed Request
Look for:
```
POST http://localhost:8001/api/v1/mcqs/899/attempt
Status: (failed) net::ERR_FAILED
```

### Step 4: Click on the Failed Request
Check these tabs:
- **Headers**:
  - Request URL (should be `http://localhost:8001/...`)
  - Request Method (should be `POST`)
  - Status Code (should show "failed")

- **Payload**:
  - Should show: `{"mcq_id": 899, "selected_answer": "A", "time_spent_seconds": ...}`

- **Preview/Response**:
  - Will be empty if request never sent

### Step 5: Check for OPTIONS Request
Look for request BEFORE the POST:
```
OPTIONS http://localhost:8001/api/v1/mcqs/899/attempt
Status: 200 OK (or failed)
```

**If OPTIONS is missing or failed**: CORS preflight is being blocked.

---

## Solutions to Try

### Solution 1: Clear Everything (MOST EFFECTIVE)
```javascript
// Open browser console (F12) and run:
localStorage.clear();
sessionStorage.clear();
location.reload(true);
```

Then:
1. Hard refresh (Ctrl+Shift+R)
2. Close all tabs for localhost:5173
3. Reopen in new tab

### Solution 2: Disable Browser Extensions
1. Open Incognito/Private window (Ctrl+Shift+N)
2. Navigate to `http://localhost:5173`
3. Try MCQ submission
4. If it works → One of your extensions is blocking it

### Solution 3: Check Browser Console for Errors
Look for:
- CSP violations: `Refused to connect to 'http://localhost:8001'`
- Mixed content: `Mixed Content: The page at 'https://...' was loaded over HTTPS`
- CORS errors: Different from the one you're seeing

### Solution 4: Test with Fetch API Directly
```javascript
// Open browser console and run:
fetch('http://localhost:8001/api/v1/mcqs/899/attempt', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Origin': 'http://localhost:5173'
  },
  credentials: 'include',
  body: JSON.stringify({
    mcq_id: 899,
    selected_answer: 'A',
    time_spent_seconds: 30
  })
})
.then(r => console.log('Response:', r.status, r.headers.get('access-control-allow-origin')))
.catch(e => console.error('Error:', e));
```

**Expected**: `Response: 401 http://localhost:5173` (auth error but CORS works)
**If you get**: `TypeError: Failed to fetch` → CORS is broken

### Solution 5: Restart Frontend Dev Server
```bash
# Terminal 1: Stop frontend
pkill -f vite

# Terminal 1: Restart frontend
cd /home/dev/Development/irStudy/frontend
npm run dev

# Wait for:
# ➜  Local:   http://localhost:5173/
```

### Solution 6: Check Vite Config for CORS Proxy
File: `frontend/vite.config.ts`

Should NOT have:
```typescript
server: {
  proxy: {
    '/api': 'http://localhost:8001'  // ← This can cause issues
  }
}
```

If it does, remove the proxy (we're using direct CORS).

---

## What I Need From You

Please run the diagnostic steps and tell me:

1. **Does an OPTIONS request appear?** (Yes/No)
   - If yes, what status code?

2. **What does the POST request show?**
   - Request URL: ?
   - Request Headers: ? (especially Authorization)
   - Request Payload: ?

3. **Any other errors in Console tab?**
   - CSP violations?
   - Other network errors?

4. **Does fetch API test work?** (from Solution 4)
   - What does it print?

5. **Are you using any browser extensions?**
   - Ad blocker?
   - CORS extension?
   - Antivirus?

6. **Does it work in Incognito mode?** (Yes/No)

---

## Temporary Workaround (If Nothing Works)

If all else fails, we can temporarily disable CORS in backend for testing:

```python
# backend/src/main.py - Line 127-134
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ← Temporarily allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # ← Allow all methods
    allow_headers=["*"],
    expose_headers=["*"],
)
```

**WARNING**: Only for local development debugging. Never use in production.

---

## Expected Working Flow

```
1. User clicks Submit MCQ
   ↓
2. Browser sends OPTIONS preflight
   ← Backend responds: 200 OK + CORS headers
   ↓
3. Browser sends POST with answer
   ← Backend responds: 401 Unauthorized + CORS headers
   ↓
4. Axios interceptor catches 401
   ↓
5. Axios tries token refresh
   ↓
6. If refresh fails → Redirect to login
```

Currently stuck at step 2 or 3 (request never reaches backend).

---

## Backend is Definitely Working

Confirmed with curl:
```bash
curl -X POST http://localhost:8001/api/v1/mcqs/899/attempt \
  -H "Content-Type: application/json" \
  -H "Origin: http://localhost:5173" \
  -d '{"mcq_id": 899, "selected_answer": "A", "time_spent_seconds": 30}'

# Returns: 401 Unauthorized
# Headers include: access-control-allow-origin: http://localhost:5173 ✅
```

So this is 100% a browser/frontend issue, not backend.

---

**Next Step**: Please follow "Diagnostic Steps" above and share your findings.
