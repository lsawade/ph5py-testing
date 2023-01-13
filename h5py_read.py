import numpy as np

import h5py

# Test all compression styles
for comp in [None, 'gzip', 'lzf']:

    
    if comp is None:
        label = 'nocomp'
    else:
        label = comp

    print("Compression:", label)
    
    with h5py.File(f'parallel_test_{comp}.h5', 'r') as db:

        print(db['test'][:])

