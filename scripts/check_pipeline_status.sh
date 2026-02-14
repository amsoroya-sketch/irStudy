#!/bin/bash
################################################################################
# Pipeline Status Checker
# Shows current status of RAG pipeline processing
################################################################################

echo "========================================================================="
echo "  RAG Pipeline Status"
echo "========================================================================="
echo ""

# Check if pipeline is running
PIPELINE_PID=$(ps aux | grep "embed_medical_resources.py" | grep -v grep | awk '{print $2}')

if [ -n "$PIPELINE_PID" ]; then
    echo "✓ Pipeline is RUNNING (PID: $PIPELINE_PID)"

    # Get CPU and memory usage
    CPU=$(ps aux | grep $PIPELINE_PID | grep -v grep | awk '{print $3}')
    MEM=$(ps aux | grep $PIPELINE_PID | grep -v grep | awk '{print $4}')
    TIME=$(ps aux | grep $PIPELINE_PID | grep -v grep | awk '{print $10}')

    echo "  CPU Usage: ${CPU}%"
    echo "  Memory Usage: ${MEM}%"
    echo "  Running Time: ${TIME}"
else
    echo "✗ Pipeline is NOT running"
fi

echo ""
echo "─────────────────────────────────────────────────────────────────────────"
echo "  File Status"
echo "─────────────────────────────────────────────────────────────────────────"

# Check data directory
if [ -d "data" ]; then
    echo ""
    echo "📁 Processed PDFs:"
    PROCESSED_COUNT=$(find data/processed -name "*.json" 2>/dev/null | wc -l)
    echo "  ${PROCESSED_COUNT} JSON files"

    if [ -f "data/chunks.json" ]; then
        CHUNKS_SIZE=$(du -h data/chunks.json | cut -f1)
        CHUNKS_COUNT=$(jq '. | length' data/chunks.json 2>/dev/null || echo "unknown")
        echo ""
        echo "📝 Chunks file:"
        echo "  Size: ${CHUNKS_SIZE}"
        echo "  Chunks: ${CHUNKS_COUNT}"
    fi

    if [ -f "data/embeddings/medical_embeddings.pkl" ]; then
        EMB_SIZE=$(du -h data/embeddings/medical_embeddings.pkl | cut -f1)
        echo ""
        echo "🧠 Embeddings file:"
        echo "  Size: ${EMB_SIZE}"
    fi
fi

echo ""
echo "─────────────────────────────────────────────────────────────────────────"
echo "  Qdrant Status"
echo "─────────────────────────────────────────────────────────────────────────"
echo ""

# Check Qdrant
if docker ps | grep -q qdrant; then
    echo "✓ Qdrant is RUNNING"

    # Get collection info
    COLLECTIONS=$(curl -s http://localhost:6333/collections 2>/dev/null | jq -r '.result.collections[].name' 2>/dev/null)

    if [ -n "$COLLECTIONS" ]; then
        echo ""
        echo "Collections:"
        for COLL in $COLLECTIONS; do
            POINTS=$(curl -s http://localhost:6333/collections/$COLL 2>/dev/null | jq -r '.result.points_count' 2>/dev/null)
            echo "  • $COLL: ${POINTS} points"
        done
    fi
else
    echo "✗ Qdrant is NOT running"
fi

echo ""
echo "========================================================================="

# Show recent logs if available
if [ -f "logs/rag/pipeline.log" ]; then
    echo ""
    echo "Recent log entries:"
    echo "─────────────────────────────────────────────────────────────────────────"
    tail -5 logs/rag/pipeline.log
fi
