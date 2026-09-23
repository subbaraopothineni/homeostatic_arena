# Pre-registration: functional self/world and self/other distinction (v0.2)

**Status:** written and committed to git *before* the environment extensions,
the learning agent, or any v0.2 experiment exist. The git commit timestamp of
this file is the registration date. Any later change to this file is a
deviation and is listed in the "Deviations" section at the end (never silently
edited).

## 1. Research question

Can an agent trained **only** on homeostatic drive reduction (no labels, no
reward for attributing causes) come to distinguish, in functional terms,

1. changes to **its own body** from changes in **the world**, and
2. world changes it **caused itself** from identical changes caused by
   **another agent** or occurring **spontaneously**?

And do the tests used to detect these abilities separate such an agent from
simple controls that could fake them?

**Scope of claims.** "Functional self-awareness" here means only the ability
above, measured by behaviour and by the agent's internal predictions. Nothing
in this study can show or rule out subjective experience; no such claim will
be made.

## 2. Theoretical basis

The comparator (forward-model) account of the sense of agency: the brain
predicts the sensory consequences of its own motor commands from an efference
copy, so self-generated consequences are predicted (attenuated), and a mismatch
signals an external cause (von Holst & Mittelstaedt, 1950; Blakemore, Wolpert &
Frith, 1998). Our operational test: **is a world change that follows from the
agent's own movement less surprising to the agent than the identical change
from another cause, and does that depend specifically on self-motion signals?**

## 3. Environment: the "agency world"

Extends the v0.1 arena (same body, physiology, physics). v0.1 scenarios and
results must remain unchanged (regression-tested).

| Element | Specification |
|---|---|
| Arena | 10 × 10 m, walls at ±5 m |
| Charger | centre (3, 3), radius 0.6 m |
| Switchable heat lamp | at the charger, (3, 3), peak 60 °C, σ = 0.7 m. When on, charging costs damage |
| Static hot spot | (−2, 2), peak 60 °C, σ = 0.7 m (always on) |
| Switch pad | centre (0, 0), radius 0.5 m. **Any robot whose centre enters the pad toggles the lamp** (on entry only) |
| Other robot | same disc body, scripted: walks at action magnitude 0.6 to waypoints; each waypoint is the pad centre with p = 0.5, else uniform in the arena. Not affected by heat |
| Spontaneous toggles | lamp toggles by itself, Poisson rate 1 / 20 s |
| Metabolic shocks | internal event: energy −0.1, Poisson rate 1 / 30 s |
| Episode | 60 s, random start (< 30 °C, ≥ 2 m from charger, off the pad), start energy U(0.4, 1.0), lamp initially on/off with p = 0.5 |

**Observation (26 values).** The 11 v0.1 channels, plus:

| # | Channel | Analogue |
|---|---|---|
| 11–12 | previous action | efference copy |
| 13 | previous reward × 20, clipped to [−1, 1] | previous consequence |
| 14–21 | thermal "vision": 8 world-frame sectors, each the max over active heat sources in that sector of ((peak − 25)/35)·exp(−distance/3) + N(0, 0.005) | distal heat sense (pit-organ-like) |
| 22 | on pad (0/1) | floor texture under the body |
| 23–25 | other robot: present, dx/5, dy/5 | seeing another agent |

**Ground truth (never observed by the agent).** Each step the environment logs
`self` state, `world` state and a list of `events`
(type, cause ∈ {self, other, spontaneous, manual, internal}, location,
body_affected).

## 4. Agents and controls

| Name | Description | Role |
|---|---|---|
| **FULL** | recurrent actor-critic (MLP encoder → GRU, 128 units) with a forward-model head that predicts the next observation from (GRU state, action). Trained with PPO on the v0.1 drive-reduction reward plus a self-supervised next-observation prediction loss | main agent |
| **NOEFF** | as FULL, but the efference-copy inputs are always zero (training and test) | ablation (training-time) |
| **NOFWD** | as FULL, but the prediction-loss weight is 0 | ablation: no learned predictions |
| **UNTRAINED** | FULL architecture, random initial weights | negative control |
| **NO-CHANGE** | predicts o(t+1) = o(t) | trivial predictor control |
| **COMPARATOR** | hand-coded: predicts a lamp toggle exactly when its own position + velocity × dt crosses into the pad | positive control (mechanism known to be present) |
| **POSITION RULE** | attributes a toggle to "self" if the agent is on the pad afterwards | shortcut control |
| **REFLEX** | v0.1 thermotactic reflex (reads the first 11 channels) | behavioural baseline |

