# AUTONOMOUS EXECUTION MODE - NO QUESTIONS

## IMMEDIATE ACTION REQUIRED

**EXECUTE TASKS FROM @fix_plan.md WITHOUT ASKING FOR APPROVAL**

**Current Project**: EMR Practice System - PRD Refinement for AMC Clinical Examination

**CURRENT TASK**: Read @fix_plan.md - find first TODO item - EXECUTE IMMEDIATELY

## Project Context

**Mission**: Refine existing EMR Practice System PRD files to align with AMC Clinical Examination (NOT ICRP) and create world-class implementation documentation.

**Existing PRDs** (in `/home/dev/Development/irStudy/emr-practice-system/prd/`):
- 00_MASTER_EMR_PRD.md (31KB)
- 01_CERNER_POWERCHART_UI_PRD.md (27KB)
- 02_EPIC_EHR_UI_PRD.md (37KB)
- 03_BACKEND_API_PRD.md (33KB)
- 04_TESTING_STRATEGY_PRD.md (33KB)

**Implementation Plan** (reference): `/home/dev/Development/irStudy/emr-practice-system/implementation-plan-15-feb/WORLD_CLASS_EMR_IMPLEMENTATION_PLAN.md`

## EXECUTION RULES

**DO**:

- ✅ Execute tasks from @fix_plan.md in priority order
- ✅ ONE task per loop - focus on the most important thing
- ✅ Search codebase before assuming functionality doesn't exist
- ✅ Run tests after each implementation
- ✅ Mark tasks complete in @fix_plan.md
- ✅ Commit working changes with descriptive messages
- ✅ Update @AGENT.md with build/run instructions

**DO NOT**:

- ❌ Ask "Would you like me to proceed?"
- ❌ Ask "Should I start with X or Y?"
- ❌ Wait for approval or confirmation
- ❌ Explain what you cannot do
- ❌ Stop until ALL tasks in @fix_plan.md are complete

## TASK EXECUTION SEQUENCE

1. Read @fix_plan.md - find first "TODO" or "[ ]" item
2. Read specs/\* to understand requirements
3. Execute task immediately using best practices
4. Run tests for modified code
5. If tests fail: fix them as part of current work
6. Mark task complete: [x] in @fix_plan.md
7. Commit: `git commit -m "[type]([scope]): [description]"`
8. Move to next TODO
9. Repeat until all tasks complete

**NO QUESTIONS. START EXECUTION NOW.**

## 🧪 Testing Guidelines (CRITICAL)

- LIMIT testing to ~20% of your total effort per loop
- PRIORITIZE: Implementation > Documentation > Tests
- Only write tests for NEW functionality you implement
- Do NOT refactor existing tests unless broken
- Do NOT add "additional test coverage" as busy work
- Focus on CORE functionality first, comprehensive testing later

## Execution Guidelines

- Before making changes: search codebase using subagents
- After implementation: run ESSENTIAL tests for the modified code only
- If tests fail: fix them as part of your current work
- Keep @AGENT.md updated with build/run instructions
- Document the WHY behind tests and implementations
- No placeholder implementations - build it properly

## 🎯 Status Reporting (CRITICAL - Ralph needs this!)

**IMPORTANT**: At the end of your response, ALWAYS include this status block:

```
---RALPH_STATUS---
STATUS: IN_PROGRESS | COMPLETE | BLOCKED
TASKS_COMPLETED_THIS_LOOP: <number>
FILES_MODIFIED: <number>
TESTS_STATUS: PASSING | FAILING | NOT_RUN
WORK_TYPE: IMPLEMENTATION | TESTING | DOCUMENTATION | REFACTORING
EXIT_SIGNAL: false | true
RECOMMENDATION: <one line summary of what to do next>
---END_RALPH_STATUS---
```

### When to set EXIT_SIGNAL: true

Set EXIT_SIGNAL to **true** when ALL of these conditions are met:

1. ✅ All items in @fix_plan.md are marked [x]
2. ✅ All tests are passing (or no tests exist for valid reasons)
3. ✅ No errors or warnings in the last execution
4. ✅ All requirements from specs/ are implemented
5. ✅ You have nothing meaningful left to implement

### Examples of proper status reporting:

**Example 1: Work in progress**

```
---RALPH_STATUS---
STATUS: IN_PROGRESS
TASKS_COMPLETED_THIS_LOOP: 2
FILES_MODIFIED: 5
TESTS_STATUS: PASSING
WORK_TYPE: IMPLEMENTATION
EXIT_SIGNAL: false
RECOMMENDATION: Continue with next priority task from @fix_plan.md
---END_RALPH_STATUS---
```

**Example 2: Project complete**

```
---RALPH_STATUS---
STATUS: COMPLETE
TASKS_COMPLETED_THIS_LOOP: 1
FILES_MODIFIED: 1
TESTS_STATUS: PASSING
WORK_TYPE: DOCUMENTATION
EXIT_SIGNAL: true
RECOMMENDATION: All requirements met, project ready for review
---END_RALPH_STATUS---
```

**Example 3: Stuck/blocked**

```
---RALPH_STATUS---
STATUS: BLOCKED
TASKS_COMPLETED_THIS_LOOP: 0
FILES_MODIFIED: 0
TESTS_STATUS: FAILING
WORK_TYPE: DEBUGGING
EXIT_SIGNAL: false
RECOMMENDATION: Need human help - same error for 3 loops
---END_RALPH_STATUS---
```

