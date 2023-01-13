#!/bin/bash

# Get Settings
source ./vars.sh

# HDF5 directory
cd $HDF5_MAINDIR

if [ -d build ]; then
	rm -rf build
fi
mkdir build

pwd
echo $HDF5_DIR

# Configuration
./configure --enable-shared --enable-parallel \
    --enable-fortran --enable-fortran2003 \
    --prefix=$HDF5_DIR CC=$MPICC FC=$MPIF90

# Installation
make -j
# make -j check
make -j install
