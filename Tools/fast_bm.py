import numpy as np
from typing import Union
import stim
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
from beliefmatching import BeliefMatching

# Global BM instance (each process builds it once)
_BM = None

def _bm_init(dem):
    """Initialize BeliefMatching in each worker process."""
    global _BM
    _BM = BeliefMatching(dem)

def _bm_task(idx, chunk):
    """Decode a chunk of shots in a worker."""
    return idx, _BM.decode_batch(chunk)

def Fast_BeliefMatching(DEM: stim.DetectorErrorModel, 
                        detector_matrix: np.ndarray, 
                        num_threads: int = 8, 
                        chunk_size: int = None, 
                        verbose: bool = True) -> np.ndarray:
    """
    Parallel Belief Matching decoding using multiple processes.
    
    Args:
        DEM : stim.DetectorErrorModel or stim.Circuit
        detector_matrix : np.ndarray, shape (shots, num_detectors)
        num_threads : int, number of parallel processes
        chunk_size : int or None, number of shots per chunk
        verbose : bool, show progress bar if True
    
    Returns:
        np.ndarray : predicted observables, same shape as BM.decode_batch(detector_matrix)
    """
    shots = detector_matrix.shape[0]
    if shots == 0 or num_threads <= 1:
        return BeliefMatching(DEM).decode_batch(detector_matrix)

    # auto chunk size if not set
    if chunk_size is None:
        chunk_size = max(1, shots // num_threads)

    # split data into chunks
    slices = [slice(i, min(i + chunk_size, shots)) for i in range(0, shots, chunk_size)]
    results = [None] * len(slices)

    with ProcessPoolExecutor(max_workers=num_threads, initializer=_bm_init, initargs=(DEM,)) as pool:
        futures = [pool.submit(_bm_task, k, detector_matrix[slc]) for k, slc in enumerate(slices)]
        if verbose:
            futures = tqdm(as_completed(futures), total=len(futures), desc="Belief Matching")

        for fut in futures:
            k, pred = fut.result()
            results[k] = pred

    return np.concatenate(results, axis=0)