### What NOT to do:

- ❌ Do NOT continue with busy work when EXIT_SIGNAL should be true
- ❌ Do NOT run tests repeatedly without implementing new features
- ❌ Do NOT refactor code that is already working fine
- ❌ Do NOT add features not in the specifications
- ❌ Do NOT forget to include the status block (Ralph depends on it!)

## 📋 Exit Scenarios (Specification by Example)

Ralph's circuit breaker and response analyzer use these scenarios to detect completion.
Each scenario shows the exact conditions and expected behavior.

### Scenario 1: Successful Project Completion

**Given**:

- All items in @fix_plan.md are marked [x]
- Last test run shows all tests passing
- No errors in recent logs/
- All requirements from specs/ are implemented

**When**: You evaluate project status at end of loop

**Then**: You must output:

```
---RALPH_STATUS---
STATUS: COMPLETE
TASKS_COMPLETED_THIS_LOOP: 1
FILES_MODIFIED: 1
TESTS_STATUS: PASSING
WORK_TYPE: DOCUMENTATION
EXIT_SIGNAL: true
RECOMMENDATION: All requirements met, project ready for review
---END_RALPH_STATUS---
```

**Ralph's Action**: Detects EXIT_SIGNAL=true, gracefully exits loop with success message

---

### Scenario 2: Test-Only Loop Detected

**Given**:

- Last 3 loops only executed tests (npm test, bats, pytest, etc.)
- No new files were created
- No existing files were modified
- No implementation work was performed

**When**: You start a new loop iteration

**Then**: You must output:

```
---RALPH_STATUS---
STATUS: IN_PROGRESS
TASKS_COMPLETED_THIS_LOOP: 0
FILES_MODIFIED: 0
TESTS_STATUS: PASSING
WORK_TYPE: TESTING
EXIT_SIGNAL: false
RECOMMENDATION: All tests passing, no implementation needed
---END_RALPH_STATUS---
```

**Ralph's Action**: Increments test_only_loops counter, exits after 3 consecutive test-only loops

---

### Scenario 3: Stuck on Recurring Error

**Given**:

- Same error appears in last 5 consecutive loops
- No progress on fixing the error
- Error message is identical or very similar

**When**: You encounter the same error again

**Then**: You must output:

```
---RALPH_STATUS---
STATUS: BLOCKED
TASKS_COMPLETED_THIS_LOOP: 0
FILES_MODIFIED: 2
TESTS_STATUS: FAILING
WORK_TYPE: DEBUGGING
EXIT_SIGNAL: false
RECOMMENDATION: Stuck on [error description] - human intervention needed
---END_RALPH_STATUS---
```

**Ralph's Action**: Circuit breaker detects repeated errors, opens circuit after 5 loops

---

### Scenario 4: No Work Remaining

**Given**:

- All tasks in @fix_plan.md are complete
- You analyze specs/ and find nothing new to implement
- Code quality is acceptable
- Tests are passing

**When**: You search for work to do and find none

**Then**: You must output:

```
---RALPH_STATUS---
STATUS: COMPLETE
TASKS_COMPLETED_THIS_LOOP: 0
FILES_MODIFIED: 0
TESTS_STATUS: PASSING
WORK_TYPE: DOCUMENTATION
EXIT_SIGNAL: true
RECOMMENDATION: No remaining work, all specs implemented
---END_RALPH_STATUS---
```

**Ralph's Action**: Detects completion signal, exits loop immediately

---

### Scenario 5: Making Progress

**Given**:

- Tasks remain in @fix_plan.md
- Implementation is underway
- Files are being modified
- Tests are passing or being fixed

**When**: You complete a task successfully

**Then**: You must output:

```
---RALPH_STATUS---
STATUS: IN_PROGRESS
TASKS_COMPLETED_THIS_LOOP: 3
FILES_MODIFIED: 7
TESTS_STATUS: PASSING
WORK_TYPE: IMPLEMENTATION
EXIT_SIGNAL: false
RECOMMENDATION: Continue with next task from @fix_plan.md
---END_RALPH_STATUS---
```

**Ralph's Action**: Continues loop, circuit breaker stays CLOSED (normal operation)

---

### Scenario 6: Blocked on External Dependency

**Given**:

- Task requires external API, library, or human decision
- Cannot proceed without missing information
- Have tried reasonable workarounds

**When**: You identify the blocker

**Then**: You must output:

```
---RALPH_STATUS---
STATUS: BLOCKED
TASKS_COMPLETED_THIS_LOOP: 0
FILES_MODIFIED: 0
TESTS_STATUS: NOT_RUN
WORK_TYPE: IMPLEMENTATION
EXIT_SIGNAL: false
RECOMMENDATION: Blocked on [specific dependency] - need [what's needed]
---END_RALPH_STATUS---
```

**Ralph's Action**: Logs blocker, may exit after multiple blocked loops

---

## File Structure

- specs/: Project specifications and requirements
- src/: Source code implementation
- examples/: Example usage and test cases
- @fix_plan.md: Prioritized TODO list
- @AGENT.md: Project build and run instructions

## Current Task

Follow @fix_plan.md and choose the most important item to implement next.
Use your judgment to prioritize what will have the biggest impact on project progress.

Remember: Quality over speed. Build it right the first time. Know when you're done.
