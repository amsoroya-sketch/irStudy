#!/bin/bash
# Execute Ralph Task 1.2 using Claude Code in tmux session

set -e

TMUX_SESSION="emr_implementation"
WORK_DIR="/home/dev/Development/irStudy/emr-frontend"
PRD_FILE="/home/dev/Development/irStudy/emr-practice-system/ralph-prds/phase1/TASK_1.2_CERNER_COMPONENTS.md"

echo "🚀 Executing Ralph Task 1.2 - Cerner PowerChart Components"
echo ""
echo "Session: $TMUX_SESSION"
echo "Working Directory: $WORK_DIR"
echo "PRD: $PRD_FILE"
echo ""

# Kill any running dev server first
echo "📦 Stopping any running dev server..."
tmux send-keys -t $TMUX_SESSION C-c
sleep 2

# Navigate to working directory
echo "📁 Navigating to working directory..."
tmux send-keys -t $TMUX_SESSION "cd $WORK_DIR" C-m
sleep 1

# Fix Tailwind CSS issue
echo "🔧 Fixing Tailwind CSS configuration..."
tmux send-keys -t $TMUX_SESSION "npm install -D @tailwindcss/postcss autoprefixer" C-m
sleep 20

# Update PostCSS config
echo "📝 Updating PostCSS configuration..."
tmux send-keys -t $TMUX_SESSION "cat > postcss.config.js << 'EOF'
export default {
  plugins: {
    '@tailwindcss/postcss': {},
    autoprefixer: {},
  },
}
EOF" C-m
sleep 2

# Now run Claude Code with the task
echo "🤖 Launching Claude Code to execute TASK 1.2..."
tmux send-keys -t $TMUX_SESSION "" C-m
tmux send-keys -t $TMUX_SESSION "# Starting Claude Code for Ralph Task 1.2" C-m
tmux send-keys -t $TMUX_SESSION "# Please execute the following:" C-m
tmux send-keys -t $TMUX_SESSION "# 1. Read PRD: cat $PRD_FILE" C-m
tmux send-keys -t $TMUX_SESSION "# 2. Implement all 3 Cerner components" C-m
tmux send-keys -t $TMUX_SESSION "# 3. Create test page" C-m
tmux send-keys -t $TMUX_SESSION "# 4. Validate implementation" C-m
tmux send-keys -t $TMUX_SESSION "" C-m

echo ""
echo "✅ Setup complete!"
echo ""
echo "📺 To attach to the session and monitor:"
echo "   tmux attach -t $TMUX_SESSION"
echo ""
echo "📝 To read the PRD in the session, run:"
echo "   cat $PRD_FILE | less"
echo ""
echo "🔍 Next steps in tmux session:"
echo "   1. Read the PRD file"
echo "   2. Start implementing components according to PRD"
echo "   3. Test each component after creation"
echo "   4. Run 'npm run dev' to verify"
echo ""
