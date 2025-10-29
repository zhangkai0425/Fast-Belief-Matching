# Fast-Belief-Matching

Parallel Belief Matching For QEC Evaluation

This simple repository provides a **simple, robust, multi-process parallel** wrapper that significantly accelerates Belief Matching decoding without modifying the original **`beliefmatching`** package. (Just because the original code is too slow for QEC evaluation, such as surface code decoding with large code distance and multiple syndrome measurement rounds)

Check the source code:

```bash
cd Fast-Belief-Matching/Tools
cat fast_bm.py
```

Run a simple demo for surface code decoding:

```bash
cd Fast-Belief-Matching
python decode.py
```

The result should be as follows:

```bash
syndrome measurement rounds: 5
p_surface: 0.003
syndrome ratio: 0.0498
###              MWPM Decoding               ###
Logical Error Rate: 74/10000
Time: 0.030 s
###         Correlated MWPM Decoding         ###
Logical Error Rate: 40/10000
Time: 0.086 s
###     Belief Matching (single thread)      ###
Logical Error Rate: 36/10000
Time: 40.079 s
###     Fast Belief Matching (parallel)      ###
Belief Matching: 100%|████████████████████████████████████████████████████████████████████████████████████████████| 8/8 [00:06<00:00,  1.24it/s]
Logical Error Rate: 36/10000
Time: 6.588 s
```
