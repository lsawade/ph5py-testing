#!/bin/bash

# Get Settings
source ./vars.sh

# HDF5 directory
cd $HDF5_MAINDIR

if [ -d build ]; then
	rm -rf $HDF5_BUILD_DIR
fi

mkdir $HDF5_BUILD_DIR

pwd
cd $HDF5_BUILD_DIR
pwd

# ./build-unix.sh

CC=$MPICC \
  FC=$MPIF90 \
  CXX=$MPICXX \
  cmake -G "Unix Makefiles" \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX=$HDF5_DIR \
  -DHDF5_ENABLE_PARALLEL=ON  \
  -DBUILD_SHARED_LIBS=ON \
  -DHDF5_BUILD_CPP_LIB=OFF \
  -DHDF5_BUILD_FORTRAN=ON \
  -DHDF5_ENABLE_THREADSAFE=OFF \
  ../hdf5-1.12.2/

cd build

make -j install

# # Configuration
# CC=$MPICC CXX=$MPICPP FC=$MPIF90 \
#   cmake .. 



# # Installation
# make -j

# # make -j check
# make -j install

