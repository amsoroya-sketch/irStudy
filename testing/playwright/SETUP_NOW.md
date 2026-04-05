# Start Autonomous Testing NOW - 3 Commands ⚡

**Time to autonomous testing**: 3 minutes

---

## Command 1: Start Test Environment (1 minute)

```bash
cd /home/dev/Development/irStudy/testing/playwright
./start-test-environment.sh
```

**What this does:**
- ✅ Starts PostgreSQL (if needed)
- ✅ Starts Backend on http://localhost:8001
- ✅ Starts Frontend on http://localhost:5173
- ✅ Waits for both to be ready

**Output you'll see:**
```
🚀 Starting irStudy Test Environment...
📦 Starting Backend...
   Backend PID: 12345
   Waiting for backend...
   ✅ Backend ready!
🎨 Starting Frontend...
   Frontend PID: 12346
   Waiting for frontend...
   ✅ Frontend ready!
✨ Test Environment Ready!
```

---

## Command 2: Configure Claude Desktop (2 minutes)

### Option A: Use my script (Fast)

```bash
mkdir -p ~/.config/claude
cat > ~/.config/claude/config.json << 'EOF'
{
  "mcpServers": {
    "playwright-testing": {
      "command": "node",
      "args": [
        "--loader",
        "ts-node/esm",
        "/home/dev/Development/irStudy/testing/playwright/mcp-server/playwright-mcp-server.ts"
      ],
      "env": {
        "NODE_ENV": "test"
      }
    }
  }
}
EOF

echo "✅ Claude Desktop config created!"
echo "🔄 Now restart Claude Desktop"
```

### Option B: Manual configuration

1. Open: `~/.config/claude/config.json`
2. Add this content:
```json
{
  "mcpServers": {
    "playwright-testing": {
      "command": "node",
      "args": [
        "--loader",
        "ts-node/esm",
        "/home/dev/Development/irStudy/testing/playwright/mcp-server/playwright-mcp-server.ts"
      ],
      "env": {
        "NODE_ENV": "test"
      }
    }
  }
}
```
3. Save and close

### Restart Claude Desktop

Close and reopen Claude Desktop application.

---

## Command 3: Run Autonomous Tests (30 seconds)

**In Claude Desktop (NEW session after restart), paste this:**

```
Run the OSCE video sample tests in headed mode.
Watch for failures and fix any bugs you find automatically.
Keep iterating until all tests pass.

Test file: tests/integration/osce/osce-video-sample.spec.ts

Use headed mode so I can watch the browser execute tests.
```

---

## What Happens Next (Autonomous)

Claude will:

1. **Call MCP tool: `run_tests`**
   - Opens Chromium browser (you see it)
   - Navigates to http://localhost:5173/osces/OSCE-MED-CARDIO-001
   - Executes 7 test cases
   - Reports results

2. **Analyze Failures** (if any)
   - Reviews error messages
   - Examines screenshots
   - Identifies root cause

3. **Fix Code Automatically**
   - Reads application files
   - Applies fixes
   - Saves changes

4. **Re-run Tests**
   - Only re-runs failed tests
   - Verifies fixes work
   - Repeats until all pass

5. **Report Success**
   - ✅ 7/7 tests passing
   - 🎉 All bugs fixed
   - 📊 Summary of changes made

---

## Expected Timeline

| Step | Time | Status |
|------|------|--------|
| Start environment | 1 min | You run script |
| Configure MCP | 2 min | You edit config |
| Run autonomous tests | 3-5 min | Claude does everything |
| **Total** | **6-8 minutes** | **Production-ready code** |

---

## Verify MCP Server Connected

After restarting Claude Desktop, in a new chat say:

```
What MCP tools do you have available?
```

You should see:
- ✅ `run_tests` - Run Playwright tests
- ✅ `get_test_results` - Get test results
- ✅ `get_failure_details` - Get failure details with screenshots
- ✅ `rerun_failed_tests` - Re-run only failed tests
- ✅ `stop_tests` - Stop running tests

If you don't see these, check:
1. Claude Desktop was restarted
2. Config file path is correct
3. MCP server file exists at the path specified

---

## Troubleshooting

### Backend won't start

**Error**: `ValueError: Database password not found`

**Fix**:
```bash
cd /home/dev/Development/irStudy/backend
export $(grep -v '^#' .env | xargs)
uvicorn src.main:app --reload --port 8001
```

### Frontend won't start

**Error**: Port 5173 already in use

**Fix**:
```bash
pkill -f vite
cd /home/dev/Development/irStudy/frontend
npm run dev
```

### MCP Server not connecting

**Error**: Claude says "No MCP tools available"

**Fix**:
1. Check config file exists: `cat ~/.config/claude/config.json`
2. Verify path: `/home/dev/Development/irStudy/testing/playwright/mcp-server/playwright-mcp-server.ts`
3. Restart Claude Desktop completely
4. Start new chat (old chats don't get new MCP servers)

### Tests fail with ECONNREFUSED

**Error**: Tests can't reach frontend/backend

**Fix**:
```bash
# Check both are running
curl http://localhost:8001/docs  # Should return HTML
curl http://localhost:5173        # Should return HTML

# If not, restart test environment
./start-test-environment.sh
```

---

## Stop Test Environment

When done testing:

```bash
# Stop backend
pkill -f 'uvicorn src.main:app'

# Stop frontend
pkill -f vite

# Or kill by PID (shown when you started)
kill <BACKEND_PID>
kill <FRONTEND_PID>
```

---

## Next Steps After First Test Pass

Once OSCE video tests pass:

### 1. Test MCQ Practice Flow
```
Create and run tests for MCQ practice flow.
Fix any bugs until all tests pass.
```

### 2. Test Authentication
```
Create and run tests for login, registration, and logout.
Fix any bugs until all tests pass.
```

### 3. Test Dashboard
```
Create and run tests for the student dashboard.
Fix any bugs until all tests pass.
```

### 4. Full Integration Suite
```
Run all integration tests and fix any failures.
Aim for 100% test pass rate.
```

---

## Summary

**3 Commands to Autonomous Testing:**

```bash
# 1. Start environment (1 min)
./start-test-environment.sh

# 2. Configure MCP (2 min)
# Edit ~/.config/claude/config.json
# Restart Claude Desktop

# 3. Run tests (in Claude Desktop)
# "Run OSCE video sample tests in headed mode and fix bugs"
```

**Result**: Claude autonomously tests and fixes your app in 3-5 minutes! 🤖✨

---

## Files Created

All setup files ready:
- ✅ `start-test-environment.sh` - One command to start everything
- ✅ `backend/start-backend.sh` - Backend with proper env vars
- ✅ `mcp-server/playwright-mcp-server.ts` - MCP server for Claude
- ✅ `tests/integration/osce/osce-video-sample.spec.ts` - Sample tests
- ✅ `QUICKSTART_AUTONOMOUS_TESTING.md` - Full documentation
- ✅ `autonomous-testing-agent.md` - Architecture details

---

**Ready? Run Command 1 now!** 🚀
