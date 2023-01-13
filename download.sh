# Download HDF5 if it doesn't exist

source vars.sh

if [ ! -d $HDF5_MAINDIR ]; then

    mkdir hdf5

    # Get HDF5
    wget -O hdf5.tar.gz $HDF5_LINK
    tar -xzvf hdf5.tar.gz --strip-components=1 -C $HDF5_MAINDIR

    cd $ROOT_DIR
fi
