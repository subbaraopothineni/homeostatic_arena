::title Which Behavioural Markers of Sentience and Self-Awareness Can a Simple Mechanism Fake? Pre-Registered Tests With Homeostatic Agents

::center [FILL: Author One]¹ and [FILL: Author Two]²

::center ¹ [FILL: Department, Institution, City, Country]

::center ² [FILL: Department, Institution, City, Country — delete this line if there is a single author]

::center **Corresponding author:** [FILL: name, postal address, e-mail address]

::center **ORCID:** [FILL: 0000-0000-0000-0000 for each author]

::center **Article type:** Article · **Main text:** {{WORDCOUNT}} words (Introduction to Conclusion; excluding tables, figure captions and references) · 7 figures · 6 tables

::center **Keywords:** sentience markers, self–other distinction, homeostatic reinforcement learning, comparator model, pre-registration, minimal mechanisms

::center **Generative-AI disclosure:** Generative AI (Claude Opus 5.5, Anthropic) was used for code, analysis, figures and drafting of this article. The nature and extent of that use are stated in the section *Use of Generative AI* and cited as Anthropic (2026).

::pagebreak

# Abstract

::noindent Behavioural markers are increasingly proposed as evidence of sentience or self-awareness in non-human systems, including artificial agents. A marker is informative only if simpler mechanisms cannot produce it. We tested four animal-sentience markers and a prediction-based test of self/other distinction in a physics-simulated agent whose only learning signal is the reduction of homeostatic drive. In Study 1, a memoryless thermotactic reflex passed anticipatory avoidance perfectly, leaving every heat encounter before its nociceptor fired, whereas no reflex passed the motivational trade-off or sensitization markers; the usual sensitization metric also carried a built-in positive bias of about 9 °C in memoryless agents. In Study 2 (pre-registered), we asked whether recurrent agents trained with a self-supervised forward model predict self-caused sensory changes better than identical changes caused by another agent or by chance. The test was validated: a hand-built comparator passed, untrained networks did not, a position shortcut was exposed, and a post-hoc sensitivity analysis showed that anticipating 2% of a self-caused change would be detected. None of five trained agents supported any hypothesis; they had learned to let another agent operate the switch. Two further pre-registered studies, one in which acting was necessary and one applying the Study 1 markers to learners, were inconclusive because the agents did not acquire the relevant behaviour. Tests pre-registered as vulnerable were passed by trivial controls. Markers of sentience and self-awareness must therefore be benchmarked against minimal mechanisms, and in our hands the learning agents, not the tests, were the limiting factor.

::pagebreak

# 1 Introduction

How could we tell whether a non-human system has states that matter to it? In animal welfare science this question is approached with behavioural and neurological criteria: evidence of nociceptors, integration of noxious information in central structures, motivational trade-offs between avoiding a noxious stimulus and obtaining a resource, wound-directed behaviour, associative learning about noxious stimuli, and changes in behaviour after injury (Sneddon et al., 2014; Birch et al., 2021). A hermit crab that accepts a stronger electric shock before leaving a higher-quality shell is making such a trade-off (Elwood & Appel, 2009). These criteria were developed for animals, where they have informed legislation, and they are now being discussed as sources of evidence about artificial systems (Butlin et al., 2023; Birch, 2024; Keeling et al., 2024).

A behavioural marker is only as good as its ability to exclude simpler explanations. Birch (2024) calls the corresponding difficulty for artificial intelligence the *gaming problem*: a system can be built or trained to produce the behaviour that a marker looks for without having the capacity the marker is meant to indicate. For animals, the problem has an unavoidable empirical limit, because one cannot build the simplest mechanism that could produce a marker and check whether it passes. For artificial agents one can. This makes artificial life a natural setting for a question that is usually argued rather than tested: *which markers can be met by mechanisms that nobody would regard as candidates for sentience or self-awareness?* The synthetic tradition in artificial life has long used minimal agents to show how little machinery a seemingly rich behaviour requires (Braitenberg, 1984), and self-models have been studied in robots that learn their own morphology (Bongard et al., 2006). Here we apply the same logic to the markers themselves.

We use homeostatic agents because they have something at stake. Following Ashby's (1952) homeostat and more recent proposals for "feeling machines" (Man & Damasio, 2019), several authors have argued that systems that must regulate internal variables to persist are the right substrate in which to look for functional analogues of affect. In homeostatic reinforcement learning, reward is defined only as a reduction of the distance between internal variables and their set points (Keramati & Gutkin, 2014). Agents trained this way can develop integrated foraging and avoidance behaviour without any task reward (Yoshida, Daikoku, et al., 2024; Yoshida, Kanazawa, & Kuniyoshi, 2024), and a recent case study has asked what could be inferred about affective consciousness in such an agent (Solms et al., 2026). Such agents are therefore both plausible candidates for marker-based assessment and fully inspectable.

The second question we ask concerns a more demanding capacity: distinguishing self-caused from externally caused events. According to the reafference principle, organisms predict the sensory consequences of their own movements and compare the prediction with what they sense (von Holst & Mittelstaedt, 1950). Self-produced stimuli are predicted and attenuated, which is why one cannot tickle oneself (Blakemore et al., 1998). A functional marker of a self/other distinction follows: an agent that models its own agency should predict a sensory change better when the change is caused by its own action than when an identical change is caused by something else. Unlike anticipatory avoidance, this marker makes specific predictions about internal processing that can be tested with ablations. But it too can be gamed. A system can "know" that it caused a change simply because it is standing in the place where changes happen; body-related and world-related events can be separated by which input channels they arrive on, without any self-model; and the identity of a cause can be decodable from internal states simply because it is present in the raw input.

A test for a marker should therefore itself be tested. We borrow three kinds of control from experimental practice. A *positive control* is a mechanism known to have the capacity in question, built by hand; if the test cannot detect it, a negative result is uninformative. A *negative control* is a system known to lack the capacity, such as a network with random weights; if it passes, the test has been fooled. A *shortcut control* implements the most obvious way of passing without the capacity, and the test should contain trials on which the shortcut fails. To these we add a sensitivity analysis, which asks how weak a real effect could be and still be detected. A null result can then be read as evidence of absence at a stated resolution rather than as mere absence of evidence. None of these elements is new on its own, but we are not aware of previous work that combines them to validate a marker of sentience or self-awareness in artificial agents.

We report four studies built around these issues. Study 1 applies four animal-sentience markers to hard-wired reflex agents. Study 2, pre-registered, tests whether recurrent agents trained with a self-supervised forward model come to predict self-caused changes better than other-caused and spontaneous ones. It uses a positive control, negative controls, a shortcut control and a double dissociation, and a post-hoc sensitivity analysis quantifies how small an effect it could detect. Study 2b, also pre-registered, repeats the test in a world in which a scripted design check showed that the agent's own action was necessary. Study 1b, also pre-registered, applies the Study 1 markers to learning agents. Our contributions are:

