#!/bin/bash
# Validate that all PRD agent assignments match actual agent files in the project

set -e

PROJECT_ROOT="/home/dev/Development/irStudy"
AGENTS_DIR="$PROJECT_ROOT/.claude/agents"
DASHBOARD_DB="/home/dev/Development/ralph-dashboard/dev.db"

echo "======================================"
echo "Agent Assignment Validation"
echo "======================================"
echo ""

# Check that agents directory exists
if [ ! -d "$AGENTS_DIR" ]; then
    echo "❌ ERROR: Agents directory not found: $AGENTS_DIR"
    exit 1
fi

echo "✅ Agents directory found: $AGENTS_DIR"
echo ""

# List all agent files
echo "Available agents in project:"
echo "----------------------------"
for agent_file in "$AGENTS_DIR"/*.md; do
    agent_name=$(grep "^name:" "$agent_file" | head -1 | cut -d: -f2 | xargs)
    filename=$(basename "$agent_file")
    echo "  - $agent_name (file: $filename)"
done
echo ""

# Get assigned agents from database
echo "Agents assigned to PRDs in Ralph Dashboard:"
echo "--------------------------------------------"
assigned_agents=$(sqlite3 "$DASHBOARD_DB" "SELECT DISTINCT assignedAgent FROM user_stories WHERE prdId IN (SELECT id FROM prds WHERE projectId IN (SELECT id FROM projects WHERE name='irStudy')) ORDER BY assignedAgent;")

echo "$assigned_agents" | while read -r agent_name; do
    if [ -z "$agent_name" ]; then
        continue
    fi

    # Check if agent file exists
    agent_file_count=$(find "$AGENTS_DIR" -name "*.md" -exec grep -l "^name: $agent_name$" {} \; 2>/dev/null | wc -l)

    if [ "$agent_file_count" -eq 0 ]; then
        echo "  ❌ $agent_name - NOT FOUND in $AGENTS_DIR"
        exit 1
    else
        agent_file=$(find "$AGENTS_DIR" -name "*.md" -exec grep -l "^name: $agent_name$" {} \; 2>/dev/null | head -1)
        echo "  ✅ $agent_name - $(basename "$agent_file")"
    fi
done

echo ""
echo "======================================"
echo "✅ All agent assignments are valid!"
echo "======================================"
echo ""
echo "Summary:"
sqlite3 "$DASHBOARD_DB" -column -header "SELECT assignedAgent as Agent, COUNT(*) as PRD_Count FROM user_stories WHERE prdId IN (SELECT id FROM prds WHERE projectId IN (SELECT id FROM projects WHERE name='irStudy')) GROUP BY assignedAgent ORDER BY assignedAgent;"
echo ""
echo "Ready for Ralph Dashboard execution!"
