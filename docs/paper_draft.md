# DRAFT: Which behavioural markers of sentience and self-awareness can a simple mechanism fake? Controlled and pre-registered studies with homeostatic agents

*Working draft generated alongside the code. Author list, affiliations,
funding and acknowledgements to be completed by the authors. All numbers are
taken from the result files named in brackets; do not edit numbers by hand.*

## Abstract

Behavioural markers are increasingly proposed as evidence of sentience or
self-awareness in non-human systems, including AI. A marker is only
informative if simpler mechanisms cannot produce it. We tested this in a
physics-simulated homeostatic agent whose only learning signal is internal
drive reduction.

**Study 1.** We applied four animal-sentience markers (survival, anticipatory
avoidance, motivational trade-off, sensitization) to hard-wired reflex agents
with no memory or learning. A one-step thermotactic reflex passed
anticipatory avoidance perfectly, so that marker does not discriminate a
reflex from more complex architectures. No reflex passed the trade-off or
sensitization markers. We also show that the sensitization metric, as usually
defined, carries a large built-in bias.

**Study 2 (pre-registered).** We asked whether a recurrent agent that learns
to predict its own observations comes to predict the consequences of its own
actions better than identical consequences caused by another agent or by
chance (the comparator account of agency). We tested the specificity of this
with a double dissociation (freezing self-motion versus other-agent signals),
and against untrained, no-change and hand-built comparator controls.

The test was valid:
- a hand-built comparator passed;
- random networks did not;
- a position shortcut failed the dissociation trials.

A post-hoc sensitivity analysis showed that it detects an agent anticipating
just 2% of a self-caused change.

However, none of five trained agents passed any pre-registered hypothesis.
Their forward models did not predict the lamp changes at all, whatever the
cause (less than about 1% anticipation). The agents had learned to wait for
others to switch the lamp rather than act themselves.

**Study 2b (pre-registered)** repeated the test in a world where, by a
scripted design check, the agent's own action was necessary. The learning
agents mostly failed to discover the action (the manipulation check failed),
and again no hypothesis was supported.

**Study 1b (pre-registered)** gave learning agents the Study 1 markers. They
converged to walking away from the charger and waiting at a wall until they
starved, so they passed no marker that the reflexes failed.

Across studies, the tests pre-registered as vulnerable were passed by trivial
controls:
- body versus world, by a no-change predictor;
- "who caused it" decoded at ceiling, from untrained networks and raw inputs.

We conclude that behavioural and decoding markers of sentience and
self-awareness must be benchmarked against minimal mechanisms. A
prediction-based self/other test can be made valid and sensitive. And in our
hands, generic homeostatic learning agents were the limiting factor: they did
not acquire, or even gather the experience for, the capacity the test
measures.

## 1. Introduction (outline)

- Marker-based approaches to sentience in animals: Sneddon et al. 2014; Birch et al. 2021. Their extension to AI: Butlin, Long et al. 2023; Birch 2024.
- The shortcut ("gaming") problem: a system can produce a marker without the capacity the marker is meant to indicate. Unlike animals, artificial agents let us (a) build minimal mechanisms that could produce each marker and (b) inspect and ablate internal mechanisms.
- Homeostatic agents as a principled test bed: reward defined only as drive reduction (Keramati & Gutkin 2014), with no task reward; feeling-machine proposals (Man & Damasio 2019); related homeostatic RL (Yoshida et al. 2024a, b); Solms et al. 2026.
- Contribution:
  1. an open, physics-based test bed with functional analogues of nociception, damage, energy and drive;
  2. evidence that one widely used sentience marker is passed by a memoryless reflex;
  3. a pre-registered test of functional self/other distinction, with explicit validity controls for the test itself.

## 2. Methods

### 2.1 Body, physiology and environment (both studies)

