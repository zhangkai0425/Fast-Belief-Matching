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
d: 5, p_surface: 0.003, syndrome measurement rounds: 5
syndrome ratio: 0.0500
###              MWPM Decoding               ###
Logical Error Rate: 70/10000
Time: 0.034 s
###         Correlated MWPM Decoding         ###
Logical Error Rate: 43/10000
Time: 0.095 s
###     Belief Matching (single thread)      ###
Logical Error Rate: 42/10000
Time: 38.839 s
###     Fast Belief Matching (parallel)      ###
Belief Matching: 100%|███████████████| 8/8 [00:06<00:00,  1.20it/s]
Logical Error Rate: 42/10000
Time: 6.723 s
```
