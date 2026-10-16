# Example: what a 30-minute run of loop-a looked like

Dry run by the organiser on 15 Oct 2026, headless, auto mode, stopped itself at minute 27.
Start 904.727 (grid), end 577.849 (lower bound 386.924). 10 tries, 8 kept, 2 reverted.
The solver and the submission of this run are not in the repository on purpose; the log is here
so you can see the rhythm: one change, one run, one line.

| # | time | hypothesis | change | total | best n improved | kept / reverted |
|---|------|------------|--------|-------|-----------------|-----------------|
| 0 | 1 | baseline grid solver as shipped | none | 904.727 | — | kept |
| 1 | 1 | greedy beats grid | layout = baseline.greedy_layout | 668.907 | all | kept |
| 2 | 2 | finer poses/lines help | ANGLE_STEP 15->10, K 8->12 | 668.905 | 100 | kept |
| 3 | 4 | reinsert boundary hats shrinks square | ruin-and-reinsert post-pass | 668.905 | none (equal) | reverted |
| 4 | 7 | annealing single-hat moves compacts small n | refine(n<=12) post-pass | 644.433 | 10 | kept |
| 5 | 11 | refine all n beats finer greedy | ANGLE_STEP back to 15, refine every group, weighted slices | 594.981 | 50 | kept |
| 6 | 15 | Metropolis everywhere escapes minima | temp=0.02*side*frac^2 all n | 617.913 | 1-3 better, mid/large much worse | reverted |
| 7 | 18 | anneal only where stuck | Metropolis for n<=4, greedy accept elsewhere, normalize box | 587.653 | 2 | kept |
| 8 | 21 | random restarts unstick tiny n | 3 anneal restarts + flip moves for n=2..4 | 580.744 | 4 | kept |
| 9 | 26 | warm start makes runs monotone | seed layouts from previous submission.csv, keep better per n | 577.849 | 24 | kept |
| — | 27 | final: submission.csv valid, TOTAL 577.849 (tries 0-9, kept 0,1,2,4,5,7,8,9) | — | 577.849 | — | kept |