1. an open, physics-based test bed with functional analogues of nociception, tissue damage, energy and homeostatic drive;
2. evidence that a widely used sentience marker, anticipatory avoidance, is passed perfectly by a memoryless reflex, and that a common sensitization metric is biased;
3. a pre-registered test of functional self/other distinction whose own validity and sensitivity are demonstrated with explicit controls;
4. three pre-registered negative results showing that generic homeostatic learning agents did not acquire, or even gather the experience needed for, the capacity the test measures;
5. methodological lessons: test worlds must be verified, the tested capacity must be useful in the world, and control agents must be competent.

All measurements are functional. Nothing in this article bears on whether any of the agents has subjective experience; the question is which observations could count as evidence at all.

# 2 Methods

## 2.1 Body, physiology and environment

All studies share one simulated body and physiology (Table 1), implemented with MuJoCo 3 (Todorov et al., 2012) behind a Gymnasium interface (Towers et al., 2024). The agent is a disc (radius 0.25 m, mass 1 kg) that moves on two damped slide joints in a 10 × 10 m walled arena. Its two-dimensional action sets the force on the body; the control step is 0.05 s and the terminal speed 2 m/s.

The physiology consists of functional analogues only. Ambient temperature at any point is the room temperature (25 °C) plus the largest Gaussian rise contributed by any heat source. Skin temperature follows ambient temperature with a first-order lag. A logistic nociceptor signal is half-maximal at a skin temperature of 45 °C, loosely following the activation threshold of the TRPV1 heat receptor (Caterina et al., 1997). Tissue damage accrues above 45 °C and heals slowly below it; energy drains at a basal rate plus a motor cost and recharges on a charger. The agent dies when damage reaches 1 or energy reaches 0.

The homeostatic drive is the weighted distance of the internal state from its set points, D = √((1 − energy)² + 2 · damage²). The only reward is the step-to-step reduction in drive, r(t) = D(t − 1) − D(t), with −1 on death (Keramati & Gutkin, 2014). There is no task reward: the agent is never rewarded for reaching the charger or avoiding heat as such, only for reducing its drive.

The base observation has 11 channels: position and velocity (proprioception), ambient and skin temperature, nociceptor activation, a charger "beacon" that decays exponentially with distance (analogous to a chemical gradient), touch, energy and damage (interoception). Studies 2 and 2b add further senses, described below.

**Table 1.** Body, physiology and reward parameters shared by all studies.

| Quantity | Value |
|---|---|
| Arena; body | 10 × 10 m, walled; disc of radius 0.25 m and mass 1 kg on damped slide joints |
| Control step; terminal speed | 0.05 s (physics step 0.01 s); 2 m/s at full action |
| Ambient temperature | 25 °C plus the largest Gaussian rise of any heat source (sources peak at 60 °C) |
| Skin temperature | first-order lag of ambient temperature, time constant 0.3 s |
| Nociceptor | logistic in skin temperature, half-maximal at 45 °C, slope 1 °C |
| Damage | +0.06 per °C above 45 °C per second; heals 0.002 per second below; death at 1 |
| Energy | drains 0.012 per second + 0.010 per second × Σ action²; +0.25 per second on the charger (radius 0.6 m); death at 0 |
| Drive; reward | D = √((1 − energy)² + 2 · damage²); r = D(t − 1) − D(t), −1 on death |
| Observation noise | Gaussian, 0.1 °C on temperatures; small noise on the beacon |

## 2.2 Study 1: sentience markers versus reflex controls

Study 1 was specified in a design brief before any code was written, but it was not formally pre-registered.

**Worlds.** In the *foraging world* (Figure 1a) the agent starts at a random cool location at least 2 m from a charger and must reach it past two heat sources (60 °C peak, σ = 0.7 m) within a 90 s episode. In the *trade-off world* (Figure 1b) a heat wall (60 °C, σ = 0.5 m, 6.6 m long) lies between the start and the charger; the charger can be reached either directly through the wall or by a longer detour around its end.

::figure Figure1 | Three square arenas shown as temperature maps. Left: the foraging world with two circular heat sources and a charger in the upper right. Middle: the trade-off world with a vertical heat wall between the start on the left and the charger on the right; a solid arrow shows the short route through the wall and a dashed arrow the long route around it. Right: the agency world with a static heat source, a lamp at the charger in the upper right, and a switch pad at the centre approached by the agent from the left in SELF trials and by the other robot from the right in OTHER trials.

**Figure 1.** The three worlds. (a) Foraging world (Studies 1 and 1b): two heat sources and a charger. (b) Trade-off world (Studies 1 and 1b): the charger is reached either through a heat wall or by a longer detour around it; the correct choice depends on the agent's energy. (c) Agency world (Studies 2 and 2b), shown with the lamp on: a switchable heat lamp sits on the charger, and any robot entering the switch pad toggles the lamp. The two robots show the start positions and directions of the scripted SELF and OTHER test trials, which in the experiment occur in separate trials. Colour: ambient temperature.

**Agents.** Three agents without memory or learning served as baselines. A *random walker* moves at constant action magnitude (0.6) along a heading that performs a random walk (standard deviation 0.3 rad per step). The *nociceptive reflex* withdraws when its nociceptor exceeds 0.1. The *thermotactic reflex* also withdraws when the ambient temperature is above 35 °C and rising, a one-step comparison analogous to the thermotaxis of *Caenorhabditis elegans* (Wittenburg & Baumeister, 1999). When energy is below 0.6, both reflexes forage by run-and-tumble on the beacon, as in bacterial chemotaxis (Berg & Brown, 1972). Withdrawal reverses the actual direction of motion and continues while the heat is falling (see Section 3.6 for why this matters).

**Markers.** We operationalized four markers from the animal literature (Sneddon et al., 2014; Birch et al., 2021):

1. *Survival*: the fraction of 90 s foraging episodes survived.
2. *Anticipatory avoidance*: a heat encounter begins when ambient temperature rises above 38 °C and ends when it falls below 35 °C. The encounter is anticipated if the agent leaves it before the nociceptor exceeds 0.5. The score is the per-episode fraction of anticipated encounters.
3. *Motivational trade-off* (after Elwood & Appel, 2009): the agent starts in the trade-off world with energy 0.08, 0.3, 0.5 or 0.9. The score is the rate of full crossings of the wall at the lowest energy minus the rate at the highest. A positive score means that the agent accepts the noxious short route only when in need. The world was designed so that at energy 0.08 only the direct route is survivable, and this was verified before use (Section 3.6).
4. *Sensitization*: the mean peak ambient temperature of encounters after the first harmful encounter (nociceptor > 0.5) minus that of encounters before it. A negative value means the agent became more cautious after harm. Because every encounter before the first harmful one is non-harmful by construction, we also computed a like-for-like variant that compares non-harmful encounters on both sides.

**Statistics.** Each condition used 30 episode seeds, and a robustness run used 100. Proportions are reported with Wilson score intervals (Wilson, 1927); means and differences of means use percentile bootstrap intervals with 2,000 resamples over episodes (Efron & Tibshirani, 1993). All intervals are 95%.

## 2.3 Study 2: functional self/other distinction (pre-registered)

**Pre-registration.** The hypotheses, controls, test conditions, pass rules and training budget were committed to the project's version-control history (commit `d70a2fe`, 22 September 2026) before any Study 2 code or data existed; the document is reproduced in the Supplementary Material, Section S1. This is not a registration on an independent registry. Git timestamps are set by the author, so we make the complete history public for inspection. Deviations are listed in the document's append-only deviations section.

