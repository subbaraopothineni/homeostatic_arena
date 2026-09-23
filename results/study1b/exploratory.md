# EXPLORATORY: Study 1b policy check (not pre-registered)

Is the learned agents' near-immobility an artefact of evaluating the mean action? 20 foraging-world episodes per seed and policy.

| seed | policy | survived 90 s | time on charger (s) | mean speed (m/s) | lifetime (s) | policy std |
|---|---|---|---|---|---|---|
| 0 | deterministic | 0.00 | 0.0 | 0.11 | 79.3 | 0.09 |
| 0 | stochastic | 0.00 | 0.0 | 0.11 | 78.3 | 0.09 |
| 1 | deterministic | 0.00 | 0.0 | 0.11 | 79.1 | 0.09 |
| 1 | stochastic | 0.00 | 0.0 | 0.11 | 78.0 | 0.09 |
| 2 | deterministic | 0.00 | 0.0 | 0.14 | 79.9 | 0.10 |
| 2 | stochastic | 0.00 | 0.0 | 0.15 | 78.7 | 0.10 |
| 3 | deterministic | 0.00 | 0.0 | 0.20 | 81.0 | 0.10 |
| 3 | stochastic | 0.00 | 0.0 | 0.21 | 79.8 | 0.10 |
| 4 | deterministic | 0.00 | 0.0 | 0.10 | 73.7 | 0.10 |
| 4 | stochastic | 0.00 | 0.0 | 0.10 | 72.7 | 0.10 |

Both policies give the same picture, so it is not an artefact of evaluating the mean action. The trajectories (`trajectories_foraging.png`) show the agents walking *away* from the charger to the far (south / south-west) wall and staying pressed against it until their energy runs out; the low mean speed (0.1–0.2 m/s, versus 1.6 m/s for a reflex) reflects that parking. They never reach the charger. The policy's exploration noise had shrunk to ~0.1: training converged to this local optimum instead of foraging.

