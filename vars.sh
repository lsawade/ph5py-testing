#!/bin/bash

# Download link
# HDF5_LINK="https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-1.12/hdf5-1.12.1/src/hdf5-1.12.1.tar.gz"

HDF5_LINK="https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-1.12/hdf5-1.12.2/src/CMake-hdf5-1.12.2.tar.gz"

# Package variables
export ROOT_DIR=$(pwd)
export HDF5_MAINDIR="${ROOT_DIR}/hdf5"
export HDF5_DIR="${HDF5_MAINDIR}/build"
export HDF5_FC="${HDF5_DIR}/bin/h5pfc"
export HDF5_CC="${HDF5_DIR}/bin/h5pcc"
export MPIFC_HDF5=$HDF5_FC
export HDF5_MPI="ON"

export PATH=${HDF5_DIR}/bin:${PATH}

# Compilers
export MPICC=mpicc
export MPICXX=mpic++
export MPIF90=mpif90


echo "Loaded"
echo "-----------------------------------------"
echo "ROOT_DIR:      $ROOT_DIR"
echo "HDF5_MAINDIR:  $HDF5_MAINDIR"
echo "HDF5_DIR:      $HDF5_DIR"
echo "HDF5_FC:       $HDF5_FC"
echo "HDF5_CC:       $HDF5_CC"
echo "MPIFC_HDF5:    $MPIFC_HDF5"
echo "HDF5_MPI:      $HDF5_MPI"

# Compilers
echo ""
echo "MPICC:  $MPICC"
echo "MPICPP: $MPICPP"
echo "MPIF90: $MPIF90"
echo "-----------------------------------------"
