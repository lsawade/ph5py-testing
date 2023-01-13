import numpy as np
from mpi4py import MPI
import h5py


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()


N = np.array([2, 1, 3, 2])
Ntot = np.sum(N)
offsets = np.hstack((np.array([0]), np.cumsum(N)))

if size != 4:
    raise ValueError('This was made to be run with 4 processors.')

precision = np.float16

length = 5

if rank == 0:
    x = 0*np.ones((2, length)).astype(precision)
elif rank == 1:
    x = 1*np.ones((1, length)).astype(precision)
elif rank == 2:
    x = 2*np.ones((3, length)).astype(precision)
elif rank == 3:
    x = 3*np.ones((2, length)).astype(precision)


# Test all compression styles
for comp in [None, 'gzip', 'lzf']:
    
    if comp is None:
        label = 'nocomp'
    else:
        label = comp
        
    with h5py.File(f'parallel_test_{comp}.h5', 'w', driver='mpio', comm=comm) as db:

        dset = db.create_dataset(
            'test', (Ntot, length), dtype=precision,
            chunks=(1, length), compression=comp)

        with dset.collective:
            if offsets[rank+1]-offsets[rank] > 0:
                print(rank, np.min(x), np.max(x))
                dset[offsets[rank]:offsets[rank+1], :] = x
