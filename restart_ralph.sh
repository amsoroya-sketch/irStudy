#!/bin/bash
# Restart Ralph with corrected directive prompt

echo "🔄 Restarting Ralph with directive PROMPT.md..."
echo ""
echo "Changes made:"
echo "✅ PROMPT.md updated to be directive (no questions)"
echo "✅ Session files reset"
echo "✅ Ready to execute tasks autonomously"
echo ""
echo "Starting Ralph loop with:"
echo "  - Max calls: 50"
echo "  - Verbose mode: enabled"
echo "  - Prompt: PROMPT.md (directive version)"
echo ""

./ralph_loop.sh --calls 50 --verbose
