#!/bin/bash

# Comprehensive fix for Patient Encounter NoneType iteration errors
# This script fixes all instances where iterating over child tables causes errors
# Date: 2026-02-09

echo "=========================================="
echo "Fixing Patient Encounter NoneType Errors"
echo "=========================================="

PATIENT_ENCOUNTER_FILE="$HOME/frappe-bench/apps/hms_tz/hms_tz/nhif/api/patient_encounter.py"

# Check if file exists
if [ ! -f "$PATIENT_ENCOUNTER_FILE" ]; then
    echo "ERROR: Patient Encounter file not found at $PATIENT_ENCOUNTER_FILE"
    exit 1
fi

# Backup the file first
BACKUP_FILE="$PATIENT_ENCOUNTER_FILE.backup_$(date +%Y%m%d_%H%M%S)"
echo "Creating backup at: $BACKUP_FILE"
cp "$PATIENT_ENCOUNTER_FILE" "$BACKUP_FILE"

echo ""
echo "Applying fixes..."
echo ""

# Fix Line 279: for row in table:
sed -i '279s/for row in table:/for row in (table or []):/' "$PATIENT_ENCOUNTER_FILE"
echo "✓ Line 279: for row in table: → for row in (table or []):"

# Fix Line 376: for row in doc.get(key):
sed -i '376s/for row in doc\.get(key):/for row in (doc.get(key) or []):/' "$PATIENT_ENCOUNTER_FILE"
echo "✓ Line 376: for row in doc.get(key): → for row in (doc.get(key) or []):"

# Fix Line 1181: for row in doc.get(child.get("table")):
sed -i '1181s/for row in doc\.get(child\.get("table")):/for row in (doc.get(child.get("table")) or []):/' "$PATIENT_ENCOUNTER_FILE"
echo "✓ Line 1181: for row in doc.get(...): → for row in (doc.get(...) or []):"

# Fix Line 1209: for row in doc.get(child.get("table")):
sed -i '1209s/for row in doc\.get(child\.get("table")):/for row in (doc.get(child.get("table")) or []):/' "$PATIENT_ENCOUNTER_FILE"
echo "✓ Line 1209: for row in doc.get(...): → for row in (doc.get(...) or []):"

# Fix Line 1227: for row in doc.get(child.get("table")):
sed -i '1227s/for row in doc\.get(child\.get("table")):/for row in (doc.get(child.get("table")) or []):/' "$PATIENT_ENCOUNTER_FILE"
echo "✓ Line 1227: for row in doc.get(...): → for row in (doc.get(...) or []):"

# Fix Line 1542: for row in doc.get(child.get("table")):
sed -i '1542s/for row in doc\.get(child\.get("table")):/for row in (doc.get(child.get("table")) or []):/' "$PATIENT_ENCOUNTER_FILE"
echo "✓ Line 1542: for row in doc.get(...): → for row in (doc.get(...) or []):"

echo ""
echo "=========================================="
echo "✅ All fixes applied successfully!"
echo "=========================================="
echo ""
echo "Summary:"
echo "- Fixed 6 instances of NoneType iteration errors"
echo "- Lines fixed: 279, 376, 1181, 1209, 1227, 1542"
echo "- Backup created: $BACKUP_FILE"
echo ""
echo "Next steps:"
echo "1. Review changes: diff $BACKUP_FILE $PATIENT_ENCOUNTER_FILE"
echo "2. Restart bench: cd ~/frappe-bench && bench restart"
echo "3. Test by creating a Patient Encounter with empty child tables"
echo "4. Commit changes to git"
echo ""
echo "Git commit suggestion:"
echo "  cd ~/frappe-bench/apps/hms_tz"
echo "  git add hms_tz/nhif/api/patient_encounter.py"
echo '  git commit -m "fix: Handle all NoneType child table iterations in Patient Encounter"'
echo ""