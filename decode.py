import os
import sys
import time
import numpy as np
import pymatching
from tqdm import tqdm
from circuit import surface_code_circuit
from beliefmatching import BeliefMatching
from Tools.fast_bm import Fast_BeliefMatching


if __name__ == "__main__":
    # code distance
    d = 5
    # physical error rate
    p_surface = 0.003
    # number of experiment shots
    n = 10000
    # number of syndrome measurement rounds for one shot
    num_layer = d
    
    print(f"syndrome measurement rounds: {num_layer}", flush=True)
    circuit = surface_code_circuit(d, num_layer, p_surface)
    sampler = circuit.compile_detector_sampler()
    detector_matrix, actual_observables = sampler.sample(shots=n, separate_observables=True)
    print(f"p_surface: {p_surface}")
    print(f"syndrome ratio: {np.sum(detector_matrix) / detector_matrix.size:.4f}")
    
    # get the detector error model (Decoding Graph)
    DEM = circuit.detector_error_model(decompose_errors=True)
    
    # ===================== Pymatching (MWPM) =====================
    print(f"### {'MWPM Decoding':^40} ###")
    MWPM = pymatching.Matching.from_detector_error_model(DEM)
    t1 = time.time()
    pred_pm = MWPM.decode_batch(detector_matrix)
    t2 = time.time()
    ler_pm = (pred_pm ^ actual_observables).sum() / n
    print(f"Logical Error Rate: {(pred_pm ^ actual_observables).sum()}/{n}")
    print(f"Time: {t2 - t1:.3f} s")

    # ===================== Correlated MWPM =====================
    print(f"### {'Correlated MWPM Decoding':^40} ###")
    MWPM_corr = pymatching.Matching.from_detector_error_model(DEM, enable_correlations=True)
    t1 = time.time()
    pred_corr = MWPM_corr.decode_batch(detector_matrix, enable_correlations=True)
    t2 = time.time()
    ler_corr = (pred_corr ^ actual_observables).sum() / n
    print(f"Logical Error Rate: {(pred_corr ^ actual_observables).sum()}/{n}")
    print(f"Time: {t2 - t1:.3f} s")

    # ===================== Belief Matching (Single) =====================
    print(f"### {'Belief Matching (single thread)':^40} ###")
    BM = BeliefMatching(DEM)
    t1 = time.time()
    pred_bm = BM.decode_batch(detector_matrix)
    t2 = time.time()
    ler_bm = (pred_bm ^ actual_observables).sum() / n
    print(f"Logical Error Rate: {(pred_bm ^ actual_observables).sum()}/{n}")
    print(f"Time: {t2 - t1:.3f} s")

    # ===================== Fast Belief Matching (Parallel) =====================
    print(f"### {'Fast Belief Matching (parallel)':^40} ###")

    t1 = time.time()
    pred_fast_bm = Fast_BeliefMatching(DEM=DEM, detector_matrix=detector_matrix)
    t2 = time.time()
    ler_fast_bm = (pred_fast_bm ^ actual_observables).sum() / n
    print(f"Logical Error Rate: {(pred_fast_bm ^ actual_observables).sum()}/{n}")
    print(f"Time: {t2 - t1:.3f} s")