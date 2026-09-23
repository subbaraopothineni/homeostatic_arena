# DRAFT: Which behavioural markers of sentience and self-awareness can a simple mechanism fake? Two controlled studies with homeostatic agents

*Working draft generated alongside the code. Author list, affiliations,
funding and acknowledgements to be completed by the authors. All numbers are
taken from the result files named in brackets; do not edit numbers by hand.*

## Abstract (to be finalised after Study 2)

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
[Results: `results/v02/report.md`.]

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

## 3. Results

### 3.1 Study 1 [`results/summary.csv`, `results/seeds100/summary.csv`]

- **Anticipatory avoidance is passed by a memoryless reflex.** The thermotactic reflex left 71/71 heat encounters before nociceptor activation (rate 1.00 [1.00, 1.00]; zero cumulative damage), whereas the nociceptive reflex scored 0.25 [0.15, 0.36], no better than random (0.34 [0.20, 0.49]).
- **No baseline agent passed the trade-off marker.** Neither reflex crossed the heat wall at any start energy. The random agent's significantly *negative* score (−0.47 [−0.67, −0.27]) is an opportunity artefact: at low energy it dies before reaching the wall.
- **Sensitization has a built-in positive bias.** Memoryless agents scored +9.95 °C [7.16, 12.87] (random) and +8.77 °C [6.14, 11.43] (nociceptive reflex) at 100 seeds, because all "before" encounters are non-harmful by construction. A like-for-like variant was ≈ 0.
- **Survival separates competent from random agents,** not reflex from learner (reflexes 0.70–0.83 vs random 0.23).

### 3.2 Study 2 [`results/v02/report.md`]

*To be written from the generated report after the pre-registered analysis
has run.*

## 4. Additional methodological findings

### 4.1 Test worlds must be verified, not assumed

The trade-off world, as first specified, did not pose a trade-off:
- **Crossing the heat wall cost only 0.007 damage at top speed.**
- **The "impossible" detour was survivable at the lowest start energy.** A scripted agent arrived with 0.041 energy to spare.

We therefore changed the wall (58 °C/σ 0.35 m → 60 °C/σ 0.5 m) and the lowest start energy (0.15 → 0.08). We verified both analytically and by scripted runs in the physics engine (`results/design_check.txt`).

### 4.2 Control agents must be competent

As first specified, the withdrawal reflex reversed its commanded heading on
every trigger. It oscillated inside heat sources until death: all 28 of its
deaths in 30 episodes were from damage. A control that fails this way makes
markers look more discriminating than they are. We used a memoryless fix
(reverse the actual motion; keep escaping while the heat falls) and report
both versions (`results/literal_reflex/`).

## 5. Discussion (outline; complete after Study 2)

- Markers that can be met by a distal sensor plus a one-step rule (anticipation) should not count as evidence beyond a reflex arc.
- Trade-off and sensitization were not passed by any reflex. They are candidates for discriminating markers, but their metrics need care (opportunity confound; selection bias).
- Study 2: what the self-prediction and dissociation results show, and do not show, about functional self/other distinction.
- Scope: functional measurements only. No claim about subjective experience.
- Limitations:
  - a disc body with no limbs;
  - a single environment;
  - a small number of training runs;
  - hyperparameters that were not tuned;
  - a scripted other robot.

## 6. Data and code availability

All code, pre-registration, trained models, raw trial data and figures are in
the repository. Every figure and table is regenerated by:
- `python -m experiments.run_baseline --seeds 30 --out results/`
- `bash experiments/train_all.sh` followed by `python -m experiments.run_v02`

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
