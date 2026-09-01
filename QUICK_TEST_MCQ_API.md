# Quick MCQ API Test

## Option 1: Test in Incognito Window (FASTEST)

**This proves the fix works immediately without any cache clearing**:

1. Open **Incognito/Private** window:
   - Chrome/Edge: `Ctrl+Shift+N` (Windows) or `Cmd+Shift+N` (Mac)
   - Firefox: `Ctrl+Shift+P` (Windows) or `Cmd+Shift+P` (Mac)

2. Navigate to: `http://localhost:5173`

3. Login with your credentials

4. Click "MCQ Practice" or "Browse MCQs"

**Expected**: You should see MCQs immediately (1,613 total)

**If this works**: Your fix is successful, you just need to clear cache in your main browser

---

## Option 2: Check API Directly with curl

```bash
# Get a login token first (create new test user)
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"quicktest@test.com","password":"Test123!@#","full_name":"Quick Test"}'

# Login
TOKEN=$(curl -s -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"quicktest@test.com","password":"Test123!@#"}' \
  | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

echo "Token: $TOKEN"

# Verify user (check database)
export PGPASSWORD='3K4cnsyxYOOHGzCcxmOesU7PExXHCMaH'
psql -h localhost -p 5433 -U postgres -d irstudy_medical \
  -c "UPDATE users SET is_verified = true WHERE email = 'quicktest@test.com';"

# Now fetch MCQs
curl -s "http://localhost:8001/api/v1/mcqs/?skip=0&limit=5" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool | head -60
```

**Expected Output**:
```json
{
    "items": [
        {
            "id": 1401,
            "question_id": "MCQ-CARD-001",
            "question_text": "...",
            "options": {
                "A": "...",
                "B": "...",
                "C": "...",
                "D": "..."
            },
            "specialty": "cardiology",
            "difficulty": "medium",
            "tags": ["..."],
            "image_url": null,
            "image_caption": null,
            "times_attempted": 0,
            "success_rate": 0.0,
            "created_at": "2026-05-27T..."
        }
        ... (4 more MCQs)
    ],
    "total": 1613,
    "skip": 0,
    "limit": 5
}
```

**Key Check**: Does response have `"items"` and `"total"` properties? ✅

---

## Option 3: Clear Browser Cache

If incognito works, clear cache in main browser:

### Chrome/Edge:
1. F12 (DevTools)
2. Application tab
3. Storage section (left sidebar)
4. "Clear site data" button
5. Hard refresh: `Ctrl+Shift+R` (Win) or `Cmd+Shift+R` (Mac)

### Firefox:
1. F12 (DevTools)
2. Storage tab
3. Right-click each storage type → "Delete All"
4. Hard refresh: `Ctrl+F5` (Win) or `Cmd+Shift+R` (Mac)

---

## Troubleshooting

### "Email not verified" error
```bash
# Verify your user in database
export PGPASSWORD='3K4cnsyxYOOHGzCcxmOesU7PExXHCMaH'
psql -h localhost -p 5433 -U postgres -d irstudy_medical \
  -c "UPDATE users SET is_verified = true WHERE email = 'YOUR_EMAIL@example.com';"
```

### "Incorrect email or password" error
```bash
# Check if user exists
export PGPASSWORD='3K4cnsyxYOOHGzCcxmOesU7PExXHCMaH'
psql -h localhost -p 5433 -U postgres -d irstudy_medical \
  -c "SELECT email, is_verified, is_active FROM users WHERE email = 'YOUR_EMAIL@example.com';"
```

---

## Success Criteria

After testing, you should see:

✅ Response has `items` array (not flat array)
✅ Response has `total: 1613`
✅ Response has `skip` and `limit` properties
✅ Frontend MCQ Browser shows grid of cards
✅ Pagination shows "Page 1 of 81"
✅ Filters work (Cardiology, Respiratory, etc.)

---

**Next**: Once you confirm it works in incognito, clear cache in main browser.
