#!/bin/bash
# Monitor Ralph EMR Sessions API Implementation

echo "🔍 Ralph EMR Sessions API Monitor"
echo "=================================="
echo ""
echo "📋 Session: ralph-emr"
echo "📁 Working Directory: /home/dev/Development/irStudy"
echo "📄 PRD: PRD-EMR-SESSIONS-API.md"
echo "📝 Log File: ralph-emr-execution.log"
echo ""

# Check if tmux session exists
if tmux has-session -t ralph-emr 2>/dev/null; then
    echo "✅ Ralph session is RUNNING"
    echo ""

    # Show last 30 lines of output
    echo "📊 Last 30 lines of output:"
    echo "----------------------------"
    tmux capture-pane -t ralph-emr -p | tail -30
    echo ""

    # Check log file if it exists
    if [ -f ralph-emr-execution.log ]; then
        echo "📈 Progress Summary:"
        echo "----------------------------"
        
        # Count phases
        echo "Phases completed: $(grep -c "Phase.*Complete\|Phase.*PASS" ralph-emr-execution.log 2>/dev/null || echo 0)"
        
        # Check for test results
        echo ""
        echo "🧪 Test Results (if available):"
        grep -E "passed|failed|error" ralph-emr-execution.log 2>/dev/null | tail -5 || echo "No test results yet"
        
        echo ""
        echo "📊 Log file size: $(du -h ralph-emr-execution.log 2>/dev/null | cut -f1 || echo 'N/A')"
    fi

    echo ""
    echo "Commands:"
    echo "  View live: tmux attach -t ralph-emr"
    echo "  View log: tail -f ralph-emr-execution.log"
    echo "  Kill: tmux kill-session -t ralph-emr"
else
    echo "❌ Ralph session NOT running"
    
    if [ -f ralph-emr-execution.log ]; then
        echo ""
        echo "📄 Found log file from previous run"
        echo "Final output (last 50 lines):"
        echo "----------------------------"
        tail -50 ralph-emr-execution.log
    fi
fi

echo ""
