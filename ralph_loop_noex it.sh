#!/bin/bash
# Temporary Ralph wrapper - disables early exit detection
# Allows Ralph to run through all tasks without premature completion detection

cd /home/dev/Development/irStudy

# Reset exit signals before each run
echo '{"test_only_loops": [], "done_signals": [], "completion_indicators": []}' > .exit_signals

# Disable exit on completion by setting high threshold
export MAX_CONSECUTIVE_DONE_SIGNALS=999
export MAX_CONSECUTIVE_TEST_LOOPS=999

# Run Ralph with original script
./ralph_loop.sh --calls 50 --verbose
