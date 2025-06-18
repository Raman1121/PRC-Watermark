#!/bin/bash

PROJECT_ROOT="/raid/s2198939/PRC-Watermark"
cd "$PROJECT_ROOT"

ROTATION_ANGLE=5
IMG_DIR="results/prc_num_500_steps_50_fpr_1e-05_nowm_0/original_images_prc"

## Step 1: Run the attack script with the specified rotation angle
echo "Running rotation attack with angle $ROTATION_ANGLE degrees on images in $IMG_DIR..."
python attacks.py $IMG_DIR --rotation $ROTATION_ANGLE

## Step 2: Decode the watermarked images after the attack
echo "Decoding watermarked images after rotation attack..."

KEY_PATH="keys/prc_num_500_steps_50_fpr_1e-05_nowm_0.pkl"
ATTACK_TYPE="rotate_$ROTATION_ANGLE"

IMG_EXTENSION="jpg"
TEST_PATH="attack_results_sequential/rotate_$ROTATION_ANGLE"
DEVICE=1

# Check path exists, exit if not
if [ ! -d "$TEST_PATH" ]; then
    echo "Test path $TEST_PATH does not exist. Exiting."
    exit 1
fi

CUDA_VISIBLE_DEVICES=$DEVICE python decode.py --key_path $KEY_PATH \
    --attack_type $ATTACK_TYPE \
    --img_extension $IMG_EXTENSION \
    --test_path $TEST_PATH