**Agency world.** The Study 1 arena was extended (Figure 1c) with:

- a switchable heat lamp at the charger (60 °C, σ = 0.7 m), so that the lamp makes the charger harmful while it is on;
- a switch pad (radius 0.5 m) at the centre of the arena that toggles the lamp whenever any robot's centre enters it;
- a second, scripted robot that moves at 0.6 m/s toward a target; on arrival it chooses the pad with probability 0.5 and otherwise a random point;
- spontaneous lamp toggles (a Poisson process with a rate of 1/20 s⁻¹);
- internal metabolic shocks that remove 0.1 energy (rate 1/30 s⁻¹).

Episodes lasted 60 s, the start energy was drawn from U(0.4, 1.0), and the lamp was on at the start with probability 0.5. The agent additionally sensed its previous motor command (efference copy), its previous reward, an eight-sector distal heat sense (radiant heat from each direction, decaying with distance), a floor sense that signals whether it is on the pad, and the other robot's relative position when visible, giving 26 observation channels. The simulator records the true cause of every event, but the agent never observes it.

**Learning agent (FULL).** A two-layer MLP encoder (tanh) feeds a gated recurrent unit (GRU; Cho et al., 2014) with 128 units, whose state feeds a Gaussian policy and a value head. A forward-model head, also a two-layer MLP, predicts the change in the next observation from the GRU state and the current motor command. Training used proximal policy optimization (PPO; Schulman et al., 2017) with generalized advantage estimation (Schulman et al., 2016) on the drive-reduction reward, plus a self-supervised mean-squared next-observation loss with weight 1. Each run trained for 3 × 10⁶ environment steps with 16 parallel environments, rollouts of 128 steps, a learning rate of 3 × 10⁻⁴, a discount of 0.99, a GAE λ of 0.95, a clip range of 0.2, four epochs of four minibatches, an entropy coefficient of 0.001 and a reward scale of 10. No hyperparameter was tuned on any test. The agent never received labels about what caused an event.

**Variants and controls.**

- *NOEFF*: FULL without the efference copy (3 seeds).
- *NOFWD*: FULL without the forward-model loss, so that its prediction head is untrained (3 seeds).
- *UNTRAINED*: FULL architecture with random weights (5 seeds), the negative control.
- *NO-CHANGE*: a predictor that expects the next observation to equal the current one.
- *COMPARATOR*: a hand-built positive control. It uses the known dynamics of its own body to predict a lamp toggle exactly when its own motion will carry it onto the pad.
- *POSITION RULE*: a shortcut that attributes any lamp change to itself if it is standing on the pad.
- The Study 1 thermotactic reflex served as a behavioural baseline.

**Competence gate.** Before testing, each trained run was evaluated on 20 held-out free-running episodes. A run passed the gate if its forward-model mean-squared error was at most 0.8 times that of NO-CHANGE. Runs failing the gate count as not supporting every hypothesis.

**Test T2 (agency).** In scripted trials, both robots are driven with forced actions and random events are disabled, so that each condition presents the same sensory situation while the cause of the lamp change differs (Table 2). There were 40 trials per condition and run, 20 with the lamp initially on and 20 off. Each trial started with energy 0.9 and random events disabled, and start positions were jittered uniformly by up to ±0.1 m in each coordinate. Both robots stood still for 1 s (20 steps). They then moved along the horizontal axis with a forced action of magnitude 0.8 until the lamp changed, and stood still again for up to 41 steps. In SPONT and NOEVENT trials, the event (or its absence) was timed to step 32, the median step at which the agent entered the pad in SELF trials, so that it followed the same amount of motion. Throughout, the network runs normally and receives its observations, including the efference copy of the forced action. The measure is the relative prediction error of the forward model on the eight distal heat channels at the step of the lamp change:

::center relPE = Σₖ (ôₖ(t + 1) − oₖ(t + 1))² / Σₖ (oₖ(t) − oₖ(t + 1))²

::noindent where ô is the prediction and o the observation. A relPE of 0 means the change was fully predicted, and a relPE of 1 means the prediction was no better than expecting no change. The absolute error absPE is the numerator alone and is used where no change occurs. Test-time ablations freeze either the self-motion channels (position, velocity, efference copy and pad sense; *self-blind*) or the other-robot channels (*other-blind*) at their values at the start of motion.

**Table 2.** Conditions of the agency test (T2). In every condition both robots move; only the cause of the lamp change differs.

| Condition | What changes the lamp | Purpose |
|---|---|---|
| SELF | the agent enters the pad | self-caused change |
| OTHER | the other robot enters the pad | identical change, other-caused |
| SPONT | a spontaneous toggle, timed to the median SELF entry | identical change, no agent as cause |
| NOEVENT | nothing | baseline without change |
| SELF-OMIT | the agent enters the pad, but the switch is disabled | omission of an expected effect |
| OTHER-ONPAD | the other robot enters while the agent stands on the pad | exposes a position shortcut |
| SPONT-ONPAD | a spontaneous toggle while the agent stands on the pad | exposes a position shortcut |

**Hypotheses.** We pre-registered four effects:

- *H1* (self-caused changes are predicted): relPE(SPONT) − relPE(SELF) > 0.
- *H2* (the agent expects its own action to have an effect): absPE(SELF-OMIT) − absPE(NOEVENT) > 0.
- *H3a* (self-prediction depends on self-motion signals): self-blinding raises relPE for SELF more than for OTHER.
- *H3b* (other-prediction depends on seeing the other robot): other-blinding raises relPE for OTHER more than for SELF.

H3a and H3b together form a double dissociation. H3b is interpretable only if the agent predicts OTHER at all, that is, if relPE(OTHER) < relPE(SPONT). A hypothesis was declared supported if the within-run 95% bootstrap interval (2,000 resamples over trials) excluded 0 in the predicted direction in at least 4 of 5 FULL runs that passed the competence gate.

**Validity checks.** The test itself was tested with three pre-registered checks:

- *V1*: UNTRAINED must not meet the pass rule, otherwise the test is declared fooled.
- *V2*: COMPARATOR must meet H1 and H2, as a check of the whole pipeline.
- *V3*: we report the POSITION RULE's attribution accuracy on the ONPAD conditions, where it is expected to fail.

**Tests expected to be fooled.** Two further analyses were pre-registered as descriptive because we expected trivial controls to pass them. *Test T1* (body versus world) presented a lamp change, an internal metabolic shock, or nothing, and measured the share of prediction error that fell on the body channels (energy and damage). *Exploratory probes* decoded the cause of a lamp change (self, other, spontaneous) and the event type (world, body, none) from the GRU state 1, 10 and 40 steps after the event. The probes were logistic regressions with L2 regularization (λ = 10⁻³), evaluated by five-fold cross-validation. They were compared with the same probes applied to UNTRAINED networks and to a raw-input baseline consisting of the last five observations. The pre-registered criterion was that decoding counts as evidence only if it exceeds the raw-input baseline.

