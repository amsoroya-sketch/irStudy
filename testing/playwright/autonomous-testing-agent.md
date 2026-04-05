# Autonomous Testing Agent with Playwright MCP Server

**Purpose**: Claude monitors Playwright tests, identifies failures, and automatically fixes application code until all tests pass.

---

## Architecture

```
┌─────────────────────────────────────────────┐
│  1. Playwright MCP Server (Port 5010)       │
│     - Runs tests in headed mode             │
│     - Streams results to Claude             │
│     - Reports failures with screenshots     │
└─────────────────┬───────────────────────────┘
                  │ MCP Protocol
┌─────────────────▼───────────────────────────┐
│  2. Claude Autonomous Testing Agent         │
│     - Monitors test execution               │
│     - Detects failures                      │
│     - Analyzes error messages               │
│     - Reads application code                │
│     - Fixes bugs automatically              │
│     - Re-runs tests                         │
└─────────────────┬───────────────────────────┘
                  │ Code Fixes
┌─────────────────▼───────────────────────────┐
│  3. Application Code                        │
│     - Frontend (React/TypeScript)           │
│     - Backend (FastAPI/Python)              │
│     - Tests pass → Deployment ready         │
└─────────────────────────────────────────────┘
```

---

## Setup Instructions

### 1. Install MCP SDK

```bash
cd /home/dev/Development/irStudy/testing/playwright
npm install @modelcontextprotocol/sdk
```

### 2. Configure MCP Server in Claude Desktop

Add to `~/.config/claude/config.json`:

```json
{
  "mcpServers": {
    "playwright-testing": {
      "command": "node",
      "args": [
        "/home/dev/Development/irStudy/testing/playwright/mcp-server/playwright-mcp-server.ts"
      ],
      "env": {
        "NODE_ENV": "test"
      }
    }
  }
}
```

### 3. Restart Claude Desktop

Restart Claude Desktop to load the MCP server.

---

## Usage: Autonomous Testing Session

### Start Autonomous Testing

In Claude, use the Playwright MCP tools:

**1. Run Tests (Headed Mode)**
```
Run Playwright tests in headed mode for OSCE video resources
```

Claude will call:
```typescript
mcp_tool: run_tests
{
  "testFile": "tests/integration/osce/osce-video-resources.spec.ts",
  "headed": true,
  "debug": false
}
```

**2. Monitor Results**
```
Show me test results
```

Claude will call:
```typescript
mcp_tool: get_test_results
```

**3. Analyze Failures**
```
Show me details of failed tests including screenshots
```

Claude will call:
```typescript
mcp_tool: get_failure_details
{
  "testName": "should display essential videos"
}
```

**4. Fix Bugs Automatically**
Claude will:
- Read the error message
- Analyze the screenshot
- Read the application code
- Identify the bug
- Fix the code using Edit tool
- Re-run the test

**5. Iterate Until All Pass**
```
Re-run failed tests
```

Claude will call:
```typescript
mcp_tool: rerun_failed_tests
{
  "headed": true
}
```

---

## Autonomous Testing Workflow

### Phase 1: Initial Test Run

```bash
# You say:
"Run all OSCE tests in headed mode and fix any errors you find"

# Claude does:
1. Calls mcp_tool: run_tests (OSCE suite)
2. Watches tests execute in browser
3. Receives results via MCP
4. Identifies 5 failed tests
```

### Phase 2: Error Analysis

```bash
# Claude automatically:
1. Calls mcp_tool: get_failure_details
2. Reviews screenshot of failed state
3. Reads error: "Element not found: [data-testid='video-thumbnail']"
4. Analyzes: Missing data-testid attribute in VideoCard component
```

### Phase 3: Code Fix

```bash
# Claude automatically:
1. Reads: /home/dev/Development/irStudy/frontend/src/components/osce/VideoCard.tsx
2. Identifies missing data-testid
3. Edits file to add: data-testid="video-thumbnail"
4. Saves changes
```

### Phase 4: Re-run and Verify

```bash
# Claude automatically:
1. Calls mcp_tool: rerun_failed_tests
2. Watches browser re-execute tests
3. Test now passes ✅
4. Moves to next failure
```

### Phase 5: Repeat Until All Pass

```bash
# Claude iterates:
- Fix error 1 → Re-run → Pass ✅
- Fix error 2 → Re-run → Pass ✅
- Fix error 3 → Re-run → Pass ✅
- Fix error 4 → Re-run → Pass ✅
- Fix error 5 → Re-run → Pass ✅

Final status: 65/65 tests passing 🎉
```

---

## Example Autonomous Session

