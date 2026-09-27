# Pre-registration: Study 2b (necessary agency) and Study 1b (learning agent on the sentience markers)

**Status:** committed to git *before* any Study 2b or Study 1b model is trained
or evaluated. Later changes go only into "Deviations" at the end.

---

## Part A: Study 2b, the same agency test in a world where the agent's own action is necessary

### A1. Rationale

Study 2 (`docs/preregistration_v0.2.md`) found no self-prediction: 0/5 runs
passed H1–H3a, while the validity checks passed. Exploratory analysis showed
that the agents almost never used the switch (26 self-caused toggles vs 2,016
others in 250 episodes). They waited for the other robot or chance to turn the
lamp off.

A design check with scripted robots (`experiments/necessity_check.py`,
100 episodes each) confirms that in the Study 2 world waiting was as good as
switching:

| World | WAITER survival | SWITCHER survival | SWITCHER − WAITER |
|---|---|---|---|
| Study 2 (other robot visits pad p = 0.5; spontaneous toggles 1/20 s; start energy 0.4–1.0; lamp on at start p = 0.5) | 0.99 | 0.95 | −0.04 [−0.09, +0.01] |
| **Study 2b** (p = 0.05; 1/120 s; start energy 0.2–0.6; lamp on at start p = 1) | 0.74 (all 26 deaths from energy) | 0.99 | **+0.25 [+0.17, +0.34]** |

The Study 2b SWITCHER toggles the lamp itself 2.9 times per episode.

**Question.** When the agent's own action is necessary for survival, does the
learning agent come to predict the consequences of its own actions (H1–H3)?

### A2. What changes, and what does not

- **World `agency_b`** (`arena/agency.py`). Identical to Study 2 except for four settings:
  - the other robot's probability of choosing the pad as a waypoint: 0.5 → **0.05**;
  - the spontaneous lamp-toggle rate: 1/20 s → **1/120 s**;
  - the start energy: U(0.4, 1.0) → **U(0.2, 0.6)**;
  - the lamp is **always on** at episode start.
- **Unchanged:**
  - agents, variants and seeds: FULL 0–4, NOEFF 0–2, NOFWD 0–2, UNTRAINED 0–4 (the same random networks as in Study 2);
  - controls: NO-CHANGE, COMPARATOR, POSITION RULE, REFLEX;
  - the training protocol: 1,464 PPO updates of 2,048 steps = 2,998,272 steps, same hyperparameters;
  - the tests T2 and T1, the probes, the competence gate, the ecological check and all pass rules.

  The scripted test trials set every world setting explicitly (random events off, positions, energy and lamp state fixed), so they are identical to Study 2. Free-running episodes (gate, ecological check) use `agency_b`.
- **Commands:**
  - `WORLD=agency_b OUT=results/v02b/models bash experiments/train_all.sh`
  - `python -m experiments.run_v02 --models results/v02b/models --out results/v02b --world agency_b`

### A3. Hypotheses and pass rule (unchanged from Study 2)

- **H1:** relPE(SPONT) − relPE(SELF) > 0.
- **H2:** absPE(SELF-OMIT) − absPE(NOEVENT) > 0.
- **H3a/H3b:** the double dissociation.

A hypothesis is supported if the within-run 95% bootstrap CI excludes 0 in the
predicted direction in ≥ 4 of 5 FULL runs that pass the competence gate.
Validity checks V1–V3 as before.

### A4. New manipulation check (reported; does not change how H1–H3 are evaluated)

**M1.** In the 50 free-running ecological episodes, each FULL run toggles the
lamp itself at least 1.0 times per episode on average. If fewer than 4 of 5
runs meet M1, the manipulation is reported as failed. H1–H3 are still
evaluated and reported.

### A5. Planned follow-ups

- The post-hoc sensitivity analysis of Study 2 (`experiments/sensitivity_v02.py`) is repeated on the Study 2b agents.
- The exploratory analyses (reafference, event counts, learned strategy) are repeated and labelled exploratory.

