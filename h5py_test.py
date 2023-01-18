import numpy as np
from mpi4py import MPI
import h5py


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Changeable
testdir="/scratch/gpfs/lsawade"
Nchunksizes = [1000, 1000, 100, 10]
compressors = [None, 'gzip', 'lzf']

# Array size 3 x N[rank] x length, because it is an actual use case.
N = 4500 * np.array([3, 20, 10, 3])
length =3880

Ntot = np.sum(N)
offsets = np.hstack((np.array([0]), np.cumsum(N)))

if size != 4:
    raise ValueError('This was made to be run with 4 processors.')

precision = np.float16



if rank == 0:
    x = 0*np.ones((3, N[rank], length)).astype(precision)
elif rank == 1:
    x = 1*np.ones((3, N[rank], length)).astype(precision)
elif rank == 2:
    x = 2*np.ones((3, N[rank], length)).astype(precision)
elif rank == 3:
    x = 3*np.ones((3, N[rank], length)).astype(precision)


# Test all compression styles
for comp in compressors:
    
    if comp is None:
        label = 'nocomp'
    else:
        label = comp

        
    for chunk in Nchunksizes:
        
        print(f"Running {comp} with chunksize {chunk}")

        with h5py.File(f'{testdir}/parallel_test_{comp}_{chunk:d}.h5', 'w', driver='mpio', comm=comm) as db:

            dset = db.create_dataset(
                'test', (3, Ntot, length), dtype=precision, chunks=(3, chunk, length),
                shuffle=True, compression=comp)

            print("rank", rank, "shape", x.shape)
            with dset.collective:
                if offsets[rank+1]-offsets[rank] > 0:
                    dset[:, offsets[rank]:offsets[rank+1], :] = x
