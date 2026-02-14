#!/bin/bash
# Run Ralph Task 1.2 - Cerner Components in tmux

set -e

echo "🚀 Starting Ralph Task 1.2 - Cerner PowerChart Components"
echo "Working Directory: /home/dev/Development/irStudy/emr-frontend"
echo ""

# Create the prompt for Ralph
RALPH_PROMPT="
# Task: Implement Cerner PowerChart Components (TASK 1.2)

## Context
You are Ralph, an autonomous AI development agent. You are implementing Task 1.2 of the EMR Practice System.

## Instructions
1. Read the complete PRD: /home/dev/Development/irStudy/emr-practice-system/ralph-prds/phase1/TASK_1.2_CERNER_COMPONENTS.md
2. Change directory to: /home/dev/Development/irStudy/emr-frontend
3. Implement all 3 components exactly as specified in the PRD:
   - src/components/cerner/CernerSidebar.tsx
   - src/components/cerner/PatientBanner.tsx
   - src/components/cerner/SOAPNoteEditor.tsx
4. Add all CSS to src/index.css
5. Create test page: src/pages/cerner/TestPage.tsx
6. Run validation checks
7. Report completion status

## Success Criteria
- All components render without errors
- TypeScript compilation succeeds
- Dev server runs without warnings
- Form validation works
- Auto-save functionality works
- Test page displays all components

## Constraints
- Follow PROJECT_CONSTRAINTS.md
- Use exact code from PRD (copy-paste ready)
- Test each component after creation
- No TypeScript errors allowed
- Must use Australian medical terminology

## Working Directory
cd /home/dev/Development/irStudy/emr-frontend

## Time Budget
16 hours estimated

Start implementation now.
"

# Send to tmux session
echo "📝 Sending task to tmux session: emr_implementation"
tmux send-keys -t emr_implementation "cd /home/dev/Development/irStudy" C-m
sleep 1
tmux send-keys -t emr_implementation "# Starting Ralph Task 1.2 - Cerner Components" C-m
tmux send-keys -t emr_implementation "# Reading PRD..." C-m
tmux send-keys -t emr_implementation "cat /home/dev/Development/irStudy/emr-practice-system/ralph-prds/phase1/TASK_1.2_CERNER_COMPONENTS.md" C-m

echo ""
echo "✅ Task sent to tmux session 'emr_implementation'"
echo ""
echo "📺 To monitor progress:"
echo "   tmux attach -t emr_implementation"
echo ""
echo "📊 To check status:"
echo "   tmux capture-pane -t emr_implementation -p | tail -50"
echo ""
echo "🔍 To verify files created:"
echo "   ls -la /home/dev/Development/irStudy/emr-frontend/src/components/cerner/"
echo ""
