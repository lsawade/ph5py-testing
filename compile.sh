#!/bin/bash
1;95;0c
# Get Settings
source ./vars.sh

# HDF5 directory
cd $HDF5_MAINDIR

if [ -d build ]; then
	rm -rf build
fi

mkdir build

pwd
cd build
echo $HDF5_DIR

# Configuration
cmake .. \
      --enable-shared \
      --enable-cxx \
      --enable-fortran \
      --enable-parallel \
      CC=$MPICC CXX=$MPICPP FC=$FC

# Installation
make -j

# make -j check
make -j install