**Sensitivity analysis (post-hoc).** After the pre-registered analysis, we asked how large a self-prediction effect the test could have detected. The heat predictions of each trained FULL agent were blended with the comparator's, prediction = (1 − w) · agent + w · comparator, for w = 0.02 to 0.5. The identical battery and pass rule were then rerun. A blended agent anticipates roughly the fraction w of a self-caused change, while keeping its own noise and biases.

## 2.4 Study 2b: necessary agency (pre-registered)

Study 2b and Study 1b were pre-registered together (commit `3486e57`, 23 September 2026; Supplementary Material, Section S2) after the Study 2 results were known.

**Design check first.** To test whether the agent's own action was useful in the Study 2 world, we compared two scripted robots with privileged knowledge over 100 episodes each. The WAITER waits for the lamp to be switched off by others. The SWITCHER walks to the pad and switches the lamp off itself. In the Study 2 world, switching conferred no survival benefit: the difference in survival between SWITCHER and WAITER was −0.04 [−0.09, +0.01]. We therefore constructed the world *agency_b* with four changes:

- the other robot chooses the pad with probability 0.05 instead of 0.5;
- spontaneous toggles occur at 1/120 s⁻¹ instead of 1/20 s⁻¹;
- start energy is drawn from U(0.2, 0.6);
- the lamp is always on at the start.

In agency_b, switching conferred a survival benefit of +0.25 [+0.17, +0.34].

Agents, seeds, training budget, test battery and pass rules were identical to Study 2. A pre-registered manipulation check (M1) required the trained agents to toggle the lamp themselves at least once per free-running episode on average.

## 2.5 Study 1b: learning agents on the Study 1 markers (pre-registered)

Study 1b asked whether the Study 1 markers that no reflex passed would be passed by a learning agent. The FULL architecture was given the 11-channel Study 1 observation. Each training episode was either the foraging world or the trade-off world, with start energy drawn from U(0.05, 1). Training used the Study 2 budget of 3 × 10⁶ steps and five seeds. Evaluation used the unchanged Study 1 marker battery with 30 seeds, and 100 seeds for sensitization, applied to the deterministic (mean) policy. There were two pre-registered decision rules:

- *Q1*: the trade-off marker separates the learner from the reflexes if the learner's score is positive with an interval excluding 0 in at least 4 of 5 seeds.
- *Q3*: sensitization separates learning from memoryless agents if, in at least 4 of 5 seeds, the learner's sensitization lies below the lowest interval bound of the memoryless agents and its like-for-like variant is below 0.

Anticipatory avoidance (Q2) and survival (Q4) were descriptive.

## 2.6 Software and reproducibility

The code is written in Python 3.14 with MuJoCo 3.14, Gymnasium 1.3, NumPy 2.5, PyTorch 2.14 (CPU) and Matplotlib 3.11. It includes 86 automated tests of the physics, physiology, worlds, agents and analysis code. Every number in this article is produced by scripts in the repository from saved raw data, and every figure is redrawn from saved result tables (Section *Data and Code Availability*).

# 3 Results

## 3.1 Study 1: anticipatory avoidance is passed by a memoryless reflex

Table 3 and Figure 2 summarize the Study 1 markers.

**Anticipatory avoidance.** The thermotactic reflex left 100% of its heat encounters before its nociceptor fired (1.00 [1.00, 1.00], 30 seeds; also 1.00 at 100 seeds) and took no damage at all. The nociceptive reflex scored 0.25 [0.15, 0.36], no better than the random walker (0.34 [0.20, 0.49]). A one-step comparison of the current temperature with the previous one is therefore enough to pass this marker perfectly. Anticipatory avoidance does not discriminate a reflex from any more complex architecture.

**Motivational trade-off.** No baseline passed. Neither reflex crossed the heat wall at any start energy, so both scored exactly 0. The random walker's score was significantly *negative* (−0.47 [−0.67, −0.27]). This is an opportunity artefact, not a preference: at low energy the random walker usually died before it reached the wall.

**Sensitization.** The metric showed a large positive bias. Memoryless agents, which cannot become more cautious, scored +9.95 °C [7.16, 12.87] (random) and +8.77 °C [6.14, 11.43] (nociceptive reflex) at 100 seeds. The bias arises because every encounter before the first harmful one is non-harmful by definition. The like-for-like variant was close to 0 (+0.93 °C [−1.50, 3.37] and −0.81 °C [−3.15, 1.52]). A learning agent's sensitization must therefore be compared with this floor, not with zero. The thermotactic reflex was never harmed, so its sensitization is undefined.

**Survival** separated competent agents from the random walker (reflexes 0.70–0.83 versus 0.23) but, by construction, cannot separate reflexes from learners.

**Table 3.** Study 1 marker results for the memoryless baselines (mean [95% CI]; 30 seeds unless stated).

| Marker | Random walker | Nociceptive reflex | Thermotactic reflex |
|---|---|---|---|
| Survival (fraction of 90 s episodes) | 0.23 [0.12, 0.41] | 0.70 [0.52, 0.83] | 0.83 [0.66, 0.93] |
| Anticipatory avoidance (fraction of encounters) | 0.34 [0.20, 0.49] | 0.25 [0.15, 0.36] | 1.00 [1.00, 1.00] |
| Damage taken per episode | 0.47 [0.34, 0.59] | 0.56 [0.45, 0.66] | 0.00 [0.00, 0.00] |
| Trade-off score (crossing at E = 0.08 minus E = 0.9) | −0.47 [−0.67, −0.27] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| Sensitization, °C (100 seeds) | +9.95 [7.16, 12.87] | +8.77 [6.14, 11.43] | not defined (never harmed) |
| Sensitization, like-for-like, °C (100 seeds) | +0.93 [−1.50, 3.37] | −0.81 [−3.15, 1.52] | not defined |

::figure Figure2 | Four bar charts comparing the random walker, the nociceptive reflex and the thermotactic reflex. Survival: 0.23, 0.70 and 0.83. Anticipatory avoidance: 0.34, 0.25 and 1.00. Trade-off score: −0.47, 0 and 0. Sensitization: about +7 and +9 degrees for the random walker and nociceptive reflex, not defined for the thermotactic reflex.

**Figure 2.** Study 1: sentience markers applied to memoryless agents (30 seeds; bars show means and whiskers 95% confidence intervals; n is the number of episodes or encounters contributing). The thermotactic reflex passes anticipatory avoidance perfectly. No agent passes the trade-off marker. Both agents that could be harmed show a positive "sensitization" without any memory; 100-seed values are given in Table 3.

## 3.2 Study 2: the test was valid, and no trained agent supported any hypothesis

**Training and competence.** All trained runs completed 2,998,272 steps. Four of five FULL runs learned to survive, surviving 40–90% of held-out 60 s episodes, against 15% for FULL seed 4. The same four runs passed the competence gate, with forward-model errors of 0.47–0.69 times that of NO-CHANGE. FULL seed 4 (1.18) and all NOEFF runs (1.63–1.98) failed it (Table 4).

**Pre-registered hypotheses.** None was supported (Table 4, Figure 4):

