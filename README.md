# Structure from Motion (SfM)

This repository contains the source code to build an OCI container using Docker
used to run a structure from motion pipeline.
The container is designed to be used on a folder containing the dataset composed
of images from the object to reconstruct.

## Pipeline

For this repository the container makes use of the
[OpenMVG](https://github.com/openMVG/openMVG) and
[OpenMVS](https://github.com/cdcseacave/openMVS) projects. Both tools integrate
rather easily and be run on the CPU and even be placed into a container.
Optionally CUDA is can be used but this is *not* supported by this container.

The following diagram visualizes all the steps required to generate a 3D model
of the Brunsviga 13 RK:

```mermaid
flowchart LR
    A[Take Photos]
    B[Postprocess]
    C[Convert]
    D[Analysis]
    E[Feature Extraction]
    F[Compute Matches]
    G[Reconstruction]
    H[Convert Format]
    I[Dense Reconstruction]
    J[Mesh Reconstruction]

    subgraph Sequential Pipeline
        direction LR

        subgraph  ds [Dataset Generation]
            direction TB
            A -- RAW --> B -- PNG --> C -- JPG --> D
        end

        subgraph  og [OpenMVG]
            direction TB
            E --> F --> G
        end

        subgraph om [OpenMVS]
            direction TB
            H -- MVS --> I -- PLY --> J
        end

        ds --> og --> om
    end
```

The only input to the pipeline is a dataset of photos of the machine. These
where shot using a camera manufactured by Samsung with a NX2000 lens.
For getting the maximum quality out, the camera saves the images as SRW raw
files. In order to improve visual quality and reduce file size the raw images
are postprocessed with [RawTherapee](https://github.com/Beep6581/RawTherapee).
Improvements were made by sharpening, removing noise, removing dark shadows and
enhancing edges. The product are loss lessy compressed PNG files.
Unfortunately OpenMVG is unable to read EXIF data from PNG files which is
required in order to determine camera features such as focal length.
For this reason the PNG files are further converted into JPGs.
These are the actual files served as input for OpenMVG.

For further explanation of how OpenMVG works see their
[wiki](https://github.com/openMVG/openMVG/wiki/OpenMVG-on-your-image-dataset).

## Quick start

You can use the makefile in order to build the docker image:
```
make build
```

Then the pipeline can be run on a dataset stored in the `jpg` folder in your
working directory:
```
make run
```

The finished 3D model will be stored in
`output/reconstruction_sequential/scene.ply`.

## Dataset

The data set can be downloaded from
[here](https://cloud.montehaselino.de/s/bfGSCZ58R8JBN5a).
In order to not blow up the repository size these images are not included by
default as the entire dataset has a size of roughly 4 Gb.
I highly recommend to *only use download the JPG dataset* from
[here](https://cloud.montehaselino.de/s/WFXnTMigBmaLWzg) as this is only a few
megabytes in size.

Please take note that the dataset is licensed under CC BY-NC-SA 4.0.
A copy of this license is included in this repository as:
`DATASET_LICENSE` for further information.

You can use the following to download, extract and setup the dataset:
```
make pull
```

## Repository Automation

This repository contains automated actions for both building the Docker image
and automatically reconstructing the model.

### Image Build

In order to build the Docker image push a tag to the remote repository. This
will trigger a build action that will build the image and name it after the
repository and additionally tagging it with the tags name. Tagging a branch
with `v1.2.4` will cause the action to build and push a Docker image to the
GHCR under: `ghcr.io/brunsviga13rk/sfm:v1.2.4`. This can be skipped by writing
`Skip-Container-Build` into the HEAD commit message.

### Reconstruction

Whenever a push is done to the `main` branch the action will check if the HEAD
commit contains a message like: `Run-Reconstruct: v7.3.9`. In this case
the action will pull the image tagged by the version given in the previous
message and use this to reconstruct a 3D mesh. Upon success a release will be
created. Note that a release is only created in case the reconstruction is
triggered for a tag.