### User Input
```
Run OSCE video resources tests and fix any bugs you find.
Keep iterating until all tests pass.
```

### Claude's Autonomous Actions

**Iteration 1:**
```
1. Running tests... (calling mcp_tool: run_tests)
   ✅ 60 passed
   ❌ 5 failed

2. Analyzing failures... (calling mcp_tool: get_failure_details)
   - Test: "should display essential videos section"
   - Error: "Element not found: h2:has-text('Essential Video Demonstrations')"
   - Screenshot: [shows page without video section]

3. Reading code... (using Read tool)
   - File: frontend/src/components/osce/OSCEDetails.tsx
   - Issue: Conditional rendering broken - videos.length check incorrect

4. Fixing bug... (using Edit tool)
   - Before: {videos.length > 0 && <VideoSection />}
   - After: {videos?.essential?.length > 0 && <VideoSection />}

5. Re-running tests... (calling mcp_tool: rerun_failed_tests)
   ✅ Test now passes!
```

**Iteration 2:**
```
1. Running remaining failures...
   ✅ 62 passed
   ❌ 3 failed

2. Analyzing failure...
   - Test: "should expand supplementary videos on click"
   - Error: "Button 'Show More' not found"
   - Screenshot: [shows no expand button]

3. Reading code...
   - File: frontend/src/components/osce/SupplementaryVideos.tsx
   - Issue: Button component missing

4. Fixing bug...
   - Added: <Button onClick={toggleExpand}>Show More</Button>

5. Re-running...
   ✅ Test now passes!
```

**Iteration 3:**
```
1. Running remaining failures...
   ✅ 64 passed
   ❌ 1 failed

2. Analyzing failure...
   - Test: "should have proper ARIA labels"
   - Error: "Button missing aria-label"

3. Fixing bug...
   - Added: aria-label="Expand supplementary videos"

4. Re-running...
   ✅ Test now passes!
```

**Final Result:**
```
All tests passing! 🎉
✅ 65/65 tests passed
Duration: 3 minutes 47 seconds
Bugs fixed: 5
Code quality: Production ready
```

---

## MCP Tools Available

### 1. `run_tests`
- Runs Playwright tests in headed mode
- Shows browser executing tests live
- Returns test results with failures

### 2. `get_test_results`
- Gets results from current session
- Shows pass/fail counts
- Lists all test statuses

### 3. `get_failure_details`
- Gets detailed failure information
- Includes error messages
- Includes screenshots (base64)
- Includes trace files

### 4. `rerun_failed_tests`
- Re-runs only failed tests
- Faster iteration
- Shows immediate feedback

### 5. `stop_tests`
- Stops running test session
- Useful if tests hang

---

## Benefits of Autonomous Testing

### 1. **Speed**
- Claude fixes bugs in seconds
- No manual debugging needed
- Iterates until all tests pass

### 2. **Thoroughness**
- Tests every button, message, interaction
- Catches edge cases
- Validates accessibility

### 3. **Consistency**
- Same fix quality every time
- No missed bugs
- Reproducible results

### 4. **Visual Feedback**
- Watch tests execute in browser
- See exactly what fails
- Understand user experience

### 5. **Zero Manual QA**
- Automated bug detection
- Automated bug fixing
- Automated verification

---

## Configuration Files

### package.json Scripts

Add these scripts to `/home/dev/Development/irStudy/testing/playwright/package.json`:

```json
{
  "scripts": {
    "mcp:server": "node mcp-server/playwright-mcp-server.ts",
    "test:autonomous": "echo 'Use Claude with MCP to run autonomous tests'",
    "test:headed": "playwright test --headed",
    "test:debug": "playwright test --debug"
  }
}
```

---

## Next Steps

1. **I'll create the MCP server** - Exposes Playwright to Claude
2. **I'll create test suite** - OSCE video resources (65 tests)
3. **You configure Claude Desktop** - Add MCP server to config
4. **You start autonomous session** - "Run tests and fix bugs"
5. **Claude does the rest** - Monitors, identifies, fixes, iterates

---

## Expected Outcome

**Before Autonomous Testing:**
- 0 tests written
- Unknown bugs lurking
- Manual QA required

**After Autonomous Testing:**
- 65+ tests passing
- All bugs found and fixed
- Production-ready code
- Zero manual work

**Time Investment:**
- Setup: 10 minutes
- Autonomous execution: 15-30 minutes
- Total: ~40 minutes for complete test coverage + bug fixes

---

Ready to start autonomous testing? Say "yes" and I'll:
1. Create the MCP server
2. Create the test suite
3. Guide you through Claude Desktop configuration
4. Watch Claude autonomously fix all bugs! 🤖