---

## Part B: Study 1b, a learning agent on the Study 1 sentience markers

### B1. Rationale

Study 1 tested only memoryless reflexes and a random agent. Showing that a
marker *discriminates* architectures requires an agent that could pass where
the reflexes fail.

### B2. Agent and training

- The FULL architecture (GRU actor-critic with a forward model), using the 11-channel v0.1 observation.
- Trained in `Study1Arena` (`arena/study1.py`):
  - each episode is the v0.1 foraging world or the v0.1 trade-off world with probability 0.5;
  - the trade-off start energy is U(0.05, 1.0).
- Reward: v0.1 drive reduction only.
- 2,998,272 steps, seeds 0–4, the same hyperparameters as Study 2.
- Command: `WORLD=study1 OUT=results/study1b/models RUNS="FULL:0 FULL:1 FULL:2 FULL:3 FULL:4" bash experiments/train_all.sh`.

### B3. Evaluation

The unchanged v0.1 marker battery, with a deterministic policy (mean action):

```
python -m experiments.run_baseline --seeds 30 --agents --learned results/study1b/models --out results/study1b
python -m experiments.run_baseline --seeds 100 --agents --learned results/study1b/models --out results/study1b/seeds100
```

Learned agents are compared with the existing Study 1 baseline results (same
episode seeds). Each learned seed is reported separately.

### B4. Questions and decision rules

| ID | Question | Decision rule |
|---|---|---|
| Q1 | Does the **trade-off** marker separate the learning agent from the reflexes (which scored 0)? | "Separates" if the trade-off score (crossing rate at start energy 0.08 minus at 0.9) is > 0 with a 95% CI excluding 0 in ≥ 4 of 5 learned seeds (30 seeds) |
| Q2 | **Anticipatory avoidance** | Descriptive only. A reflex already scores 1.00, so no result can make this marker discriminative |
| Q3 | Does **sensitization** separate learning from memoryless agents? | Using the 100-seed run: "separates" if the learned agent's `sensitization_c` upper CI bound is below the lower CI bound of *both* memoryless agents (random +7.16, nociceptive reflex +6.14) in ≥ 4 of 5 learned seeds, **and** `sensitization_nonharmful_c` < 0 with a CI excluding 0 in ≥ 4 of 5 seeds. With too few qualifying episodes (CI not computable) the answer is "not estimable" |
| Q4 | Survival | Descriptive |

No claim about subjective experience will be made from any outcome.

---

## Deviations

*(none yet)*

**Added after the analysis (2026-09-23). The text above is unchanged since registration.**

1. **Execution.** Training, the evaluation battery and the decision rules ran as registered. The commit message of the registration commit was corrected once, before any training; the content was not.
2. **Tooling fixes that do not change numbers.**
   - `run_v02` did not write `meta.json`. It was written by hand for Study 2 and Study 2b (event timing step 32, as printed in each report), and the code now writes it.
   - The report header now names the right pre-registration and shows M1.
   - The sensitivity table gained an "ignoring the gate" column.
3. **Exploratory additions, labelled as such everywhere.** All were added after results were known:
   - the Study 2b strategy analysis;
   - the reafference check;
   - for Study 1b, a comparison of deterministic and stochastic policies on the foraging world (`results/study1b/exploratory.md`).

**Added 2026-09-26 (post-hoc analyses, not part of the registration; no verdict changes).**

4. **Minimal controls for the Study 1 markers.** Two control agents were added after all results were known: a motivational reflex (withdrawal vetoed while energy < 0.2) and a sensitizing reflex (one bit of state set by harm) (`agents/minimal.py`, `results/minimal_controls/`). A decision-time analysis of the trade-off was also added (`experiments/tradeoff_decision.py`).
5. **Heat-channel competence** was computed for the Study 2b runs as well (`results/thermal_competence/`).
