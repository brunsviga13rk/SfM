FROM ubuntu:jammy AS builder

# Setup PATH for OpenMVG and OpenMVS
ENV PATH $PATH:/home/sfmop/openmvg/install/bin
ENV PATH $PATH:/home/sfmop/openmvs/make/bin

# install dependencies
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata; \
    apt-get install -y \
    cmake \
    build-essential \
    graphviz \
    git \
    coinor-libclp-dev \
    libceres-dev \
    libflann-dev \
    libjpeg-dev \
    liblemon-dev \
    libpng-dev \
    libtiff-dev \
    python3 \
    python3-dev \
    libcgal-dev \
    libeigen3-dev \
    libopencv-dev \
    libboost-iostreams-dev \
    libboost-program-options-dev \
    libboost-system-dev \
    libboost-serialization-dev \
    libcgal-dev \
    libcgal-qt5-dev; \
    apt-get autoclean && apt-get clean

# Create a new user SfM operator
RUN useradd -ms /bin/bash sfmop

ADD openmvg /home/sfmop/openmvg
ADD openmvs /home/sfmop/openmvs
ADD vcg /home/sfmop/vcg
RUN chown -R sfmop:sfmop /home/sfmop

# make sure NOT to build and run as root
USER sfmop

# ------------------------------
# OpenMVG

# Build OpenMVG
WORKDIR /home/sfmop/openmvg
RUN mkdir /home/sfmop/openmvg/build; \
    cd /home/sfmop/openmvg/build; \
    cmake -DCMAKE_BUILD_TYPE=RELEASE \
    -DCMAKE_INSTALL_PREFIX="/home/sfmop/openmvg/install" \
    -DOpenMVG_BUILD_TESTS=ON \
    -DOpenMVG_BUILD_EXAMPLES=OFF \
    -DCOINUTILS_INCLUDE_DIR_HINTS=/usr/include \
    -DLEMON_INCLUDE_DIR_HINTS=/usr/include/lemon \
    -DCLP_INCLUDE_DIR_HINTS=/usr/include \
    -DOSI_INCLUDE_DIR_HINTS=/usr/include \
    ../src; \
    make -j 4;

RUN cd /home/sfmop/openmvg/build && make test && make install;

# ------------------------------
# OpenMVS

ENV VCG_ROOT="/home/sfmop/vcg"

WORKDIR /home/sfmop/openmvs
RUN mkdir make; \
    cd make; \
    cmake .. -DCMAKE_BUILD_TYPE=Release; \
    cmake --build . -j4;

WORKDIR /home/sfmop/

FROM ubuntu:jammy AS runtime

RUN useradd -ms /bin/bash -u 1000 sfmop

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata; \
    apt-get install -y \
    cmake \
    build-essential \
    graphviz \
    git \
    coinor-libclp-dev \
    libceres-dev \
    libflann-dev \
    libjpeg-dev \
    liblemon-dev \
    libpng-dev \
    libtiff-dev \
    python3 \
    python3-dev \
    libcgal-dev \
    libeigen3-dev \
    libopencv-dev \
    libboost-iostreams-dev \
    libboost-program-options-dev \
    libboost-system-dev \
    libboost-serialization-dev \
    libcgal-dev \
    libcgal-qt5-dev \
    imagemagick; \
    apt-get autoclean && apt-get clean

# Copy binaries from build to runtime
COPY --from=builder /home/sfmop/openmvg/install/bin /home/sfmop/.local/bin
COPY --from=builder /home/sfmop/openmvs/make/bin /home/sfmop/.local/bin

ADD run-pipeline.sh /home/sfmop/
ADD sequential_pipeline.py /home/sfmop/
ADD openmvg/src/openMVG/exif/sensor_width_database/sensor_width_camera_database.txt /home/sfmop/

RUN chown -R sfmop:sfmop /home/sfmop

ENV PATH="$PATH:/home/sfmop/.local/bin"

USER sfmop
WORKDIR /home/sfmop/
RUN mkdir workspace

ENTRYPOINT [ "/bin/sh", "-c", "/home/sfmop/run-pipeline.sh /home/sfmop/dataset" ]
