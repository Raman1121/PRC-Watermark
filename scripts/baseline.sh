#!/bin/bash

PROJECT_ROOT="/raid/s2198939/PRC-Watermark"
cd "$PROJECT_ROOT"

TEST_PATH="results/prc_num_500_steps_50_fpr_1e-05_nowm_0/original_images_prc"
KEY_PATH="keys/prc_num_500_steps_50_fpr_1e-05_nowm_0.pkl"

IMG_EXTENSION="png"
ATTACK_TYPE="original"
DEVICE=5

# Check path exists, exit if not
if [ ! -d "$TEST_PATH" ]; then
    echo "Test path $TEST_PATH does not exist. Exiting."
    exit 1
fi

CUDA_VISIBLE_DEVICES=$DEVICE python decode.py --key_path $KEY_PATH \
    --attack_type $ATTACK_TYPE \
    --img_extension $IMG_EXTENSION \
    --test_path $TEST_PATH
