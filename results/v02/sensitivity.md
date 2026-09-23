# POST-HOC sensitivity of the Study 2 agency test (not pre-registered)

Blended predictor = (1 − w) × trained FULL agent + w × hand-built comparator (heat channels). Same T2 battery, 40 trials per condition, same pass rule (≥ 4 of 5 runs; FULL_seed4 fails the competence gate and never counts).

| w | H1 effect (mean of 5 runs) | H1 runs passing | H2 runs passing | H3a runs passing | Would H1 be declared supported? |
|---|---|---|---|---|---|
| 0.0 | -0.002 | 0/5 | 0/5 | 0/5 | no |
| 0.02 | +0.038 | 4/5 | 1/5 | 4/5 | yes |
| 0.05 | +0.097 | 4/5 | 1/5 | 4/5 | yes |
| 0.1 | +0.190 | 4/5 | 4/5 | 4/5 | yes |
| 0.25 | +0.441 | 4/5 | 4/5 | 4/5 | yes |
| 0.5 | +0.760 | 4/5 | 4/5 | 4/5 | yes |

**Smallest blend weight detected by the pre-registered rule:** 0.02.
**Equivalence bound from the actual data:** every FULL run's H1 95% CI lies below +0.016 (relative prediction error units).

![sensitivity](fig_sensitivity.png)

