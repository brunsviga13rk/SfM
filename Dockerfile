FROM ubuntu:jammy

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
    libcgal-dev libcgal-qt5-dev; \
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
    cmake ..; \
    cmake --build . -j4;

WORKDIR /home/sfmop/