**Training protocol (fixed in advance).** 3 million environment steps per run;
16 parallel environments; rollouts of 128 steps; γ = 0.99, GAE λ = 0.95;
Adam, learning rate 3·10⁻⁴; PPO clip 0.2; 4 epochs × 4 minibatches (by
environment); value coefficient 0.5; entropy coefficient 0.001; gradient-norm
clip 0.5; reward × 10; prediction-loss weight 1.0 (FULL, NOEFF). Seeds:
FULL 0–4, NOEFF 0–2, NOFWD 0–2, UNTRAINED 0–4. No hyperparameter tuning on any
test in §5. If throughput makes 3 M steps infeasible, the budget may be reduced
**once, before any test is run**, for all variants alike, and the change logged.

**Competence gate.** Before testing, each trained run is evaluated on 20
held-out free-running episodes. A run passes the gate if its forward model's
mean squared next-observation error is ≤ 0.8 × that of NO-CHANGE (FULL,
NOEFF). Survival is reported but not gated. Runs failing the gate are
reported, and they count as **not supporting** every hypothesis.

## 5. Tests

All test trials disable random events and drive both robots with scripted
(forced) actions, so the sensory situation is matched across conditions. The
agent's network runs normally: it receives the observations (including the
efference copy of the executed action), and we record its GRU state and
forward-model predictions. Each trial has a 1 s stationary warm-up. 40 trials
per condition per run: 20 with the lamp initially on and 20 with it off, with
start positions jittered ±0.1 m and sensor noise on.

### T2: agency (primary)

| Condition | Agent | Other robot | Lamp toggles because |
|---|---|---|---|
| SELF | from (−1, 0) moves east (action 0.8) **into** the pad | from (1, −0.9) moves west, passing south of the pad | the agent entered |
| OTHER | from (−1, 0.9) moves east, passing north of the pad | from (1, 0) moves west **into** the pad | the other robot entered |
| SPONT | passes north | passes south | manual toggle at the median SELF event time |
| NOEVENT | passes north | passes south | no toggle |
| SELF-OMIT | as SELF | as SELF | **switch disabled**: the agent enters but nothing happens |
| OTHER-ONPAD | stands on the pad at (−0.2, 0) | moves west into the pad | the other robot entered |
| SPONT-ONPAD | stands on the pad | passes south | manual toggle |

Test-time ablations (for SELF, OTHER, SPONT):
- **self-blind:** position, velocity, efference copy and on-pad channels are frozen at their values at the start of motion.
- **other-blind:** the other-robot channels are frozen the same way.

**Measures.**
- **Relative prediction error (relPE)** on the thermal channels at the step the
  lamp change first appears: relPE = ‖prediction − actual‖² / ‖previous − actual‖².
  0 = the change was fully predicted, ≈ 1 = no change was predicted.
- **Absolute PE** on the thermal channels (for omission).

### Hypotheses and pass rules

A hypothesis is **supported** if, in at least **4 of 5** FULL runs, the
within-run 95% bootstrap CI (2000 resamples over trials) of the effect excludes
0 in the predicted direction. All runs are reported whatever the outcome.

| ID | Hypothesis | Effect |
|---|---|---|
| **H1** | Self-caused changes are predicted | relPE(SPONT) − relPE(SELF) > 0 |
| **H2** | The agent expects its own action to have an effect | absPE(SELF-OMIT) − absPE(NOEVENT) > 0 |
| **H3a** | Self-prediction depends on self-motion signals | [relPE(SELF, self-blind) − relPE(SELF)] − [relPE(OTHER, self-blind) − relPE(OTHER)] > 0 |
| **H3b** | Other-prediction depends on seeing the other | [relPE(OTHER, other-blind) − relPE(OTHER)] − [relPE(SELF, other-blind) − relPE(SELF)] > 0 |

H3a and H3b together form the double dissociation: a separable "self" versus
"other" source of prediction. H3b is only interpretable if the agent predicts
OTHER at all (relPE(OTHER) < relPE(SPONT)); otherwise it is reported as not
applicable.

