#!/bin/bash

echo "==> [Sparse Reconstruction] running sequential pipeline"

python3 /home/sfmop/workspace/SfM_SequentialPipeline.py "$1" "/home/sfmop/workspace/sparse_reconstruction"
