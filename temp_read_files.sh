#!/bin/bash

echo "=== OSCE METHODOLOGY GUIDE ==="
cat "/home/dev/Development/irStudy/OSCE_METHODOLOGY_GUIDE.html" | head -500

echo -e "\n\n=== CARDIOVASCULAR RESPIRATORY EXAM ==="
cat "/home/dev/Development/irStudy/ICRP_OSCE_Preparation/Medicine/02_Physical_Examination_Cardiovascular_Respiratory.html" | head -300

echo -e "\n\n=== ABDOMINAL NEUROLOGICAL EXAM ==="
cat "/home/dev/Development/irStudy/ICRP_OSCE_Preparation/Medicine/03_Physical_Examination_Abdominal_Neurological.html" | head -300

echo -e "\n\n=== PDF FILES AVAILABLE ==="
ls -lh "/home/dev/Development/irStudy/Clinical_Examination_Split/"