**Validity checks (the test is itself tested).**
- **V1.** UNTRAINED must **not** meet the H1–H3 pass rule (5 seeds). If it does, the test is declared fooled.
- **V2.** COMPARATOR must meet H1 and H2 (pipeline check).
- **V3.** POSITION RULE attribution accuracy on SELF vs OTHER-ONPAD vs SPONT-ONPAD is reported. It is expected to misattribute the ONPAD conditions, demonstrating that a position shortcut fails the dissociation trials.

**Secondary (direction predicted, not part of the pass rule).**
- relPE(OTHER) − relPE(SELF) > 0.
- The H1 effect in NOEFF and NOFWD runs. Expectation: NOFWD shows no H1 effect; NOEFF may still show it, because proprioception also carries self-motion.
- **Ecological check:** in 50 free-running episodes per FULL run, relPE of naturally occurring toggles by cause (self / other / spontaneous).

### T1: body vs world (descriptive; expected to be fooled)

The agent is held stationary at (−2.5, −2.5) and the other robot parked far
away. At 1.5 s one event happens:
- **WORLD:** manual lamp toggle; the lamp is far away, so there is no body effect.
- **BODY:** metabolic shock.
- **NONE:** nothing.

Measure: the share of prediction error on interoceptive channels (energy,
damage) versus exteroceptive channels (thermal sectors) at the event step, for
FULL, UNTRAINED and NO-CHANGE.

Behaviour: start energy 0.65; after the event the agent's own policy (or
REFLEX) controls it for 5 s; measure displacement toward the charger.

**Prediction:** trivial controls separate body from world events as well as
FULL does, because the events arrive on different sensor channels, and REFLEX
responds behaviourally to BODY because the shock crosses its 0.6 energy
threshold. T1 is included to document that body-vs-world tests of this kind
are passed by trivial mechanisms.

### Exploratory (clearly labelled as such in any report)

Linear probes (cross-validated logistic regression) on the GRU state,
decoding:
- event type ("what is happening");
- cause ("who did it");
- body_affected ("is it my body");
- the same labels 10 and 40 steps later ("what happened before").

Compared against UNTRAINED and against a probe on the last 5 raw
observations. Decoding success is **not** interpreted as evidence of
self-awareness unless it exceeds the raw-input probe.

## 6. What would count as a negative result

- H1 not supported: the agent does not predict the consequences of its own actions any better than spontaneous changes.
- H1 supported but H3a not: prediction is not specific to self-motion signals.
- V1 fails: the prediction-error test is fooled by untrained networks and cannot be used.

Negative results will be reported with the same prominence as positive ones.

## 7. What will not be claimed

- Subjective experience, feelings or consciousness of any agent.
- That passing these tests implies self-awareness in any sense beyond §1.
- Generalisation beyond this environment and these agents.

## Deviations

*(none yet)*

**Added after the analysis (2026-09-22). The text above is unchanged since registration.**

1. **Training length.** Each run trained for 2,998,272 environment steps (1,464 rollouts of 2,048 steps; integer division) instead of exactly 3,000,000. The budget was not otherwise changed.
2. **NOEFF implementation.** "Efference-copy inputs always zero" was implemented as zeroing both the previous-action observation channels and the forward model's current-action input.
3. **Ablation details.** Self-blind and other-blind freeze the listed observation channels at the last warm-up observation. The forward model's current-action input is not frozen, because it is not an observation channel.
4. **Exploratory probes.**
   - The "what" probe (T1 trials) uses lags 1 and 9, because T1 trials end 10 steps after the event.
   - No separate body_affected probe: in T1 it is identical to the event-type label.
   - No lag-40 probe for T1.
   - The probe's ridge penalty (10⁻³) was set on synthetic data before any real data were analysed.
5. **Descriptive attribution rule.** "Self" if relPE < 0.5 was added for reporting. It is not used in any verdict.
6. **Exploratory follow-up.** After the pre-registered results were known, two analyses were added to understand the negative result:
   - reafference on NOEVENT trials, with a self-blind and an other-blind control;
   - how often each cause toggled the lamp.

   They are reported separately in `results/v02/exploratory.md` and labelled exploratory everywhere.