A disc-shaped body (radius 0.25 m, mass 1 kg) moves on two damped slide joints
in a 10 × 10 m MuJoCo arena (Todorov et al. 2012; control step 0.05 s,
terminal speed 2 m/s). The physiology is a set of functional analogues:
- Ambient temperature is the room temperature (25 °C) plus the largest Gaussian rise from any heat source.
- Skin temperature follows ambient with a 0.3 s time constant.
- A logistic nociceptor signal is half-maximal at 45 °C (cf. TRPV1; Caterina et al. 1997).
- Damage accrues at 0.06 per °C above 45 °C per second and heals at 0.002/s; death at 1.
- Energy drains at 0.012/s plus 0.010/s × Σaction², and recharges at 0.25/s on a charger; death at 0.
- The homeostatic drive is √((1 − energy)² + 2·damage²). The only reward is its step-to-step decrease, with −1 on death.

Observations include proprioception, ambient and skin temperature,
nociceptor, a chemical-gradient-like beacon to the charger, touch, energy and
damage. Details: `README.md`, `arena/`.

### 2.2 Study 1: sentience markers versus reflex controls

**Agents.**
- A random walker.
- Two memoryless reflex agents:
  - *nociceptive*: withdraws when the nociceptor exceeds 0.1;
  - *thermotactic*: also withdraws when ambient temperature is above 35 °C and rising (cf. Wittenburg & Baumeister 1999).

  Both run-and-tumble on the beacon when energy is below 0.6 (Berg & Brown 1972).

**Markers.**
1. **Survival** in a 90 s foraging world.
2. **Anticipatory avoidance:** the fraction of heat encounters (ambient > 38 °C, hysteresis to 35 °C) left before the nociceptor exceeded 0.5.
3. **Motivational trade-off:** full crossings of a heat wall at start energies 0.08–0.9, on the way to a charger that can also be reached by a longer detour (after Elwood & Appel 2009). The world's design was verified analytically and in simulation before use (§ 4.1).
4. **Sensitization:** encounter peak temperature after versus before the first harmful encounter.

**Statistics.** 30 seeds per condition, plus a 100-seed robustness run.
Proportions use Wilson intervals; means use percentile bootstrap intervals
over episodes.

### 2.3 Study 2: functional self/other distinction (pre-registered)

The hypotheses, controls, pass rules and training budget were committed to
the repository (`docs/preregistration_v0.2.md`, commit `d70a2fe`) before any
Study 2 code or data existed.

**Agency world.** The Study 1 arena is extended with:
- a switchable heat lamp at the charger;
- a switch pad that toggles the lamp whenever any robot's centre enters it;
- a second, scripted robot;
- spontaneous lamp toggles (Poisson, 1/20 s);
- internal metabolic shocks (energy −0.1, 1/30 s).

The agent additionally senses:
- its previous motor command (efference copy);
- its previous reward;
- an 8-sector distal heat sense;
- a floor sense for the pad;
- the other robot's relative position.

**Learning agent (FULL).** An MLP encoder feeds a GRU (128 units), which feeds
a Gaussian policy and a value head. A forward-model head predicts the next
observation from the GRU state and the motor command. Training: PPO
(Schulman et al. 2017) on the drive-reduction reward, plus a self-supervised
next-observation prediction loss; 3 × 10⁶ steps, 5 seeds. The agent never
receives labels about what caused an event.

**Variants and controls.**
- NOEFF: no efference copy, 3 seeds.
- NOFWD: no prediction loss, 3 seeds.
- UNTRAINED: random weights, 5 seeds.
- NO-CHANGE: predicts that nothing changes.
- COMPARATOR: hand-built. It predicts a lamp toggle exactly when its own dynamics carry it into the pad; this is the positive control.
- POSITION RULE: attributes a change to itself if it is on the pad.
- The Study 1 thermotactic reflex, as a behavioural baseline.

**Test T2 (agency).** Scripted trials (40 per condition per run) present the
same lamp change with different causes and matched motion of both robots:
- SELF: the agent enters the pad;
- OTHER: the other robot enters the pad;
- SPONT: a spontaneous toggle;
- NOEVENT: no toggle;
- SELF-OMIT: the agent enters but the switch is disabled;
- OTHER-ONPAD and SPONT-ONPAD: the agent already stands on the pad.

The measure is the relative prediction error (relPE) of the agent's forward
model on the distal heat channels at the change. Test-time ablations freeze
either the self-motion channels (self-blind) or the other-robot channels
(other-blind).

