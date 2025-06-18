#!/bin/bash

PROJECT_ROOT="/raid/s2198939/PRC-Watermark"
cd "$PROJECT_ROOT"

ROTATION_ANGLE=15
IMG_DIR="results/prc_num_500_steps_50_fpr_1e-05_nowm_0/original_images_prc"

python attacks.py $IMG_DIR --rotation $ROTATION_ANGLE