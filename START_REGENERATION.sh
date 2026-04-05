#!/bin/bash
# Start respiratory OSCE regeneration

cd /home/dev/Development/irStudy

# Make scripts executable
chmod +x execute_respiratory_osce_regeneration.sh
chmod +x scripts/regenerate_respiratory_osces_complete.py

# Execute
bash execute_respiratory_osce_regeneration.sh
