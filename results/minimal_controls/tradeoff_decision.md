# POST-HOC: trade-off measured at the moment of decision

Trade-off world, start energies (0.08, 0.3, 0.5, 0.9), 100 seeds each. One observation per approach to the wall from the start side; energy is the agent's energy when the approach began. Slope: logistic regression of crossing on energy (negative = crosses when in need), 95% CI from a bootstrap over episodes.

| Agent | Approaches | Crossed | P(cross), energy < 0.25 | 0.25–0.5 | ≥ 0.5 | Logistic slope [95% CI] |
|---|---|---|---|---|---|---|
| random | 302 | 140 | 0.43 (57/133) | 0.49 (43/87) | 0.49 (40/82) | +0.5 [-0.3, +1.4] |
| reflex_nociceptive | 790 | 0 | 0.00 (0/356) | 0.00 (0/277) | 0.00 (0/157) | no crossings |
| reflex_thermotactic | 1195 | 0 | 0.00 (0/660) | 0.00 (0/376) | 0.00 (0/159) | no crossings |
| reflex_motivational | 967 | 231 | 0.56 (231/414) | 0.00 (0/384) | 0.00 (0/169) | -20.8 [-25.8, -17.4] |
| reflex_sensitizing | 1187 | 0 | 0.00 (0/663) | 0.00 (0/364) | 0.00 (0/160) | no crossings |
