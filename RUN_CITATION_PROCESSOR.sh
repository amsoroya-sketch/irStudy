#!/bin/bash
cd /home/dev/Development/irStudy
echo "Starting citation addition process..."
python3 add_citations_systematic.py
echo ""
echo "Process complete. Check citation_addition_report.md for details."
