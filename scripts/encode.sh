# Script for generating watermaked images

#!/bin/bash

PROJECT_ROOT="/raid/s2198939/PRC-Watermark"
cd "$PROJECT_ROOT"

mkdir -p "keys"

NUM_IMAGES=500
WATERMARKING_METHOD="tr"

CUDA_VISIBLE_DEVICES=2

CUDA_VISIBLE_DEVICES=$CUDA_VISIBLE_DEVICES python encode.py --test_num $NUM_IMAGES --method $WATERMARKING_METHOD