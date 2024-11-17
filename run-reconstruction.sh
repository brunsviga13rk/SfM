#!/bin/bash

echo "==> [Host] running automatic reconstruction pipeline"

# start SfM container, mount the current working directory
# and start the full automatic reconstruction pipeline
docker run -it \
    -v "./:/home/sfmop/workspace" \
    brunsviga13rk-sfm:git \
    /home/sfmop/workspace/run-pipeline.sh "/home/sfmop/workspace/$1"
