#!/bin/env python

from mpi4py import MPI
import math
import h5py
import numpy as np
import sys

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

def roundup(x, N):
    return math.ceil(x / N) * N

# MUST CHANGE
testdir="/scratch/gpfs/lsawade" ### CHANGE THIS ###

# CHANGEABLE
Nchunksizes = [1000] #, 100, 10, 1]
compressors = ['lzf'] #, 'gzip', None]'
encoded = [0] #,1]
encoding_level = [8,16,32] # Irrelevant if encoded is '0'

# The above sets the test setup. That is, all
# list will be looped over:
# - the directory where to save the hdf5 files
# - the format in which HDF5 stores the chunks in the second dimension
# - the 

# Array size 3 x N[rank] x length, because it is an actual use case.
Nproc = 3
if rank==0:
    # Instead of setting the array length per slice manually we can
    # 
    # N = np.random.randint(30000, 50000, size=Nproc).astype('i')

    # Number of elements per slice 
    N = np.array([349017, 271089, 371089], dtype='i')
else:
    N = np.empty(Nproc, dtype='i')

# Broadcast the array (important if N is randomly selected )
comm.Bcast(N, root=0)

# Third dimension
length = 3725

# Total final array length in second dimension
Ntot = np.sum(N)

# Offsets in the final array on each processor
offsets = np.hstack((np.array([0]), np.cumsum(N)))

# Some general info
if rank == 0:
    print(N, flush=True)
    print("Total number of of elements:", Ntot, flush=True)
    print("Last offset:                ", offsets[-1], flush=True)

# Making sure that every core is writing
if size != len(N):
    raise ValueError(f'This was made to be run with {Nproc}  processors.')

# Setting the precision for the HDF5 array
pprecision = np.float16

# Creating a large random array with some what repeatable indeces
# specific to the slice
x_original = np.random.randint(-60000, 60000, size=(3, N[rank], length)).astype(np.float32)/60000.0

# Move on with a reduced precision version of the array
x = 1.0*x_original.astype(pprecision)


# Loop over with or without encoding
for _encoded in encoded:

    if _encoded:

        # Encoding
        encoding_level = "16"
        encoding_level = int(encoding_level)

        if encoding_level == 8:
            precision = np.uint8
        elif encoding_level == 16:
            precision = np.uint16
        elif encoding_level == 32:
            precision = np.uint32
        else:
            raise ValueError('Not implemented.')


        # Get global minimum
        offset = np.array([np.min(x_original)], dtype=np.float32)
        comm.Allreduce(offset, offset, op=MPI.MIN)

        # Make data positive.
        x = x_original - offset

        # Amplitude normalization => [0, 1]
        normal_factor = np.array([np.max(x)], dtype=np.float32)
        comm.Allreduce(normal_factor, normal_factor, op=MPI.MAX)

        # Normalized
        x = x / normal_factor

        # Encode with 16bit unsigned integer 
        x = np.asarray(x * (2 ** encoding_level - 1)).astype(precision)


    # Loop over compressors
    for comp in compressors:

        if comp is None:
            label = 'nocomp'
        else:
            label = comp


        # Loop over chunksizes
        for chunk in Nchunksizes:
        
            if rank == 0:
                print(f"Running {comp} compression, chunksize {chunk}, encoded {_encoded}.", flush=True)
                print("============================================================\n", flush=True)

            # If True the file wil write in serial, this is encredible slow for compression
            # and hence very undesireable. I initially thought this may be a good idea to setup
            # the processing like this, because the bottleneck is the I/O and not the processing.
            # I forgot, however, that the bottleneck here is the compression.
            
            if False:
                
                for i in range(size):

                    if rank == i:

                        # Truncate file if exists else 'append'
                        open_opt = 'w' if i == 0 else 'r+'

                        # Open file
                        with h5py.File(f'{testdir}/parallel_test_{comp}_{chunk:d}_enc{_encoded:d}.h5', open_opt) as db:

                            # Write encoding parameters when encoding is enabled
                            if (open_opt == 'w') and (_encoded):
                                db.create_dataset("encoding", data=encoding_level)
                                db.create_dataset("offset", data=offset)
                                db.create_dataset("normal_factor", data=normal_factor)

                            if i == 0:
                                dset = db.create_dataset(
                                    'test', (3, roundup(Ntot, chunk), length), dtype=pprecision, chunks=(3, chunk, length),
                                    shuffle=True, compression=comp)

                            else:
                                dset = db['test']


                            print(flush=True)
                            print("rank", rank, "shape x", x.shape, flush=True)
                            print("rank", rank, "shape d", dset.shape, "Ntot", Ntot, flush=True)
                            print("rank", rank, "offset ", offsets[rank], offsets[rank+1], flush=True)
                            print("rank", rank, "loffset", offsets[-1])
                            # Write to the dataset.
                            dset[:, offsets[rank]:offsets[rank+1], :] = x

                    comm.Barrier()
                    
            else:

                if rank == 0:
                    print("Writing in Parallel", flush=True)
                    
                # Open file
                with h5py.File(f'{testdir}/parallel_test_{comp}_{chunk:d}_enc{_encoded:d}.h5', 'w', driver='mpio', comm=MPI.COMM_WORLD) as db:

                    # Write encoding parameters when encoding is enabled
                    if _encoded:
                        db.create_dataset("encoding", data=encoding_level)
                        db.create_dataset("offset", data=offset)
                        db.create_dataset("normal_factor", data=normal_factor)

                        
                        dset = db.create_dataset(
                            'test', (3, roundup(Ntot, chunk), length), dtype=precision, chunks=(3, chunk, length),
                            shuffle=True, compression=comp)
                        
                    else:
                        dset = db.create_dataset(
                            'test', (3, roundup(Ntot, chunk), length), dtype=pprecision, chunks=(3, chunk, length),
                            shuffle=True, compression=comp)

                    print(flush=True)
                    print("rank", rank, "shape x", x.shape, flush=True)
                    print("rank", rank, "shape d", dset.shape, "Ntot", Ntot, flush=True)
                    print("rank", rank, "offset ", offsets[rank], offsets[rank+1], flush=True)
                    print("rank", rank, "loffset", offsets[-1])

                    # Write to the dataset.
                    with dset.collective:
                        dset[:, offsets[rank]:offsets[rank+1], :] = x

            # TEST in Printed format whether wat we wrote is 'OK'.
            if rank == 0:

                print("="*50, flush=True)
                print("="*21 + " RESULT " + "="*21, flush=True)
                print("="*50, flush=True)
                print(flush=True)
                with h5py.File(f'{testdir}/parallel_test_{comp}_{chunk:d}_enc{_encoded:d}.h5', 'r') as db:

                    # recover waveform
                    xout = db['test'][0,offsets[rank]:offsets[rank+1],:]

                    # Recover encoding 
                    if _encoded:
                        encoding = db['encoding'][()]
                        offset = db['offset'][()]
                        normal_factor = db['normal_factor'][()]

                        
                        xout = xout / (2 ** encoding_level - 1) * normal_factor + offset


                    print("x:", flush=True)
                    print("-"*50, flush=True)
                    print(x_original[0, offsets[rank]:offsets[rank+1], :], flush=True)
                    print(flush=True)
                    print("x out:", flush=True)
                    print("-"*50, flush=True)
                    print(xout, flush=True)

                print(flush=True)
                print("="*50, flush=True)
                print("="*50, flush=True)
                print("="*50, flush=True)
                
            comm.Barrier()