**Hypotheses.**
- **H1:** relPE(SPONT) > relPE(SELF).
- **H2:** omission surprise, absPE(SELF-OMIT) > absPE(NOEVENT).
- **H3a/b:** a double dissociation. Self-blinding raises relPE for SELF more than for OTHER; other-blinding does the reverse.

A hypothesis is supported if the within-run 95% bootstrap CI excludes 0 in the
predicted direction in ≥ 4 of 5 FULL runs, each of which must first pass a
forward-model competence gate.

**Validity checks.**
- V1: UNTRAINED must not pass.
- V2: COMPARATOR must pass H1 and H2.
- V3: the POSITION RULE's attribution accuracy on the dissociation trials.

**Test T1 (body versus world)** is descriptive and pre-registered as expected
to be passed by trivial controls. **Exploratory probes** decode the cause
and the event type from the GRU state, and are compared with a raw-input
baseline.

### 2.4 Study 2b: necessary agency (pre-registered, `docs/preregistration_v0.2b.md`, Part A)

**Design check first.** Scripted robots with privileged knowledge compared a
WAITER (waits for the lamp to go off) with a SWITCHER (switches it off
itself), 100 episodes each (`experiments/necessity_check.py`).
- In the Study 2 world, switching gave no survival benefit: −0.04 [−0.09, +0.01].
- World `agency_b` changes four settings:
  - the other robot's pad visits: p 0.5 → 0.05;
  - spontaneous toggles: 1/20 s → 1/120 s;
  - start energy: 0.2–0.6;
  - the lamp is always on at start.

  There, switching gave +0.25 [+0.17, +0.34].

**Everything else was identical to Study 2:** agents, seeds, training budget,
test battery and pass rules. A manipulation check (M1) required the agents to
toggle the lamp themselves at least once per free-running episode.

### 2.5 Study 1b: a learning agent on the Study 1 markers (pre-registered, Part B)

- **Agent:** the FULL architecture with the 11-channel Study 1 observation.
- **Training world:** each episode is the foraging world or the trade-off world (start energy U(0.05, 1)).
- **Training:** 3 × 10⁶ steps, five seeds.
- **Evaluation:** the unchanged Study 1 marker battery (30 and 100 seeds), using the deterministic policy.
- **Decision rules:**
  - Q1: the trade-off score > 0 in ≥ 4/5 seeds;
  - Q3: sensitization below the memoryless agents' CI floor, and the non-harmful variant < 0, in ≥ 4/5 seeds.

## 3. Results

### 3.1 Study 1 [`results/summary.csv`, `results/seeds100/summary.csv`]

- **Anticipatory avoidance is passed by a memoryless reflex.** The thermotactic reflex left 71/71 heat encounters before nociceptor activation (rate 1.00 [1.00, 1.00]; zero cumulative damage), whereas the nociceptive reflex scored 0.25 [0.15, 0.36], no better than random (0.34 [0.20, 0.49]).
- **No baseline agent passed the trade-off marker.** Neither reflex crossed the heat wall at any start energy. The random agent's significantly *negative* score (−0.47 [−0.67, −0.27]) is an opportunity artefact: at low energy it dies before reaching the wall.
- **Sensitization has a built-in positive bias.** Memoryless agents scored +9.95 °C [7.16, 12.87] (random) and +8.77 °C [6.14, 11.43] (nociceptive reflex) at 100 seeds, because all "before" encounters are non-harmful by construction. A like-for-like variant was ≈ 0.
- **Survival separates competent from random agents,** not reflex from learner (reflexes 0.70–0.83 vs random 0.23).

### 3.2 Study 2 [`results/v02/report.md`, `results/v02/*.csv`]

**Training.**
- All trained runs completed 2,998,272 steps.
- Four of five FULL runs learned to survive: 40–90% of held-out 60 s episodes survived, against 15% for FULL seed 4.
- Four FULL runs passed the competence gate: prediction error 0.47–0.69 × no-change. FULL seed 4 (1.18) and all NOEFF runs (1.63–1.98) failed it (Fig. training).

