# POST-HOC: sensitivity to an imprecise self-prediction (not pre-registered)

Blended predictor = (1 − w) × trained FULL agent + w × comparator with a per-trial pad-edge error ~ N(0, σ) and gain error ~ lognormal(0, 0.3). Runs meeting each hypothesis (CI excludes 0; gated-out FULL seed 4 never counts; pass rule ≥ 4 of 5). In brackets: H1 runs with CI > 0 ignoring the gate.

| Self-model precision | w = 0.02 | w = 0.05 | w = 0.1 | w = 0.25 | w = 0.5 | w = 1 |
|---|---|---|---|---|---|---|
| exact | H1 4/5 (5), H2 1/5, H3a 4/5; effect +0.038 | H1 4/5 (5), H2 1/5, H3a 4/5; effect +0.097 | H1 4/5 (5), H2 4/5, H3a 4/5; effect +0.190 | H1 4/5 (5), H2 4/5, H3a 4/5; effect +0.441 | H1 4/5 (5), H2 4/5, H3a 4/5; effect +0.760 | H1 4/5 (5), H2 4/5, H3a 4/5; effect +1.026 |
| edge error 0.05 m | H1 2/5 (3), H2 0/5, H3a 4/5; effect +0.017 | H1 4/5 (5), H2 1/5, H3a 4/5; effect +0.045 | H1 4/5 (5), H2 3/5, H3a 4/5; effect +0.090 | H1 4/5 (5), H2 4/5, H3a 4/5; effect +0.206 | H1 4/5 (5), H2 4/5, H3a 4/5; effect +0.343 | H1 4/5 (5), H2 4/5, H3a 4/5; effect +0.407 |
| edge error 0.1 m | H1 1/5 (2), H2 0/5, H3a 3/5; effect +0.009 | H1 3/5 (4), H2 0/5, H3a 4/5; effect +0.025 | H1 4/5 (5), H2 1/5, H3a 4/5; effect +0.050 | H1 4/5 (5), H2 4/5, H3a 4/5; effect +0.116 | H1 4/5 (5), H2 4/5, H3a 4/5; effect +0.194 | H1 4/5 (5), H2 4/5, H3a 3/5; effect +0.228 |
| edge error 0.2 m | H1 0/5 (0), H2 0/5, H3a 1/5; effect +0.005 | H1 1/5 (2), H2 0/5, H3a 2/5; effect +0.014 | H1 3/5 (4), H2 1/5, H3a 3/5; effect +0.028 | H1 4/5 (5), H2 1/5, H3a 2/5; effect +0.067 | H1 4/5 (5), H2 3/5, H3a 2/5; effect +0.112 | H1 4/5 (5), H2 4/5, H3a 0/5; effect +0.133 |