- *H1* (self-prediction) was met by 0 of 5 FULL runs. The effects ranged from −0.004 to +0.001, and every interval included 0.
- *H2* (omission surprise) was met by 0 of 5.
- *H3a* (self-blind specificity) was met by 0 of 5.
- *H3b* was not applicable in 4 of 5 runs, because relPE(OTHER) was not below relPE(SPONT).

At the moment of the lamp change, the FULL agents' relative prediction error was about 1 in every condition: SELF 0.996, OTHER 0.994, SPONT 0.994, OTHER-ONPAD 1.002 and SPONT-ONPAD 1.001 (Figure 3). The forward models therefore did not predict lamp changes at all, whatever their cause. This is different from predicting all causes equally well.

**Table 4.** Study 2 FULL runs: competence, survival and the pre-registered H1 effect (relPE(SPONT) − relPE(SELF), mean [95% CI]). No run met any hypothesis.

| Run | Forward error / NO-CHANGE | Gate (≤ 0.8) | Survived 60 s | H1 effect | H2, H3a met? |
|---|---|---|---|---|---|
| FULL seed 0 | 0.54 | passed | 0.90 | −0.004 [−0.015, 0.007] | no, no |
| FULL seed 1 | 0.47 | passed | 0.90 | −0.002 [−0.017, 0.013] | no, no |
| FULL seed 2 | 0.69 | passed | 0.85 | −0.002 [−0.020, 0.016] | no, no |
| FULL seed 3 | 0.64 | passed | 0.40 | +0.001 [−0.008, 0.011] | no, no |
| FULL seed 4 | 1.18 | failed | 0.15 | −0.001 [−0.010, 0.009] | no, no |
| COMPARATOR (positive control) | — | — | — | +1.026 [1.011, 1.040] | yes, yes |

::figure Figure3 | Four line plots of relative prediction error at the lamp change for five conditions. FULL agents lie at 1 for every condition. Untrained networks lie above 1. The comparator is near 0 for SELF and near 1 for all other conditions. The no-change predictor is exactly 1 everywhere.

**Figure 3.** How surprising is the same lamp change, depending on its cause? Relative prediction error of the distal heat prediction at the lamp change (0 = fully predicted; 1 = no better than predicting no change; symmetric-log axis). The hand-built COMPARATOR predicts only self-caused changes. Trained FULL agents behave like the NO-CHANGE predictor in every condition: they do not anticipate lamp changes at all.

**Validity checks.** All three checks came out as required:

- *V1 passed*: UNTRAINED networks met no hypothesis in 4 or more of 5 runs. Random networks did, however, produce "significant" single-run effects in 3 of 15 hypothesis tests, which shows why a multi-run pass rule is necessary.
- *V2 passed*: COMPARATOR relPE was 0.004 for SELF against 1.030 for SPONT, an H1 effect of +1.026 [1.011, 1.040]. It met H2, and self-blinding raised its relPE for SELF to 0.924, the expected dissociation.
- *V3*: the POSITION RULE attributed every OTHER-ONPAD and SPONT-ONPAD change to itself (accuracy 0.00 on both), so a position shortcut fails the dissociation trials.

::figure Figure4 | Four forest plots, one per hypothesis, with one row per run. Rows for FULL, NOEFF, NOFWD, UNTRAINED and COMPARATOR show effect estimates with 95 percent confidence intervals. Only the comparator lies clearly on the predicted side for H1, H2 and H3a; FULL intervals all include zero.

**Figure 4.** Pre-registered effects per run (95% bootstrap intervals; positive = predicted direction; filled markers count toward the verdict, that is, the interval excludes 0 and the run is gated and applicable; symmetric-log axes). FULL intervals include 0 for every hypothesis. A few untrained and NOFWD runs show isolated "significant" effects, which the 4-of-5 rule absorbs.

**Why no self-prediction?** An ecological check suggests that self-caused lamp changes were almost absent from the agents' experience. In 250 free-running episodes (50 per FULL run), the agents entered the pad 26 times, against 1,378 entries by the other robot and 638 spontaneous toggles. A strategy analysis (20 episodes per run) showed that the surviving agents did 94–96% of their charging while the lamp was off, and waited near the charger while it was on. They had learned to let the other robot and chance switch the lamp for them, and toggled it themselves only 0.00–0.20 times per episode on average. With lamp changes on fewer than 1% of time steps, and self-caused ones rarer still, a next-observation loss averaged over all channels gives little pressure to model them.

**Tests expected to be fooled (T1 and probes).** In T1, the share of prediction error that fell on the body channels after an internal shock was 0.96 for NO-CHANGE and 0.86 for FULL, against 0.00–0.08 after world events. Because the body has dedicated interoceptive channels, a predictor that knows nothing separates body events from world events. FULL agents' behaviour after the events did not differ by condition: they moved 4.97–4.99 m toward the charger in the following 5 s. Linear probes decoded "who caused the lamp change" with 100% accuracy at every lag from 1 to 40 steps. They did so from trained FULL agents, from UNTRAINED networks and from the raw input alike (Figure 6). Event type was decoded at 0.59–0.74 by all three feature sets, where chance was 0.33. Decodability therefore gave no evidence beyond what the raw input already contained.

::figure Figure6 | Two line plots of cross-validated decoding accuracy against memory lag. Left: who caused the lamp change, decoded at 1.0 at lags 1, 10 and 40 by FULL agents, untrained networks and raw input alike. Right: what happened (world, body or nothing), decoded at about 0.6 to 0.75 by all three feature sets; chance is one third.

**Figure 6.** Exploratory probes. Left: the cause of a lamp change is decodable at ceiling from trained agents, untrained networks and raw input alike. Right: event type is decoded similarly well by all feature sets. Decodable information is present in the input and is not evidence of a self-model.

**Exploratory analysis (not pre-registered).** Although the agents did not anticipate lamp changes, their distal heat predictions while walking with no lamp change depended specifically on self-motion signals. Self-blinding increased their prediction error in 4 of 5 FULL runs (for example, from 1.66 to 2.50 times the no-change error), whereas other-blinding had no effect (1.66 to 1.66). The predictions were nevertheless poor in absolute terms: they stayed above the no-change error, with ratios of 1.47–3.11. This hints at a self-motion–dependent but inaccurate model of reafference. We treat it as hypothesis-generating only.

## 3.3 Sensitivity of the agency test (post-hoc)

Blending a small fraction of the comparator into each agent's heat predictions was enough to meet the pre-registered rule (Table 5, Figure 5). At w = 0.02, that is, anticipating about 2% of a self-caused change, H1 and H3a were met in 4 of 5 runs. The fifth run, FULL seed 4, failed the competence gate and never counts. From w = 0.1, H2 was also met. Conversely, every real FULL run's H1 interval lay below +0.016. Since the effect grew by about 1.9 per unit of w at small w, this bound corresponds to w ≈ 0.008. The Study 2 null result is therefore informative at this resolution: the trained agents anticipated less than about 1% of self-caused lamp changes, below the smallest effect the test was shown to detect.

**Table 5.** Post-hoc sensitivity analysis: runs meeting each hypothesis when a fraction w of the comparator's heat prediction is blended into each trained FULL agent (pass rule: 4 of 5; the gated-out FULL seed 4 never counts).

