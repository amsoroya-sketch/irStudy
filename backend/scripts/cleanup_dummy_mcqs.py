#!/usr/bin/env python3
"""
Script to remove dummy/placeholder MCQs from the database.

Identifies and deletes MCQs with placeholder content patterns:
- Options containing "Option A", "Option B", etc.
- Generic question patterns
- Placeholder IDs
"""

import psycopg2
import sys
from datetime import datetime

def connect_db():
    """Connect to the PostgreSQL database."""
    return psycopg2.connect(
        host="localhost",
        port=5433,
        database="irstudy_medical",
        user="postgres",
        password="3K4cnsyxYOOHGzCcxmOesU7PExXHCMaH"
    )

def analyze_mcqs(cursor):
    """Analyze MCQ patterns and identify dummy MCQs."""

    # Count dummy MCQs by different patterns
    cursor.execute("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN options::text LIKE '%Option A%' AND options::text LIKE '%Option B%' THEN 1 ELSE 0 END) as dummy_by_options,
            SUM(CASE WHEN question_text LIKE '%Clinical scenario for%' AND question_text LIKE '%Question about%' THEN 1 ELSE 0 END) as dummy_by_question
        FROM mcqs
    """)

    row = cursor.fetchone()
    print(f"\n=== Analysis ===")
    print(f"Total MCQs: {row[0]}")
    print(f"Dummy MCQs (by options pattern): {row[1]}")
    print(f"Dummy MCQs (by question pattern): {row[2]}")

    return row[1]  # Return count of dummy MCQs

def backup_mcqs(cursor):
    """Create a backup table of MCQs before deletion."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_table = f"mcqs_backup_{timestamp}"

    print(f"\n=== Creating Backup ===")
    print(f"Backup table: {backup_table}")

    cursor.execute(f"""
        CREATE TABLE {backup_table} AS
        SELECT * FROM mcqs
        WHERE options::text LIKE '%Option A%'
        AND options::text LIKE '%Option B%'
    """)

    cursor.execute(f"SELECT COUNT(*) FROM {backup_table}")
    count = cursor.fetchone()[0]
    print(f"Backed up {count} dummy MCQs to {backup_table}")

    return backup_table

def delete_dummy_mcqs(cursor, dry_run=True):
    """Delete dummy MCQs from the database."""

    if dry_run:
        print(f"\n=== DRY RUN MODE ===")
        print("Showing what would be deleted (no actual deletion)")

        # Show sample dummy MCQs
        cursor.execute("""
            SELECT question_id, specialty, question_text
            FROM mcqs
            WHERE options::text LIKE '%Option A%'
            AND options::text LIKE '%Option B%'
            LIMIT 5
        """)

        print("\nSample MCQs to be deleted:")
        for row in cursor.fetchall():
            print(f"  - {row[0]} ({row[1]}): {row[2][:60]}...")

        cursor.execute("""
            SELECT COUNT(*)
            FROM mcqs
            WHERE options::text LIKE '%Option A%'
            AND options::text LIKE '%Option B%'
        """)
        count = cursor.fetchone()[0]
        print(f"\nTotal MCQs to be deleted: {count}")

    else:
        print(f"\n=== DELETING DUMMY MCQs ===")

        cursor.execute("""
            DELETE FROM mcqs
            WHERE options::text LIKE '%Option A%'
            AND options::text LIKE '%Option B%'
        """)

        deleted_count = cursor.rowcount
        print(f"Deleted {deleted_count} dummy MCQs")

        # Verify remaining MCQs
        cursor.execute("SELECT COUNT(*) FROM mcqs")
        remaining = cursor.fetchone()[0]
        print(f"Remaining MCQs: {remaining}")

        return deleted_count

def main():
    """Main execution function."""
    print("=" * 60)
    print("MCQ Database Cleanup Utility")
    print("=" * 60)

    # Check for dry-run flag
    dry_run = "--execute" not in sys.argv

    if dry_run:
        print("\n⚠️  DRY RUN MODE - No changes will be made")
        print("To execute deletion, run with --execute flag")
    else:
        print("\n🔴 EXECUTION MODE - Changes will be made!")
        response = input("\nAre you sure you want to delete dummy MCQs? (yes/no): ")
        if response.lower() != "yes":
            print("Aborted.")
            return

    conn = connect_db()
    cursor = conn.cursor()

    try:
        # Analyze current state
        dummy_count = analyze_mcqs(cursor)

        if dummy_count == 0:
            print("\n✅ No dummy MCQs found. Database is clean!")
            return

        if not dry_run:
            # Create backup before deletion
            backup_table = backup_mcqs(cursor)

        # Delete dummy MCQs
        delete_dummy_mcqs(cursor, dry_run)

        if not dry_run:
            conn.commit()
            print("\n✅ Database cleanup completed successfully!")
            print(f"Backup saved in table: {backup_table}")
        else:
            print("\n✅ Dry run completed. Use --execute to perform deletion.")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