**Pre-registered hypotheses.** None was supported (Table 1; Fig. hypotheses):
- H1 (self-prediction): 0/5 FULL runs. Effects ranged from −0.004 to 0.001, and every CI included 0.
- H2 (omission surprise): 0/5.
- H3a (self-blind specificity): 0/5.
- H3b: not applicable in 4/5 runs, because relPE(OTHER) did not fall below relPE(SPONT).

At the lamp change, the FULL agents' relative prediction error was ≈ 1 in
every condition (SELF 0.996, OTHER 0.994, SPONT 0.994, OTHER-ONPAD 1.002,
SPONT-ONPAD 1.001). The forward models therefore did not predict lamp changes
at all, rather than predicting all causes equally well (Fig. relPE).

**Validity checks.**
- **V1 passed:** UNTRAINED met no hypothesis in ≥ 4/5 runs.
- **V2 passed:** COMPARATOR relPE was 0.004 for SELF vs 1.030 for SPONT; H1 effect 1.026 [1.011, 1.040]; self-blinding raised relPE(SELF) to 0.924.
- **V3:** the POSITION RULE attributed 100% of OTHER-ONPAD and SPONT-ONPAD changes to itself.

Random networks produced "significant" single-run effects in 3 of 15
hypothesis tests. This shows the need for the multi-run pass rule.

**Why no self-prediction?** The ecological check indicates that self-caused
lamp changes were almost absent from the agents' experience. In 250
free-running episodes the agents entered the pad 26 times, against 1,378
entries by the other robot and 638 spontaneous toggles. With lamp changes
under 1% of time steps, a next-observation loss averaged over all channels
provides little pressure to model them.

**Tests expected to be fooled (T1, probes).**
- **Body vs world.** The share of prediction error on body channels after an internal shock was 0.96 for NO-CHANGE and 0.86 for FULL (0.00–0.08 for world events). Dedicated channels make the distinction trivial.
- **FULL behaviour after the events** did not differ by condition (+4.97 to +4.99 m toward the charger).
- **Probes.** Linear probes decoded "who caused the lamp change" at 100% at lags 1–40 steps from FULL, UNTRAINED and raw-input features alike. Event type ("what") was decoded at 0.59–0.74 by all three (chance 0.33). Decodability therefore gave no evidence beyond the raw input.

**Exploratory (not pre-registered).**
- **Setting:** thermal predictions while walking with no lamp change.
- **Self-blinding** increased FULL prediction error in 4/5 runs, e.g. 1.66 → 2.50 × no-change.
- **Other-blinding control:** no effect (1.66 → 1.66).
- **Absolute accuracy:** prediction error stayed above the no-change error (ratio 1.47–3.11).
- **Reading:** the agents' distal predictions depend specifically on self-motion signals, without being accurate. This is hypothesis-generating only (`results/v02/exploratory.md`).

### 3.3 Sensitivity of the agency test (post-hoc) [`results/v02/sensitivity.md`]

We blended each agent's heat predictions with a fraction *w* of the
comparator's and re-ran the identical battery.

| Blend weight *w* | H1 runs passing | H3a runs passing | H2 runs passing |
|---|---|---|---|
| 0.02 | 4/5 | 4/5 | 1/5 |
| 0.10 and more | 4/5 | 4/5 | 4/5 |

The real agents' H1 CIs all lay below +0.016, so they anticipated less than
about 1% of self-caused changes. The Study 2 null is therefore evidence of
absence at this resolution.

### 3.4 Study 2b [`results/v02b/report.md`, `results/v02b/exploratory.md`]

- **Hypotheses:** H1–H3 were supported in 0/5 FULL runs each. V1–V3 passed.
- **Competence gate:** all five FULL runs failed it (prediction error 0.99–1.35 × no-change).
- **Survival:** 0, 0, 55, 50 and 0% of held-out episodes.
- **M1 failed:** self-caused toggles per episode were 0.00, 0.04, 0.22, 0.90 and 0.04.
- **Learned behaviour:**
  - Three agents never learned to charge and died in all 20 strategy episodes.
  - Two agents charged only with the lamp off (95–96%); only one regularly used the switch.
