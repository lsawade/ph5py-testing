# Installing Parallel `HDF5` and `h5py`

This requires working `MPI` compilers!

## 1. Make conda environment

```bash
conda create -n ph5 python=3.10
conda activate ph5

# On Mac
conda install -y wget
```

## 2. Install Parallel HDF5

First step here, since you cloned this repo, is to enter

```bash
cd /path/to/ph5test
```

Then, we have to download the HDF5. Here, we chose to download version `1.12.2`
for no particular reason.

```bash
./download.sh
```

After downloading the HDF5 installation files, go ahead and edit
`vars.sh` to adjust the two MPI compilers to match your local ones:

```bash
...
# Compilers
export MPICC=mpicc
export MPIF90=mpif90
...
```

Then, compile HDF5

```bash
./compile.sh
```


## 3. Install `h5py` with PHDF5 bindings

To install `h5py` we just need to get the variables from the `vars.sh`
and run the one-liner:
```bash
CC=$MPICC HDF5_MPI=$HDF5_MPI HDF5_DIR=$HDF5_DIR pip install --no-binary=h5py h5py
```

## 4. Test installation

Simply run the test script  

```bash
mpiexec -n 3 python h5py_test.py
```

To see whether writing worked, let's read the files

```bash
python h5py_read.py
```

Note that we do not need `MPI` here. Also, for `h5dump` to work it needs to know
where `LibLZF` is.

`h5py_test.py` started very small but has eveolved a lot to test a bunch of things. This includes
structure of the chunks, compression, quantization, and serial vs. parallel I/O, all of which are
controlled at the top of the file in form of lists.
