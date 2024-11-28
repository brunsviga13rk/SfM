#!/bin/bash

echo "==> [Prepare] check dataset integrity"

find "${1}" -type f -print0 | xargs -0 -I {} sh -c 'identify {} || exit 255' || exit 1

echo "==> [Sparse Reconstruction] running sequential pipeline"

python3 /home/sfmop/sequential_pipeline.py "${1}" "/home/sfmop/sparse_reconstruction"