- **Sensitivity:** ignoring the gate, the test detected a 2% blend in 5/5 runs, and the agents' H1 CIs lay below +0.033.
- **Exploratory:** the Study 2 self-motion hint did not replicate consistently.

### 3.5 Study 1b [`results/study1b/report.md`, `results/study1b/exploratory.md`]

- **Q1: not separated.** The trade-off score was 0 in 5/5 seeds; the learners never crossed the heat wall and never reached the charger in the trade-off world.
- **Q3: not estimable.** The learners were almost never harmed (harm in 7–10% of episodes; no episode with encounters before and after harm).
- **Q2:** anticipation rates were 0.00–0.60, from 2–5 encounters.
- **Survival:** 0%; the learners never reached the charger.

**Why.** Trajectories show the learners walking away from the charger to the
far wall and waiting there until they starved (lifetime 74–81 s of 90).
Their exploration noise had shrunk to about 0.1, and the stochastic training
policy behaved the same (exploratory).

## 4. Additional methodological findings

### 4.1 Test worlds must be verified, not assumed

The trade-off world, as first specified, did not pose a trade-off:
- **Crossing the heat wall cost only 0.007 damage at top speed.**
- **The "impossible" detour was survivable at the lowest start energy.** A scripted agent arrived with 0.041 energy to spare.

We therefore changed the wall (58 °C/σ 0.35 m → 60 °C/σ 0.5 m) and the lowest start energy (0.15 → 0.08). We verified both analytically and by scripted runs in the physics engine (`results/design_check.txt`).

### 4.2 Worlds must make the tested capacity useful

In Study 2 the agents' failure to use the switch was not a quirk of learning.
A scripted design check showed that switching was simply not worth it in that
world (−0.04). A test of self-caused prediction presupposes that acting on the
world pays. That condition can and should be checked before training.

### 4.3 Control agents must be competent

As first specified, the withdrawal reflex reversed its commanded heading on
every trigger. It oscillated inside heat sources until death: all 28 of its
deaths in 30 episodes were from damage. A control that fails this way makes
markers look more discriminating than they are. We used a memoryless fix
(reverse the actual motion; keep escaping while the heat falls) and report
both versions (`results/literal_reflex/`).

## 5. Discussion

**Markers must be benchmarked against minimal mechanisms.** Across both
studies, the markers most often proposed as accessible evidence of richer
processing were met by trivial mechanisms:
- anticipatory avoidance, by a one-step thermotactic reflex;
- body-versus-world discrimination, by a no-change predictor with dedicated interoceptive channels;
- "self/other" information in internal states, by untrained networks and raw inputs.

None of these results says that anticipation or internal representations are
irrelevant to sentience or self-awareness. They say that such observations
carry no evidential weight *unless* the minimal mechanisms fail them. This
parallels the gaming problem discussed for AI sentience (Birch 2024), and it
is directly testable in artificial agents.

**Tests can be made robust.** The pre-registered agency test was not fooled:
- it detected a known comparator mechanism;
- it rejected random networks;
- it defeated a position shortcut.

Its dissociation logic (freezing self-motion versus other-agent signals) adds
causal, not merely correlational, evidence about which signals a prediction
depends on.

**The limiting factor was the learners, not the tests.** Survival training
plus a generic next-observation loss produced agents that failed in three
distinct ways:
- **They free-rode** when others changed the world for them (Study 2).
- **They failed to discover** a necessary action (Study 2b).
- **They settled into doing nothing** (Study 1b).

In none of these cases did the agents gather the experience from which a
self-prediction could be learned. These pre-registered negative results warn
against assuming that self-models emerge "for free" from homeostatic training.
Positive tests of the markers now require competent learners, via:
- longer training;
- curricula or exploration bonuses;
- prediction objectives not dominated by easy channels;
- world-model agents.

Each should be pre-registered separately and evaluated with the same
validated battery. The exploratory hint that distal predictions depend on
self-motion signals (Study 2) did not replicate consistently in Study 2b.

**Scope.** All results are functional. Nothing here bears on whether any agent
has subjective experience. Passing or failing these tests is evidence about
mechanisms, not about feelings.