| Blend weight w | Mean H1 effect | H1 runs | H2 runs | H3a runs | H1 supported? |
|---|---|---|---|---|---|
| 0 (the actual agents) | −0.002 | 0/5 | 0/5 | 0/5 | no |
| 0.02 | +0.038 | 4/5 | 1/5 | 4/5 | yes |
| 0.05 | +0.097 | 4/5 | 1/5 | 4/5 | yes |
| 0.10 | +0.190 | 4/5 | 4/5 | 4/5 | yes |
| 0.25 | +0.441 | 4/5 | 4/5 | 4/5 | yes |
| 0.50 | +0.760 | 4/5 | 4/5 | 4/5 | yes |

::figure Figure5 | Two line plots against blend weight on a symmetric-log axis. Left: the H1 effect for each of five runs rises from about 0 at w equals 0 to about 0.76 at w equals 0.5, crossing the largest confidence bound observed in the real data already at w equals 0.02. Right: the number of runs meeting H1, H2 and H3a; H1 and H3a reach 4 of 5 at w equals 0.02, H2 at w equals 0.1.

**Figure 5.** Sensitivity of the pre-registered agency test (post-hoc). Left: H1 effect as a function of the blend weight w, one line per FULL run; the horizontal line marks the largest upper confidence bound in the real data (+0.016). Right: number of runs meeting each hypothesis; the pass rule requires 4 of 5 (horizontal line).

## 3.4 Study 2b: the agents did not discover the necessary action

The manipulation check failed. Self-caused toggles per free-running episode were 0.00, 0.04, 0.22, 0.90 and 0.04 across the five FULL runs, and no run reached the pre-registered 1.0 (Table 6). All five FULL runs also failed the competence gate, with forward-model errors of 0.99–1.35 times that of NO-CHANGE. Only two agents survived any held-out episodes. A strategy analysis showed three distinct outcomes:

- three agents never learned to charge and died in all 20 strategy episodes;
- two charged almost only while the lamp was off (95–96% of charging time);
- only one of those two regularly used the switch.

As registered, the hypotheses were evaluated regardless: H1–H3 were each met in 0 of 5 FULL runs, and V1–V3 again passed. Ignoring the gate, the sensitivity analysis again detected a 2% blend in 5 of 5 runs, and the agents' H1 intervals lay below +0.033. The Study 2 exploratory observation that distal predictions depend on self-motion signals did not replicate consistently.

**Table 6.** Study 2b FULL runs (world agency_b): competence, survival, the manipulation check M1 and the H1 effect (mean [95% CI]).

| Run | Forward error / NO-CHANGE | Survived 60 s | Self-caused toggles per episode (M1 needs ≥ 1) | H1 effect |
|---|---|---|---|---|
| FULL seed 0 | 1.01 | 0.00 | 0.00 | −0.003 [−0.013, 0.007] |
| FULL seed 1 | 1.13 | 0.00 | 0.04 | −0.002 [−0.037, 0.033] |
| FULL seed 2 | 1.16 | 0.55 | 0.22 | −0.005 [−0.012, 0.001] |
| FULL seed 3 | 1.35 | 0.50 | 0.90 | +0.003 [−0.024, 0.031] |
| FULL seed 4 | 0.99 | 0.00 | 0.04 | −0.002 [−0.031, 0.026] |

## 3.5 Study 1b: the learners settled into doing nothing

The trade-off marker did not separate the learners from the reflexes (Q1). The trade-off score was 0.00 [0.00, 0.00] in all five seeds, because the learners never crossed the heat wall and never reached the charger in the trade-off world. Sensitization was not estimable (Q3), because the learners were almost never harmed: no episode contained encounters both before and after harm. Anticipation rates were 0.00–0.60, based on only 2–5 encounters per seed. No learner survived a single 90 s foraging episode, and none ever reached the charger.

The trajectories (Figure 7) show why. The learners walked away from the charger to the far wall and waited there until their energy ran out, with lifetimes of 74–81 s of the 90 s episode. Their exploration noise had shrunk to a standard deviation of about 0.1, and in an exploratory check the stochastic training policy behaved in the same way as the deterministic one. Within the fixed training budget, the learners converged on a local optimum: by moving little they reduced both energy expenditure and the risk of heat damage.

::figure Figure7 | Five panels, one per learned seed, each showing five trajectories in the foraging world. Trajectories lead away from the charger in the upper right to the bottom or left wall, where most end in a cross marking death.

**Figure 7.** Study 1b: the first five foraging episodes of each learning agent (deterministic policy). Circles mark starts and crosses deaths. The agents move away from the charger (upper right) to the far wall and wait there until their energy runs out.

## 3.6 Additional methodological findings

**Test worlds must be verified, not assumed.** The trade-off world, as first specified in the design brief, did not pose a trade-off. At top speed, crossing the heat wall cost only 0.007 damage. Moreover, the supposedly impossible detour was survivable at the lowest start energy, where a scripted agent arrived at the charger with 0.041 energy to spare. We therefore changed the wall from 58 °C with σ = 0.35 m to 60 °C with σ = 0.5 m, and the lowest start energy from 0.15 to 0.08. Both changes were verified analytically and with scripted runs in the physics engine before any marker was measured (Supplementary Material, Section S5).

**Worlds must make the tested capacity useful.** The Study 2 agents' failure to use the switch was not a quirk of learning. The scripted design check showed that switching was not worth it in that world (−0.04 [−0.09, +0.01]). A test of whether an agent predicts the consequences of its own actions presupposes that acting pays. This condition can and should be checked before training.

**Control agents must be competent.** As first specified, the withdrawal reflex reversed its *commanded* heading on every trigger. It therefore oscillated inside heat sources until it died: all 28 of its deaths in 30 episodes were from damage. A control that fails in this way makes markers look more discriminating than they are. We used a memoryless fix, which reverses the *actual* direction of motion and keeps escaping while the heat is falling, and we report both versions in the repository.

# 4 Discussion

**Markers must be benchmarked against minimal mechanisms.** Across our studies, the markers most readily proposed as accessible evidence of richer processing were met by trivial mechanisms:

- anticipatory avoidance, by a one-step thermotactic reflex;
- body-versus-world discrimination, by a predictor that expects nothing to change, because the body has dedicated interoceptive channels;
- "self/other" information in internal states, by untrained networks and by the raw input.

A fourth marker, sensitization, was biased toward a positive value in agents that have no memory at all. None of this shows that anticipation, interoception or internal representations are irrelevant to sentience or self-awareness. It shows that such observations carry no evidential weight unless minimal mechanisms fail them. This is a concrete, testable form of the gaming problem (Birch, 2024). Artificial life is well placed to test it, because the minimal mechanism can be built, run through exactly the same battery, and inspected. We suggest that any proposal to use a behavioural or decoding marker as evidence about an artificial system should report the marker's performance on reflex, random and untrained controls matched to the system's sensors and body.

The two markers that no reflex passed, motivational trade-off and like-for-like sensitization, are the ones that require an agent to weigh its internal state against an external cost, or to change its policy as a result of experience. They are therefore the more promising candidates, and our design check shows how to make the trade-off genuine. However, no learning agent in our hands produced them either (Study 1b), so we cannot yet say whether they discriminate architectures in the positive direction.

