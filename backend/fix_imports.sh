#!/bin/bash
# Fix relative imports to absolute imports in backend Python files

cd /home/dev/Development/irStudy/backend/src

echo "Fixing imports in backend Python files..."

# Fix api/v1/router.py
sed -i 's|from api\.v1 import|from src.api.v1 import|g' api/v1/router.py

# Fix all Python files in api/v1/
for file in api/v1/{auth,users,mcqs,osces,progress}.py; do
    echo "Fixing $file"
    sed -i 's|^from db\.|from src.db.|g' "$file"
    sed -i 's|^from auth\.|from src.auth.|g' "$file"
    sed -i 's|^from schemas\.|from src.schemas.|g' "$file"
done

echo "✅ Import fixes complete"