**Limitations.**
- a disc body with no limbs;
- a single environment per study;
- five training runs per variant and one fixed, untuned training budget, which our learners did not master (Studies 1b, 2b);
- a scripted (non-learning) other robot;
- a forward model trained with an unweighted mean-squared loss.

A different agent or objective could produce a different result.

## 6. Data and code availability

All code, pre-registration, trained models, raw trial data and figures are in
the repository. Every figure and table is regenerated by:
- `python -m experiments.run_baseline --seeds 30 --out results/`
- `bash experiments/train_all.sh` followed by `python -m experiments.run_v02`
- Study 2b: `WORLD=agency_b OUT=results/v02b/models bash experiments/train_all.sh`, then `python -m experiments.run_v02 --models results/v02b/models --out results/v02b --world agency_b`
- Study 1b: `WORLD=study1 OUT=results/study1b/models RUNS="FULL:0 FULL:1 FULL:2 FULL:3 FULL:4" bash experiments/train_all.sh`, then `python -m experiments.run_baseline --seeds 30 --agents --learned results/study1b/models --out results/study1b` and `python -m experiments.report_study1b`
- Post-hoc and exploratory: `python -m experiments.sensitivity_v02`, `python -m experiments.explore_v02`, `python -m experiments.explore_study1b`, `python -m experiments.necessity_check`

## References

- Berg, H. C. & Brown, D. A. (1972). Chemotaxis in *Escherichia coli* analysed by three-dimensional tracking. *Nature* 239:500–504.
- Birch, J. (2024). *The Edge of Sentience: Risk and Precaution in Humans, Other Animals, and AI.* Oxford University Press.
- Birch, J., Burn, C., Schnell, A., Browning, H. & Crump, A. (2021). *Review of the Evidence of Sentience in Cephalopod Molluscs and Decapod Crustaceans.* LSE Consulting.
- Blakemore, S.-J., Wolpert, D. M. & Frith, C. D. (1998). Central cancellation of self-produced tickle sensation. *Nature Neuroscience* 1:635–640.
- Butlin, P., Long, R., et al. (2023). Consciousness in Artificial Intelligence: Insights from the Science of Consciousness. arXiv:2308.08708.
- Caterina, M. J., et al. (1997). The capsaicin receptor: a heat-activated ion channel in the pain pathway. *Nature* 389:816–824.
- Elwood, R. W. & Appel, M. (2009). Pain experience in hermit crabs? *Animal Behaviour* 77:1243–1246.
- Keramati, M. & Gutkin, B. (2014). Homeostatic reinforcement learning for integrating reward collection and physiological stability. *eLife* 3:e04811.
- Man, K. & Damasio, A. (2019). Homeostasis and soft robotics in the design of feeling machines. *Nature Machine Intelligence* 1:446–452.
- Schulman, J., Wolski, F., Dhariwal, P., Radford, A. & Klimov, O. (2017). Proximal policy optimization algorithms. arXiv:1707.06347.
- Sneddon, L. U., Elwood, R. W., Adamo, S. A. & Leach, M. C. (2014). Defining and assessing animal pain. *Animal Behaviour* 97:201–212.
- Solms, M., et al. (2026). Inferring affective consciousness in an artificial agent: a case study. *Journal of Consciousness Studies* 33(7–8):14–34.
- Todorov, E., Erez, T. & Tassa, Y. (2012). MuJoCo: a physics engine for model-based control. *IROS 2012.*
- von Holst, E. & Mittelstaedt, H. (1950). Das Reafferenzprinzip. *Naturwissenschaften* 37:464–476.
- Wittenburg, N. & Baumeister, R. (1999). Thermal avoidance in *Caenorhabditis elegans*: an approach to the study of nociception. *PNAS* 96:10477–10482.
- Yoshida, N., Kanazawa, H. & Kuniyoshi, Y. (2024). Synthesising integrated robot behaviour through reinforcement learning for homeostasis. *bioRxiv* 2024.06.03.597087.
- Yoshida, N., Daikoku, T., Nagai, Y. & Kuniyoshi, Y. (2024). Emergence of integrated behaviors through direct optimization for homeostasis. *Neural Networks.*