**Tests can be made robust.** The pre-registered agency test was not fooled:

- it detected a known comparator mechanism;
- it rejected random networks;
- it exposed a position shortcut;
- it would have detected an agent that anticipated about 2% of its self-caused changes.

Its dissociation logic, freezing self-motion signals versus other-agent signals, provides causal rather than merely correlational evidence about which signals a prediction depends on. This matters because decoding, the most common way of looking for "self" information in networks, failed badly here: the cause of a lamp change was decodable at ceiling from networks that had never been trained. A prediction-based test with ablations and matched controls asks what the system uses, not merely what is present in its states.

**The limiting factor was the learners, not the tests.** Survival training plus a generic next-observation loss produced agents that failed in three distinct ways:

- in Study 2 they *free-rode*, letting the other robot and chance change the world for them;
- in Study 2b they *failed to discover* a necessary action;
- in Study 1b they *settled into doing nothing* until they starved.

In none of these cases did the agents gather the experience from which a self-prediction could be learned. This is an ecological point as much as a computational one. A capacity to predict the consequences of one's own actions can be learned only by an agent that acts, in a world where acting makes a difference and often enough to be worth modelling. Our pre-registered negative results caution against assuming that self-models emerge "for free" from homeostatic training. They also suggest a specific order of work. First verify that the world makes the capacity useful, which is a cheap scripted check. Then verify that the learner exercises the capacity, which is a manipulation check. Only then test for the internal signature.

These results complement recent work in which homeostatic agents develop integrated behaviour (Yoshida, Daikoku, et al., 2024; Yoshida, Kanazawa, & Kuniyoshi, 2024) and in which behavioural observations of such an agent are weighed as evidence about affect (Solms et al., 2026). Our contribution is not a claim about what such agents can or cannot do in general. It is a set of tools and controls that makes such claims testable, and a demonstration of how easily several standard observations can be produced without the capacity they are taken to indicate.

**What would count as a positive result?** Under our pre-registered criteria, a learning agent would show a functional self/other distinction if four conditions held together, in at least four of five independently trained runs that pass the competence gate and the manipulation check. It would have to:

- predict self-caused changes better than spontaneous ones (H1);
- register surprise when an expected self-caused change fails to occur (H2);
- lose this advantage specifically when its self-motion signals are frozen (H3a);
- predict other-caused changes from the other agent's signals (H3b).

Each element rules out a different shortcut. H1 alone could reflect position, and H2 alone could reflect a generic expectation that something changes after movement. H3a and H3b establish which signals the prediction depends on. Even this full pattern would be evidence of a comparator-like mechanism, and the hand-built positive control shows that such a mechanism can be implemented in a few lines of code. It would not by itself be evidence of self-awareness in any richer sense. This illustrates the general point: the more precisely a marker is specified, the more clearly one can see which minimal mechanism would satisfy it, and hence what further evidence is needed.

**Beyond embodied agents.** The same logic applies to other kinds of artificial system. Keeling et al. (2024) found that several large language models make threshold-like trade-offs between points and stipulated pain or pleasure in a text-based game. Our results do not bear directly on language models, whose behaviour is shaped by human-generated text rather than by homeostatic need. But they suggest how the evidential weight of such a finding could be assessed. One would construct minimal systems that could produce the same pattern, for example systems that map the stated stakes to choices without representing any internal state, and show that they fail the test.

**Paths to positive tests.** Positive tests of the markers now require learners that reliably forage, act on the world and model it. Candidate routes include longer training, curricula or exploration bonuses, prediction objectives that are not dominated by easily predicted channels, and agents with explicit world models. Each should be pre-registered separately and evaluated with the same validated battery, including the sensitivity analysis. The exploratory hint that distal predictions depend on self-motion signals (Study 2) did not replicate consistently in Study 2b, and should itself be tested prospectively.

**Scope.** All results are functional. Nothing here bears on whether any agent has subjective experience. Passing or failing these tests is evidence about mechanisms, not about feelings. Our claim is methodological: a marker that a minimal mechanism passes cannot, on its own, distinguish a system that has a capacity from one that does not.

**Limitations.** The body is a disc with no limbs, and each study used a single environment. Five training runs per variant and one fixed, untuned training budget were used, and our learners did not master that budget in Studies 1b and 2b. The other robot was scripted rather than learning. The forward model was trained with an unweighted mean-squared loss over all channels, which may have let easily predicted channels dominate. The pre-registrations were time-stamped in version control rather than on an independent registry. A different agent, objective or training budget could produce a different result, and our negative results about learners should be read as results about these learners.

# 5 Conclusion

Behavioural and decoding markers of sentience and self-awareness need to be benchmarked against minimal mechanisms before they are used as evidence. In a physics-simulated homeostatic agent, a memoryless reflex passed anticipatory avoidance perfectly. A standard sensitization metric was biased in agents without memory, and body/world and self/other "information" was available to trivial predictors and untrained networks. A pre-registered, prediction-based self/other test could be made valid and sensitive, with explicit positive, negative and shortcut controls. Generic homeostatic learning agents, however, did not acquire the capacity it measures, or even the experience needed to learn it. The code, pre-registrations, trained models and raw data are openly available, so that other agents can be run through the same validated battery.

# Use of Generative AI

