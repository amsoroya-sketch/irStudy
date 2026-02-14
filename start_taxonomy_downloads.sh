#!/bin/bash
# Parallel HEAL Image Downloads - Taxonomy-Based
# Generated from medical_image_taxonomy_v1.json
# Total: 831 nodes across 11 specialties

echo "============================================================"
echo "MEDICAL IMAGE DOWNLOAD PLAN"
echo "Based on taxonomy with 831 nodes"
echo "============================================================"
echo ""

# HIGH PRIORITY SPECIALTIES (Priority 1)
# Total: 10 specialties, 786 nodes
# Estimated images: 6105

echo "[1/10] Downloading cardiology (96 nodes, ~768 images)"
# python3 scripts/download_heal_comprehensive.py \
#     --specialties cardiology \
#     --images-per-topic 8 \
#     --output data/medical_images &

echo "[2/10] Downloading dermatology (71 nodes, ~568 images)"
# python3 scripts/download_heal_comprehensive.py \
#     --specialties dermatology \
#     --images-per-topic 8 \
#     --output data/medical_images &

echo "[3/10] Downloading haematology (60 nodes, ~480 images)"
# python3 scripts/download_heal_comprehensive.py \
#     --specialties haematology \
#     --images-per-topic 8 \
#     --output data/medical_images &

echo "[4/10] Downloading neurology (100 nodes, ~800 images)"
# python3 scripts/download_heal_comprehensive.py \
#     --specialties neurology \
#     --images-per-topic 8 \
#     --output data/medical_images &

echo "[5/10] Downloading gastroenterology (88 nodes, ~704 images)"
# python3 scripts/download_heal_comprehensive.py \
#     --specialties gastroenterology \
#     --images-per-topic 8 \
#     --output data/medical_images &

echo "[6/10] Downloading endocrinology (72 nodes, ~576 images)"
# python3 scripts/download_heal_comprehensive.py \
#     --specialties endocrinology \
#     --images-per-topic 8 \
#     --output data/medical_images &

echo "[7/10] Downloading obstetrics_gynaecology (79 nodes, ~632 images)"
# python3 scripts/download_heal_comprehensive.py \
#     --specialties obstetrics_gynaecology \
#     --images-per-topic 8 \
#     --output data/medical_images &

echo "[8/10] Downloading paediatrics (84 nodes, ~672 images)"
# python3 scripts/download_heal_comprehensive.py \
#     --specialties paediatrics \
#     --images-per-topic 8 \
#     --output data/medical_images &

echo "[9/10] Downloading emergency_medicine (75 nodes, ~600 images)"
# python3 scripts/download_heal_comprehensive.py \
#     --specialties emergency_medicine \
#     --images-per-topic 8 \
#     --output data/medical_images &

echo "[10/10] Downloading respiratory (61 nodes, ~305 images)"
# python3 scripts/download_heal_comprehensive.py \
#     --specialties respiratory \
#     --images-per-topic 5 \
#     --output data/medical_images &


echo "Waiting for HIGH priority downloads to complete..."
# wait

# MEDIUM PRIORITY SPECIALTIES (Priority 2)
# Total: 1 specialties, 45 nodes

echo "[1/1] Downloading psychiatry (45 nodes)"
# python3 scripts/download_heal_comprehensive.py \
#     --specialties psychiatry \
#     --images-per-topic 5 \
#     --output data/medical_images &


echo ""
echo "============================================================"
echo "DOWNLOAD PLAN SUMMARY"
echo "============================================================"
echo "  cardiology: 96 nodes × 8 images = ~768 images"
echo "  dermatology: 71 nodes × 8 images = ~568 images"
echo "  haematology: 60 nodes × 8 images = ~480 images"
echo "  neurology: 100 nodes × 8 images = ~800 images"
echo "  gastroenterology: 88 nodes × 8 images = ~704 images"
echo "  endocrinology: 72 nodes × 8 images = ~576 images"
echo "  obstetrics_gynaecology: 79 nodes × 8 images = ~632 images"
echo "  paediatrics: 84 nodes × 8 images = ~672 images"
echo "  emergency_medicine: 75 nodes × 8 images = ~600 images"
echo "  respiratory: 61 nodes × 5 images = ~305 images"
echo "  psychiatry: 45 nodes × 5 images = ~225 images"

echo ""
echo "TOTALS:"
echo "  Specialties: 11"
echo "  Nodes: 831"
echo "  Estimated images: ~6330"
echo "  Estimated time: 3.5 hours (with 2s rate limit)"
echo ""
echo "============================================================"
echo "NOTE: Commands are commented out. Uncomment to execute."
echo "For parallel execution, use '&' and 'wait' as shown above."
echo "============================================================"
