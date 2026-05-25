#!/bin/bash
#
# Fix Database Schema - Add Missing Token Columns
#
# Issue: Python models include verification_token and reset_token fields
#        but PostgreSQL database is missing these columns
#
# Solution: Add columns to all content tables
#
# Usage:
#   export DATABASE_PASSWORD="3K4cnsyxYOOHGzCcxmOesU7PExXHCMaH"
#   export DATABASE_HOST="localhost"
#   export DATABASE_PORT="5433"
#   bash scripts/fix_database_schema.sh

set -e  # Exit on error

echo "========================================="
echo "Database Schema Fix Script"
echo "========================================="
echo "Date: $(date)"
echo ""

# Database connection parameters
DB_HOST="${DATABASE_HOST:-localhost}"
DB_PORT="${DATABASE_PORT:-5433}"
DB_NAME="${DATABASE_NAME:-irstudy_medical}"
DB_USER="${DATABASE_USER:-postgres}"
DB_PASSWORD="${DATABASE_PASSWORD}"

if [ -z "$DB_PASSWORD" ]; then
    echo "❌ ERROR: DATABASE_PASSWORD environment variable not set"
    exit 1
fi

export PGPASSWORD="$DB_PASSWORD"

echo "Connection Details:"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo ""

# Test connection
echo "Testing database connection..."
if ! psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" > /dev/null 2>&1; then
    echo "❌ ERROR: Cannot connect to database"
    echo "   Please check:"
    echo "   - PostgreSQL is running (docker ps | grep postgres)"
    echo "   - DATABASE_PASSWORD is correct"
    echo "   - Host and port are correct"
    exit 1
fi
echo "✓ Database connection successful"
echo ""

# Function to add columns to a table
add_token_columns() {
    local table_name=$1
    echo "Processing table: $table_name"

    # Add verification_token column
    echo "  Adding verification_token column..."
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<SQL
DO \$\$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='$table_name' AND column_name='verification_token'
    ) THEN
        ALTER TABLE $table_name ADD COLUMN verification_token VARCHAR(255);
        RAISE NOTICE '  ✓ Added verification_token column';
    ELSE
        RAISE NOTICE '  ⚠ verification_token column already exists (skipped)';
    END IF;
END \$\$;
SQL

    # Add verification_token_created_at column
    echo "  Adding verification_token_created_at column..."
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<SQL
DO \$\$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='$table_name' AND column_name='verification_token_created_at'
    ) THEN
        ALTER TABLE $table_name ADD COLUMN verification_token_created_at TIMESTAMP WITH TIME ZONE;
        RAISE NOTICE '  ✓ Added verification_token_created_at column';
    ELSE
        RAISE NOTICE '  ⚠ verification_token_created_at column already exists (skipped)';
    END IF;
END \$\$;
SQL

    # Add reset_token column
    echo "  Adding reset_token column..."
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<SQL
DO \$\$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='$table_name' AND column_name='reset_token'
    ) THEN
        ALTER TABLE $table_name ADD COLUMN reset_token VARCHAR(255);
        RAISE NOTICE '  ✓ Added reset_token column';
    ELSE
        RAISE NOTICE '  ⚠ reset_token column already exists (skipped)';
    END IF;
END \$\$;
SQL

    # Add reset_token_created_at column
    echo "  Adding reset_token_created_at column..."
    psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<SQL
DO \$\$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='$table_name' AND column_name='reset_token_created_at'
    ) THEN
        ALTER TABLE $table_name ADD COLUMN reset_token_created_at TIMESTAMP WITH TIME ZONE;
        RAISE NOTICE '  ✓ Added reset_token_created_at column';
    ELSE
        RAISE NOTICE '  ⚠ reset_token_created_at column already exists (skipped)';
    END IF;
END \$\$;
SQL

    echo "  ✅ Completed table: $table_name"
    echo ""
}

echo "========================================="
echo "Adding Token Columns to Tables"
echo "========================================="
echo ""

# Add columns to all content tables
add_token_columns "mcqs"
add_token_columns "osces"
add_token_columns "patient_personas"
add_token_columns "mock_patients"
add_token_columns "mock_exams"

echo "========================================="
echo "Verification"
echo "========================================="
echo ""

# Verify all columns exist
echo "Verifying schema changes..."
VERIFICATION_RESULT=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -t <<SQL
SELECT
    table_name,
    COUNT(CASE WHEN column_name = 'verification_token' THEN 1 END) as has_verification_token,
    COUNT(CASE WHEN column_name = 'verification_token_created_at' THEN 1 END) as has_verification_created,
    COUNT(CASE WHEN column_name = 'reset_token' THEN 1 END) as has_reset_token,
    COUNT(CASE WHEN column_name = 'reset_token_created_at' THEN 1 END) as has_reset_created
FROM information_schema.columns
WHERE table_name IN ('mcqs', 'osces', 'patient_personas', 'mock_patients', 'mock_exams')
  AND column_name IN ('verification_token', 'verification_token_created_at', 'reset_token', 'reset_token_created_at')
GROUP BY table_name
ORDER BY table_name;
SQL
)

echo "$VERIFICATION_RESULT" | while IFS='|' read -r table v_token v_created r_token r_created; do
    # Trim whitespace
    table=$(echo "$table" | xargs)
    v_token=$(echo "$v_token" | xargs)
    v_created=$(echo "$v_created" | xargs)
    r_token=$(echo "$r_token" | xargs)
    r_created=$(echo "$r_created" | xargs)

    if [ -n "$table" ]; then
        echo "Table: $table"
        if [ "$v_token" = "1" ] && [ "$v_created" = "1" ] && [ "$r_token" = "1" ] && [ "$r_created" = "1" ]; then
            echo "  ✅ All 4 token columns present"
        else
            echo "  ❌ Missing columns: v_token=$v_token, v_created=$v_created, r_token=$r_token, r_created=$r_created"
        fi
    fi
done

echo ""
echo "========================================="
echo "Content Count Verification"
echo "========================================="
echo ""

# Check content counts
echo "Current database content:"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<SQL
SELECT 'MCQs' as content_type, COUNT(*) as count FROM mcqs
UNION ALL
SELECT 'OSCEs', COUNT(*) FROM osces
UNION ALL
SELECT 'EMR Personas', COUNT(*) FROM patient_personas
UNION ALL
SELECT 'Mock Patients', COUNT(*) FROM mock_patients
UNION ALL
SELECT 'Mock Exams', COUNT(*) FROM mock_exams
ORDER BY content_type;
SQL

echo ""
echo "========================================="
echo "✅ Schema Fix Complete"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Run import scripts if content is missing"
echo "2. Run backend tests to verify schema: ./run_tests.sh"
echo "3. Start backend server: uvicorn src.main:app --reload --port 8001"
echo ""