::noindent In accordance with the *Artificial Life* policy on generative AI, we state that generative AI was used extensively in this work. The system was Claude Opus 5.5 (Anthropic, 2026; model identifier claude-opus-5-5; accessed through the Claude Code application at https://claude.ai, 22–23 September 2026). It was used for the following:

- writing the simulation, agent, training and analysis code from a specification written by the author(s);
- proposing elements of the experimental design, including the validity controls, the competence gate, the drafts of both pre-registration documents, the design checks and the post-hoc sensitivity analysis;
- running the experiments and analyses;
- producing all figures and tables;
- drafting the text of this article and of the Supplementary Material.

The research questions, the initial design brief and all decisions about what to run and report were the author(s)'. [FILL: Describe accurately and specifically what the author(s) personally checked. For example: which parts of the code were read and verified, whether the analyses were re-run independently, whether every number in the text was checked against the result files, and whether every reference was checked against its source.] The author(s) take full responsibility for the content of this article. Generative AI is not an author of this work.

# Acknowledgements

::noindent [FILL: Acknowledge people who helped but are not authors, or write "None."]

# Funding

::noindent [FILL: Name each funder and grant number, or write "This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors."]

# Competing Interests

::noindent [FILL: Declare any competing interests, or write "The author(s) declare no competing interests."]

# Author Contributions (CRediT)

::noindent [FILL: For each author, list their CRediT roles, for example: Conceptualization, Methodology, Software, Validation, Formal analysis, Investigation, Data curation, Writing – original draft, Writing – review & editing, Visualization, Supervision, Project administration, Funding acquisition. Contributions made with generative AI must be consistent with the section Use of Generative AI.]

# Data and Code Availability

::noindent All code, both pre-registration documents with their version-control history, the trained models, the raw trial data, the result tables and the scripts that regenerate every figure and table are openly available at [FILL: public repository URL] and archived at [FILL: Zenodo DOI], under the [FILL: licence, for example MIT for code and CC BY 4.0 for data] licence. The Supplementary Material lists the commands that reproduce each study.

# Ethics Statement

::noindent This study is entirely computational. It involved no human participants, no animals and no personal data, so ethical approval was not required.

# References

::refs
Anthropic. (2026). *Claude Opus 5.5* [Large language model]. https://claude.ai
Ashby, W. R. (1952). *Design for a brain*. Chapman & Hall.
Berg, H. C., & Brown, D. A. (1972). Chemotaxis in *Escherichia coli* analysed by three-dimensional tracking. *Nature*, *239*(5374), 500–504. https://doi.org/10.1038/239500a0
Birch, J. (2024). *The edge of sentience: Risk and precaution in humans, other animals, and AI*. Oxford University Press. https://doi.org/10.1093/9780191966729.001.0001
Birch, J., Burn, C., Schnell, A., Browning, H., & Crump, A. (2021). *Review of the evidence of sentience in cephalopod molluscs and decapod crustaceans*. LSE Consulting.
Blakemore, S.-J., Wolpert, D. M., & Frith, C. D. (1998). Central cancellation of self-produced tickle sensation. *Nature Neuroscience*, *1*(7), 635–640. https://doi.org/10.1038/2870
Bongard, J., Zykov, V., & Lipson, H. (2006). Resilient machines through continuous self-modeling. *Science*, *314*(5802), 1118–1121. https://doi.org/10.1126/science.1133687
Braitenberg, V. (1984). *Vehicles: Experiments in synthetic psychology*. MIT Press.
Butlin, P., Long, R., Elmoznino, E., Bengio, Y., Birch, J., Constant, A., Deane, G., Fleming, S. M., Frith, C., Ji, X., Kanai, R., Klein, C., Lindsay, G., Michel, M., Mudrik, L., Peters, M. A. K., Schwitzgebel, E., Simon, J., & VanRullen, R. (2023). *Consciousness in artificial intelligence: Insights from the science of consciousness* (arXiv:2308.08708). arXiv. https://doi.org/10.48550/arXiv.2308.08708
Caterina, M. J., Schumacher, M. A., Tominaga, M., Rosen, T. A., Levine, J. D., & Julius, D. (1997). The capsaicin receptor: A heat-activated ion channel in the pain pathway. *Nature*, *389*(6653), 816–824. https://doi.org/10.1038/39807
Cho, K., van Merriënboer, B., Gulcehre, C., Bahdanau, D., Bougares, F., Schwenk, H., & Bengio, Y. (2014). Learning phrase representations using RNN encoder–decoder for statistical machine translation. In *Proceedings of the 2014 Conference on Empirical Methods in Natural Language Processing* (pp. 1724–1734). Association for Computational Linguistics. https://doi.org/10.3115/v1/D14-1179
Efron, B., & Tibshirani, R. J. (1993). *An introduction to the bootstrap*. Chapman & Hall.
Elwood, R. W., & Appel, M. (2009). Pain experience in hermit crabs? *Animal Behaviour*, *77*(5), 1243–1246. https://doi.org/10.1016/j.anbehav.2009.01.028
Keeling, G., Street, W., Stachaczyk, M., Zakharova, D., Comsa, I. M., Sakovych, A., Logothetis, I., Zhang, Z., Agüera y Arcas, B., & Birch, J. (2024). *Can LLMs make trade-offs involving stipulated pain and pleasure states?* (arXiv:2411.02432). arXiv. https://doi.org/10.48550/arXiv.2411.02432
Keramati, M., & Gutkin, B. (2014). Homeostatic reinforcement learning for integrating reward collection and physiological stability. *eLife*, *3*, e04811. https://doi.org/10.7554/eLife.04811
Man, K., & Damasio, A. (2019). Homeostasis and soft robotics in the design of feeling machines. *Nature Machine Intelligence*, *1*(10), 446–452. https://doi.org/10.1038/s42256-019-0103-7
Schulman, J., Moritz, P., Levine, S., Jordan, M., & Abbeel, P. (2016). High-dimensional continuous control using generalized advantage estimation. In *Proceedings of the 4th International Conference on Learning Representations*. https://doi.org/10.48550/arXiv.1506.02438
Schulman, J., Wolski, F., Dhariwal, P., Radford, A., & Klimov, O. (2017). *Proximal policy optimization algorithms* (arXiv:1707.06347). arXiv. https://doi.org/10.48550/arXiv.1707.06347
Sneddon, L. U., Elwood, R. W., Adamo, S. A., & Leach, M. C. (2014). Defining and assessing animal pain. *Animal Behaviour*, *97*, 201–212. https://doi.org/10.1016/j.anbehav.2014.09.007
Solms, M., Grimbly, S. J., Bassett, B., Boonstra, E., Hodson, R., Kuske, N., Mahadew, K., Rosman, B., van Hoof, C., & Shock, J. (2026). Inferring affective consciousness in an artificial agent: A case study. *Journal of Consciousness Studies*, *33*(7–8), 14–34.
Todorov, E., Erez, T., & Tassa, Y. (2012). MuJoCo: A physics engine for model-based control. In *2012 IEEE/RSJ International Conference on Intelligent Robots and Systems* (pp. 5026–5033). IEEE. https://doi.org/10.1109/IROS.2012.6386109
Towers, M., Kwiatkowski, A., Terry, J., Balis, J. U., De Cola, G., Deleu, T., Goulão, M., Kallinteris, A., Krimmel, M., KG, A., Perez-Vicente, R., Pierré, A., Schulhoff, S., Tai, J. J., Tan, H., & Younis, O. G. (2024). *Gymnasium: A standard interface for reinforcement learning environments* (arXiv:2407.17032). arXiv. https://doi.org/10.48550/arXiv.2407.17032
von Holst, E., & Mittelstaedt, H. (1950). Das Reafferenzprinzip: Wechselwirkungen zwischen Zentralnervensystem und Peripherie. *Naturwissenschaften*, *37*(20), 464–476. https://doi.org/10.1007/BF00622503
Wilson, E. B. (1927). Probable inference, the law of succession, and statistical inference. *Journal of the American Statistical Association*, *22*(158), 209–212. https://doi.org/10.1080/01621459.1927.10502953
Wittenburg, N., & Baumeister, R. (1999). Thermal avoidance in *Caenorhabditis elegans*: An approach to the study of nociception. *Proceedings of the National Academy of Sciences*, *96*(18), 10477–10482. https://doi.org/10.1073/pnas.96.18.10477
Yoshida, N., Daikoku, T., Nagai, Y., & Kuniyoshi, Y. (2024). Emergence of integrated behaviors through direct optimization for homeostasis. *Neural Networks*, *177*, Article 106379. https://doi.org/10.1016/j.neunet.2024.106379
Yoshida, N., Kanazawa, H., & Kuniyoshi, Y. (2024). *Synthesising integrated robot behaviour through reinforcement learning for homeostasis* [Preprint]. bioRxiv. https://doi.org/10.1101/2024.06.03.597087
::endrefs
