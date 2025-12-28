#!/bin/bash
cd /home/dev/Development/irStudy
python3 process_citations.py
cat citation_work_batch.json | jq '.claims_by_file | keys[]' | head -20
