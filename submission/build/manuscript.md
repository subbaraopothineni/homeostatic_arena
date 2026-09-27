::title Behavioural Markers of Sentience Are Met by Minimal Mechanisms: Validated and Pre-Registered Tests With Homeostatic Agents

::center [FILL: Author One]¹ and [FILL: Author Two]²

::center ¹ [FILL: Department, Institution, City, Country]

::center ² [FILL: Department, Institution, City, Country — delete this line if there is a single author]

::center **Corresponding author:** [FILL: name, postal address, e-mail address]

::center **ORCID:** [FILL: 0000-0000-0000-0000 for each author]

::center **Article type:** Article · **Main text:** {{WORDCOUNT}} words (Introduction to Conclusion; excluding tables, figure captions and references) · 7 figures · 7 tables

::center **Keywords:** sentience markers, sense of agency, homeostatic reinforcement learning, comparator model, pre-registration, minimal mechanisms

::center **Generative-AI disclosure:** Generative AI (Claude Opus 5.5, Anthropic) was used for code, analysis, figures and drafting of this article. The nature and extent of that use are stated in the section *Use of Generative AI* and cited as Anthropic (2026).

::pagebreak

# Abstract

::noindent Behavioural markers are increasingly proposed as evidence of sentience in non-human systems, including artificial agents. A marker is informative only if simpler mechanisms cannot produce it. We tested four behavioural markers adapted from animal-sentience frameworks, and a comparator-based test of the sense of agency, in a physics-simulated agent whose only learning signal is the reduction of homeostatic drive. Every behavioural marker was met by a mechanism with at most one bit of memory. A memoryless thermotactic reflex left every heat encounter before its nociceptor fired. A reflex whose withdrawal is vetoed by critically low energy accepted a noxious route only when in need. A reflex with one bit of state became more cautious after harm (−3.2 °C). A standard trade-off score missed that genuine trade-off because need changed within a trial, and a standard sensitization metric was biased by about +9 °C. A pre-registered study asked whether recurrent agents trained with a self-supervised forward model predict self-caused sensory changes better than identical changes with other causes. Positive, negative and shortcut controls validated the test, which detected a self-model contributing 2–25% of the prediction, depending on its timing precision. No trained agent supported any hypothesis: their forward models did not predict the relevant channels at all, and they had learned to let another agent operate the switch. Two further pre-registered studies were inconclusive: the learners never acquired the relevant behaviour. Behavioural markers of sentience must be benchmarked against minimal mechanisms; prediction-based agency tests can be made valid but require competent learners.

::pagebreak

# 1 Introduction

How could we tell whether a non-human system has states that matter to it? Animal-welfare science approaches this question with a set of neural and behavioural criteria. Birch et al. (2021) list eight: nociception, sensory integration, integrated nociception, analgesia, motivational trade-offs, flexible self-protection, associative learning, and a preference for analgesia when injured. They weigh the evidence for each criterion and combine it into graded confidence levels (see also Sneddon et al., 2014; Crump et al., 2022). A hermit crab that tolerates a stronger electric shock before leaving a higher-quality shell is making a motivational trade-off (Elwood & Appel, 2009). These frameworks were built for animals, where they have informed legislation. They are now being discussed as sources of evidence about artificial systems (Butlin et al., 2023; Birch, 2024; Keeling et al., 2024).

A behavioural marker is only as good as its ability to exclude simpler explanations. Birch (2024) calls the corresponding difficulty for artificial intelligence the *gaming problem*: a system can be built or trained to produce the behaviour that a marker looks for without having the capacity the marker is meant to indicate. For animals, one cannot build the simplest mechanism that could produce a marker and check whether it passes. For artificial agents one can, which makes artificial life a natural setting for a question that is usually argued rather than tested: *which markers can be met by mechanisms that nobody would regard as candidates for sentience?* Artificial life has a long tradition of using minimal agents to show how little machinery a seemingly rich behaviour requires (Braitenberg, 1984; Beer, 1996). It has studied homeostatic adaptation (Di Paolo, 2000) and agents whose behaviour is coupled to their own metabolism (Egbert et al., 2012). It has also examined what it takes for a system to count as an agent at all (Barandiaran et al., 2009). Here we apply the same synthetic logic to the markers themselves.

We use homeostatic agents because they have something at stake. Following Ashby's (1952) homeostat and more recent proposals for "feeling machines" (Man & Damasio, 2019), several authors have argued that systems that must regulate internal variables to persist are the right substrate in which to look for functional analogues of affect. In homeostatic reinforcement learning, reward is defined only as a reduction of the distance between internal variables and their set points (Keramati & Gutkin, 2014). Agents trained this way can develop integrated foraging and avoidance behaviour without any task reward (Yoshida, Daikoku, et al., 2024; Yoshida, Kanazawa, & Kuniyoshi, 2024). A recent case study has asked what could be inferred about affective consciousness in such an agent (Solms et al., 2026). Homeostatic agents are therefore plausible candidates for marker-based assessment, and they are fully inspectable.

The second capacity we examine is the *sense of agency*: registering that one is the cause of a change. According to the reafference principle, organisms predict the sensory consequences of their own movements and compare the prediction with what they sense (von Holst & Mittelstaedt, 1950). Self-produced stimuli are predicted and attenuated, which is why one cannot tickle oneself (Blakemore et al., 1998). The comparator account holds that this prediction underlies the feeling of agency, although the judgement that one caused an event draws on further cues (Synofzik et al., 2008). A functional marker follows from this account. An agent that models its own agency should predict a sensory change better when it caused the change than when an identical change had another cause. Unlike simple avoidance, this marker makes specific predictions about internal processing that can be tested with ablations. But it too can be gamed:
- a system can "know" that it caused a change simply because it is standing where changes happen;
- body-related and world-related events can be separated by the input channels they arrive on, without any self-model;
- the cause of an event can be decoded from internal states simply because it is present in the raw input.

A test for a marker should therefore itself be tested. We borrow three kinds of control from experimental practice:
- a *positive control*: a mechanism known to have the capacity, built by hand. If the test cannot detect it, a negative result is uninformative.
- a *negative control*: a system known to lack the capacity, such as a network with random weights. If it passes, the test has been fooled.
- a *shortcut control*: the most obvious way of passing without the capacity. The test should contain trials on which the shortcut fails.

To these we add a sensitivity analysis, which asks how weak a real effect could be and still be detected. A null result can then be read as evidence of absence at a stated resolution rather than as mere absence of evidence. None of these elements is new on its own, but we are not aware of previous work that combines them to validate a marker of sentience or agency in artificial agents.

We report four studies:
- **Study 1** applies four behavioural markers to hard-wired reflex agents, and to minimal variants with one extra rule or one bit of state.
- **Study 2** (pre-registered) tests whether recurrent agents trained with a self-supervised forward model predict self-caused changes better than changes caused by another agent or by chance.
- **Study 2b** (pre-registered) repeats Study 2 in a world where acting is necessary.
- **Study 1b** (pre-registered) applies the Study 1 markers to learning agents.

Our contributions are:

1. an open, physics-based test bed with functional analogues of nociception, tissue damage, energy and homeostatic drive;
2. evidence that each behavioural marker tested is met by a mechanism with at most one bit of memory, together with two measurement pitfalls: a trade-off score confounded by within-trial changes of need, and a biased sensitization metric;
3. a pre-registered test of the sense of agency whose validity and sensitivity are demonstrated with explicit controls, including a self-model with imperfect timing;
4. three pre-registered negative results showing that generic homeostatic learners did not acquire, or even gather the experience needed for, the capacity the test measures;
5. methodological lessons for building test worlds, controls and competence checks.

All measurements are functional. Nothing in this article bears on whether any of the agents has subjective experience; the question is which observations could count as evidence at all.

# 2 Methods

## 2.1 Body, physiology and environment

All studies share one simulated body and physiology (Table 1), implemented with MuJoCo 3 (Todorov et al., 2012) behind a Gymnasium interface (Towers et al., 2024). The agent is a disc (radius 0.25 m, mass 1 kg) that moves on two damped slide joints in a 10 × 10 m walled arena. Its two-dimensional action sets the force on the body; the control step is 0.05 s and the terminal speed 2 m/s.

The physiology consists of functional analogues only:
- *Ambient temperature* at any point is the room temperature (25 °C) plus the largest Gaussian rise contributed by any heat source.
- *Skin temperature* follows ambient temperature with a first-order lag.
- A logistic *nociceptor* signal is half-maximal at a skin temperature of 45 °C, loosely following the activation threshold of the TRPV1 heat receptor (Caterina et al., 1997).
- *Tissue damage* accrues above 45 °C and heals slowly below it.
- *Energy* drains at a basal rate plus a motor cost, and recharges on a charger.

The agent dies when damage reaches 1 or energy reaches 0.

The homeostatic drive is the weighted distance of the internal state from its set points, D = √((1 − energy)² + 2 · damage²). The only reward is the step-to-step reduction in drive, r(t) = D(t − 1) − D(t), with −1 on death (Keramati & Gutkin, 2014). There is no task reward: the agent is never rewarded for reaching the charger or avoiding heat as such, only for reducing its drive.

The base observation has 11 channels:
- position and velocity (proprioception);
- ambient and skin temperature;
- nociceptor activation;
- a charger "beacon" that decays exponentially with distance (analogous to a chemical gradient);
- touch;
- energy and damage (interoception).

Studies 2 and 2b add further senses, described below.

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

## 2.2 Study 1: behavioural markers versus minimal mechanisms

Study 1 was specified in a design brief before any code was written, but it was not formally pre-registered. The two minimal controls and the decision-time analysis described at the end of this section were added after all pre-registered studies were complete, and are labelled post hoc throughout.

**Worlds.**
- *Foraging world* (Figure 1a): the agent starts at a random cool location at least 2 m from a charger. It must reach the charger past two heat sources (60 °C peak, σ = 0.7 m) within a 90 s episode.
- *Trade-off world* (Figure 1b): a heat wall (60 °C, σ = 0.5 m, 6.6 m long) lies between the start and the charger. The charger can be reached either directly through the wall or by a longer detour around its end.

::figure Figure1 | Three square arenas shown as temperature maps. Left: the foraging world with two circular heat sources and a charger in the upper right. Middle: the trade-off world with a vertical heat wall between the start on the left and the charger on the right; a solid arrow shows the short route through the wall and a dashed arrow the long route around it. Right: the agency world with a static heat source, a lamp at the charger in the upper right, and a switch pad at the centre approached by the agent from the left in SELF trials and by the other robot from the right in OTHER trials.

**Figure 1.** The three worlds. (a) Foraging world (Studies 1 and 1b): two heat sources and a charger. (b) Trade-off world (Studies 1 and 1b): the charger is reached either through a heat wall or by a longer detour around it; the correct choice depends on the agent's energy. (c) Agency world (Studies 2 and 2b), shown with the lamp on: a switchable heat lamp sits on the charger, and any robot entering the switch pad toggles the lamp. The two robots show the start positions and directions of the scripted SELF and OTHER test trials, which in the experiment occur in separate trials. Colour: ambient temperature.

**Baseline agents.** Three agents without learning served as baselines.
- The *random walker* moves at constant action magnitude (0.6) along a heading that performs a random walk (standard deviation 0.3 rad per step).
- The *nociceptive reflex* withdraws when its nociceptor exceeds 0.1.
- The *thermotactic reflex* also withdraws when the ambient temperature is above 35 °C and rising. This one-step comparison is analogous to the thermotaxis of *Caenorhabditis elegans* (Wittenburg & Baumeister, 1999).

When energy is below 0.6, both reflexes forage by run-and-tumble on the beacon, as in bacterial chemotaxis (Berg & Brown, 1972). Withdrawal reverses the actual direction of motion and continues while the heat is falling (see Section 3.6 for why this matters). None of these agents stores anything beyond the previous time step.

**Markers.** We operationalized four behavioural markers. Table 2 maps each to the published criteria.

1. *Survival*: the fraction of 90 s foraging episodes survived.
2. *Anticipatory avoidance*: a heat encounter begins when ambient temperature rises above 38 °C and ends when it falls below 35 °C. An encounter counts as anticipated if the agent leaves it before the nociceptor exceeds 0.5. The score is the per-episode fraction of anticipated encounters.
3. *Motivational trade-off* (after Elwood & Appel, 2009): the agent starts in the trade-off world with energy 0.08, 0.3, 0.5 or 0.9.
   - The pre-specified score is the rate of full crossings of the wall at the lowest start energy minus the rate at the highest.
   - A positive score means that the agent accepts the noxious short route only when in need.
   - The world was designed so that, at energy 0.08, only the direct route is survivable; this was verified before use (Section 3.6).
4. *Sensitization*: the mean peak ambient temperature of encounters after the first harmful encounter (nociceptor > 0.5), minus that of encounters before it. A negative value means the agent became more cautious after harm. Every encounter before the first harmful one is non-harmful by construction, so we also computed a like-for-like variant that compares non-harmful encounters on both sides.

**Table 2.** How the behavioural tests relate to the published sentience criteria (Birch et al., 2021; Crump et al., 2022).

| Test in this study | Closest published criterion | Difference |
|---|---|---|
| Anticipatory avoidance | None directly; it is the unlearned part of avoidance. Criterion 7 (associative learning) requires *learned* avoidance | Tests unlearned avoidance only |
| Motivational trade-off | Criterion 5, motivational trade-offs | The cost is weighed against internal need rather than an external reward |
| Sensitization | Changed responses after injury (Sneddon et al., 2014); a non-associative form of learning, weaker than criterion 7 | Non-associative |
| Survival | None; a competence check | — |
| Not tested behaviourally | Criteria 1–4 and 8 (nociceptors, integrative regions and pathways, analgesia, analgesia preference); criterion 6 (flexible self-protection of an injured part) | Criterion 1 is met by construction in every agent here, including the random walker |

**Minimal controls (post hoc).** The plain reflexes were never designed to attempt the trade-off or sensitization markers, so their failure on those markers is uninformative. We therefore added one minimal control for each marker, each consisting of a reflex plus exactly one element.
- The *motivational reflex* is the thermotactic reflex with its withdrawal vetoed while energy is below 0.2. This adds a single threshold on an interoceptive channel and no memory.
- The *sensitizing reflex* is the nociceptive reflex plus one bit of state, set by the first harmful stimulus (nociceptor > 0.5) and kept for the rest of the episode. While the bit is set, the agent also withdraws when ambient temperature is above 35 °C and rising. Harm thus lowers its withdrawal threshold, a form of non-associative sensitization.

Both controls were run through the unchanged marker battery with the same episode seeds as the baselines.

**Trade-off at the moment of decision (post hoc).** The pre-specified trade-off score compares start energies, but energy drains during the 90 s episode. An agent that starts with high energy can therefore be in need later and cross then. We therefore also scored each approach to the wall from the start side:
- an approach begins when ambient temperature rises above 38 °C with the agent west of the wall;
- for each approach we recorded the agent's energy at its start and whether the agent crossed through the wall during it.

The trade-off signature is a negative logistic slope of crossing on energy, with a 95% confidence interval from a bootstrap over episodes (2,000 resamples). This analysis used 100 seeds per start energy.

**Statistics.** Each condition used 30 episode seeds, and a robustness run used 100. Proportions are reported with Wilson score intervals (Wilson, 1927). Means and differences of means use percentile bootstrap intervals with 2,000 resamples over episodes (Efron & Tibshirani, 1993). All intervals are 95%.

## 2.3 Study 2: the sense of agency (pre-registered)

**Pre-registration.** The hypotheses, controls, test conditions, pass rules and training budget were committed to the project's version-control history before any Study 2 code or data existed (commit `d70a2fe`, 22 September 2026). The document is reproduced in the Supplementary Material, Section S1. This is not a registration on an independent registry. Git timestamps are set by the author, so we make the complete history public for inspection. Deviations are listed in the document's append-only deviations section.

**Agency world.** The Study 1 arena was extended (Figure 1c) with:

- a switchable heat lamp at the charger (60 °C, σ = 0.7 m), so that the lamp makes the charger harmful while it is on;
- a switch pad (radius 0.5 m) at the centre of the arena that toggles the lamp whenever any robot's centre enters it;
- a second, scripted robot that moves at 0.6 m/s toward a target; on arrival it chooses the pad with probability 0.5 and otherwise a random point;
- spontaneous lamp toggles (a Poisson process with a rate of 1/20 s⁻¹);
- internal metabolic shocks that remove 0.1 energy (rate 1/30 s⁻¹).

Episodes lasted 60 s, the start energy was drawn from U(0.4, 1.0), and the lamp was on at the start with probability 0.5. The agent also had additional senses, for 26 observation channels in total:
- its previous motor command (efference copy);
- its previous reward;
- an eight-sector distal heat sense (radiant heat from each direction, decaying with distance);
- a floor sense that signals whether it is on the pad;
- the other robot's relative position when visible.

The simulator records the true cause of every event, but the agent never observes it.

**Learning agent (FULL).**
- *Architecture:* a two-layer MLP encoder (tanh) feeds a gated recurrent unit (GRU; Cho et al., 2014) with 128 units. The GRU state feeds a Gaussian policy and a value head.
- *Forward model:* a separate two-layer MLP head predicts the change in the next observation from the GRU state and the current motor command.
- *Training objective:* proximal policy optimization (PPO; Schulman et al., 2017) with generalized advantage estimation (Schulman et al., 2016) on the drive-reduction reward, plus a self-supervised mean-squared next-observation loss with weight 1.
- *Training settings:* 3 × 10⁶ environment steps per run, 16 parallel environments, rollouts of 128 steps, learning rate 3 × 10⁻⁴, discount 0.99, GAE λ 0.95, clip range 0.2, four epochs of four minibatches, entropy coefficient 0.001, reward scale 10.

No hyperparameter was tuned on any test, and the agent never received labels about what caused an event.

**Variants and controls.**

- *NOEFF*: FULL without the efference copy (3 seeds).
- *NOFWD*: FULL without the forward-model loss, so that its prediction head is untrained (3 seeds).
- *UNTRAINED*: FULL architecture with random weights (5 seeds), the negative control.
- *NO-CHANGE*: a predictor that expects the next observation to equal the current one.
- *COMPARATOR*: a hand-built positive control. It uses the known dynamics of its own body to predict a lamp toggle exactly when its own motion will carry it onto the pad.
- *POSITION RULE*: a shortcut that attributes any lamp change to itself if it is standing on the pad.
- The Study 1 thermotactic reflex served as a behavioural baseline.

**Competence gate.** Before testing, each trained run was evaluated on 20 held-out free-running episodes. A run passed the gate if its forward-model mean-squared error, averaged over all 26 channels, was at most 0.8 times that of NO-CHANGE. Runs failing the gate count as not supporting any hypothesis. After the pre-registered analysis, we also computed the same ratio on the eight heat channels that the test scores (post hoc; same episodes).

**Test T2 (agency).** In scripted trials, both robots are driven with forced actions and random events are disabled. Each condition therefore presents the same sensory situation while the cause of the lamp change differs (Table 3). The protocol was:
- 40 trials per condition and run, 20 with the lamp initially on and 20 off;
- energy 0.9 at the start of each trial, and start positions jittered uniformly by up to ±0.1 m in each coordinate;
- both robots stood still for 1 s (20 steps), then moved along the horizontal axis with a forced action of magnitude 0.8 until the lamp changed, and stood still again for up to 41 steps;
- in SPONT and NOEVENT trials, the event (or its absence) was timed to step 32, the median step at which the agent entered the pad in SELF trials, so that it followed the same amount of motion.

Throughout, the network runs normally and receives its observations, including the efference copy of the forced action. The measure is the relative prediction error of the forward model on the eight distal heat channels at the step of the lamp change:

::center relPE = Σₖ (ôₖ(t + 1) − oₖ(t + 1))² / Σₖ (oₖ(t) − oₖ(t + 1))²

::noindent where ô is the prediction and o the observation. A relPE of 0 means the change was fully predicted; 1 means the prediction was no better than expecting no change. The absolute error absPE is the numerator alone and is used where no change occurs. Test-time ablations freeze one group of channels at their values at the start of motion:
- *self-blind* freezes the self-motion channels (position, velocity, efference copy and pad sense);
- *other-blind* freezes the other-robot channels.

**Table 3.** Conditions of the agency test (T2). In every condition both robots move; only the cause of the lamp change differs.

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

H3a and H3b together form a double dissociation. H3b is interpretable only if the agent predicts OTHER at all, that is, if relPE(OTHER) < relPE(SPONT). A hypothesis was declared supported if the within-run 95% bootstrap interval (2,000 resamples over trials) excluded 0 in the predicted direction. This had to hold in at least 4 of 5 FULL runs, each of which had passed the competence gate.

**Validity checks.** The test itself was tested with three pre-registered checks:

- *V1*: UNTRAINED must not meet the pass rule, otherwise the test is declared fooled.
- *V2*: COMPARATOR must meet H1 and H2, as a check of the whole pipeline.
- *V3*: we report the POSITION RULE's attribution accuracy on the ONPAD conditions, where it is expected to fail.

**Tests expected to be fooled.** Two further analyses were pre-registered as descriptive, because we expected trivial controls to pass them.
- *Test T1* (body versus world) presented a lamp change, an internal metabolic shock or nothing. It measured the share of prediction error that fell on the body channels (energy and damage).
- *Exploratory probes* decoded two things from the GRU state: the cause of a lamp change (self, other, spontaneous), 1, 10 and 40 steps after the event; and the event type (world, body, none), 1 and 9 steps after it. The probes were logistic regressions with L2 regularization (λ = 10⁻³), evaluated by five-fold cross-validation. They were compared with the same probes applied to UNTRAINED networks and to a raw-input baseline consisting of the last five observations. The pre-registered criterion was that decoding counts as evidence only if it exceeds the raw-input baseline.

**Sensitivity analyses (post hoc).** After the pre-registered analysis, we asked how large a self-prediction effect the test could have detected. Each trained FULL agent's heat prediction was blended with a self-model's: prediction = (1 − w) · agent + w · self-model, for w = 0.02 to 1. The identical battery and pass rule were then rerun.
- In the first analysis, the self-model was the COMPARATOR, which times self-caused changes perfectly.
- A partly learned self-model would be less precise. In a second analysis, the comparator therefore misjudged the pad edge on each trial by an error drawn from N(0, σ), for σ = 0.05, 0.1 or 0.2 m. The agent moves about 0.08 m per step, so these errors shift the predicted toggle by about 0.6, 1.3 or 2.5 steps. The size of the expected change was also misjudged, with a gain drawn from lognormal(0, 0.3).

The draws depended only on the trial, so intact and ablated versions of a trial shared them.

## 2.4 Study 2b: necessary agency (pre-registered)

Study 2b and Study 1b were pre-registered together (commit `3486e57`, 23 September 2026; Supplementary Material, Section S2), after the Study 2 results were known.

**Design check.** To test whether the agent's own action was useful in the Study 2 world, we compared two scripted robots with privileged knowledge over 100 episodes each. The WAITER waits for others to switch the lamp off; the SWITCHER switches it off itself. In the Study 2 world, switching conferred no survival benefit: SWITCHER minus WAITER survival was −0.04 [−0.09, +0.01]. The world *agency_b* made switching worthwhile with four changes:
- the other robot chooses the pad with probability 0.05 instead of 0.5;
- spontaneous toggles occur at 1/120 s⁻¹ instead of 1/20 s⁻¹;
- start energy is drawn from U(0.2, 0.6);
- the lamp is always on at the start.

With these changes, switching conferred a survival benefit of +0.25 [+0.17, +0.34]. Everything else was identical to Study 2. A pre-registered manipulation check (M1) required the trained agents to toggle the lamp themselves at least once per free-running episode on average.

## 2.5 Study 1b: learning agents on the Study 1 markers (pre-registered)

- *Agent:* the FULL architecture, given the 11-channel Study 1 observation.
- *Training:* each episode was either the foraging world or the trade-off world, with start energy drawn from U(0.05, 1). The budget was the same as in Study 2 (3 × 10⁶ steps), with five seeds.
- *Evaluation:* the unchanged Study 1 battery with the deterministic policy.
- *Decision rules:* the trade-off marker separates the learners from the reflexes if the score is positive, with an interval excluding 0, in at least 4 of 5 seeds (Q1). Sensitization separates them if, in at least 4 of 5 seeds, it lies below the memoryless agents' lowest interval bound and its like-for-like variant is below 0 (Q3).

## 2.6 Software and reproducibility

The code is written in Python 3.14 with MuJoCo 3.14, Gymnasium 1.3, NumPy 2.5, PyTorch 2.14 (CPU) and Matplotlib 3.11, and the exact package versions are recorded. It includes 90 automated tests of the physics, physiology, worlds, agents and analysis code. Every number in this article is produced by scripts in the repository from saved raw data. Every figure is redrawn from saved result tables (Section *Data and Code Availability*).

# 3 Results

## 3.1 Study 1: every behavioural marker was met by a minimal mechanism

Table 4 and Figure 2 summarize the markers for all five agents.

**Anticipatory avoidance: no memory needed.**
- The thermotactic reflex left 100% of its heat encounters before its nociceptor fired (1.00 [1.00, 1.00]; also 1.00 at 100 seeds) and took no damage.
- The nociceptive reflex scored 0.25 [0.15, 0.36], no better than the random walker (0.34 [0.20, 0.49]).

A one-step comparison of the current temperature with the previous one passes this marker perfectly.

**Motivational trade-off: one interoceptive threshold, but the standard score misses it.**
- The plain reflexes never crossed the heat wall, so both scored exactly 0.
- The random walker's score was negative (−0.47 [−0.67, −0.27]). This is an opportunity artefact: at low energy it usually died before reaching the wall.
- The motivational reflex also scored −0.47 [−0.70, −0.23] on the pre-specified score, apparently failing. It crossed at start energy 0.08 in 0.23 of episodes, but at 0.9 in 0.70. Starting with high energy, it later became needy within the 90 s episode and crossed then.

At the moment of decision the picture reverses (Table 5). The motivational reflex crossed on 56% of approaches begun with energy below 0.25 and on none of the 553 approaches begun with more energy (slope −20.8 [−25.8, −17.4]). The random walker showed no relation between energy and crossing (+0.5 [−0.3, +1.4]). A single threshold on energy, with no memory, therefore produces a clean trade-off, and the score as commonly operationalized fails to detect it.

**Sensitization: one bit of state is enough, and the standard metric is biased.**
- The metric carried a large positive bias. At 100 seeds, memoryless agents, which cannot become more cautious, scored +9.95 °C [7.16, 12.87] (random) and +8.77 °C [6.14, 11.43] (nociceptive reflex). The bias arises because every encounter before the first harmful one is non-harmful by definition.
- The like-for-like variant was close to 0 for both (+0.93 °C [−1.50, 3.37] and −0.81 °C [−3.15, 1.52]).
- The sensitizing reflex scored −3.16 °C [−4.81, −1.58] on both versions of the metric. This is far below the memoryless floor of +6.14 °C, and it meets the criterion that Study 1b pre-registered for learning agents.

**Survival** separated competent agents from the random walker (0.70–0.83 versus 0.23) but, by construction, cannot separate reflexes from learners.

**Table 4.** Study 1 marker results (mean [95% CI]; 30 seeds; sensitization at 100 seeds because few episodes qualify).

| Marker | Random walker | Nociceptive reflex | Thermotactic reflex | Motivational reflex | Sensitizing reflex |
|---|---|---|---|---|---|
| Memory | none | none | none | none | one bit |
| Survival | 0.23 [0.12, 0.41] | 0.70 [0.52, 0.83] | 0.83 [0.66, 0.93] | 0.83 [0.66, 0.93] | 0.77 [0.59, 0.88] |
| Anticipatory avoidance | 0.34 [0.20, 0.49] | 0.25 [0.15, 0.36] | 1.00 [1.00, 1.00] | 0.97 [0.93, 1.00] | 0.55 [0.45, 0.64] |
| Damage taken per episode | 0.47 [0.34, 0.59] | 0.56 [0.45, 0.66] | 0.00 [0.00, 0.00] | 0.03 [0.00, 0.10] | 0.19 [0.14, 0.23] |
| Trade-off score, pre-specified | −0.47 [−0.67, −0.27] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | −0.47 [−0.70, −0.23] | 0.00 [0.00, 0.00] |
| Sensitization, °C | +9.95 [7.16, 12.87] | +8.77 [6.14, 11.43] | not defined (never harmed) | not estimable (1 episode) | −3.16 [−4.81, −1.58] |
| Sensitization, like-for-like, °C | +0.93 [−1.50, 3.37] | −0.81 [−3.15, 1.52] | not defined | not estimable | −3.16 [−4.81, −1.58] |

**Table 5.** Trade-off at the moment of decision (post hoc; trade-off world, 4 start energies × 100 seeds). Crossing probability per approach, by the agent's energy when the approach began, and the logistic slope of crossing on energy (negative = crosses when in need).

| Agent | Approaches | Energy < 0.25 | 0.25–0.5 | ≥ 0.5 | Slope [95% CI] |
|---|---|---|---|---|---|
| Random walker | 302 | 0.43 (57/133) | 0.49 (43/87) | 0.49 (40/82) | +0.5 [−0.3, +1.4] |
| Nociceptive reflex | 790 | 0.00 (0/356) | 0.00 (0/277) | 0.00 (0/157) | no crossings |
| Thermotactic reflex | 1,195 | 0.00 (0/660) | 0.00 (0/376) | 0.00 (0/159) | no crossings |
| Motivational reflex | 967 | 0.56 (231/414) | 0.00 (0/384) | 0.00 (0/169) | −20.8 [−25.8, −17.4] |
| Sensitizing reflex | 1,187 | 0.00 (0/663) | 0.00 (0/364) | 0.00 (0/160) | no crossings |

::figure Figure2 | Four bar charts comparing five agents: random walker, nociceptive reflex, thermotactic reflex, motivational reflex and sensitizing reflex. Survival: 0.23, 0.70, 0.83, 0.83 and 0.77. Anticipatory avoidance: 0.34, 0.25, 1.00, 0.97 and 0.55. Pre-specified trade-off score: −0.47, 0, 0, −0.47 and 0. Sensitization at 100 seeds: about +10 and +9 degrees for the random walker and nociceptive reflex, not defined or not estimable for the thermotactic and motivational reflexes, and −3.2 degrees for the sensitizing reflex.

**Figure 2.** Study 1: behavioural markers applied to agents with no memory or one bit of state. Bars show means and whiskers 95% confidence intervals; n is the number of episodes or encounters contributing. Survival, anticipation and trade-off use 30 seeds; sensitization uses 100 seeds. The thermotactic reflex passes anticipatory avoidance perfectly, and the sensitizing reflex passes sensitization. The motivational reflex appears to fail the pre-specified trade-off score, although it makes a clean trade-off at the moment of decision (Table 5). Memoryless agents that can be harmed show a positive "sensitization".

## 3.2 Study 2: the test was valid, and no trained agent supported any hypothesis

**Training and competence.** All trained runs completed 2,998,272 steps.
- Four of five FULL runs learned to survive: 40–90% of held-out 60 s episodes, against 15% for FULL seed 4.
- The same four runs passed the pre-registered competence gate, with forward-model errors of 0.47–0.69 times that of NO-CHANGE. FULL seed 4 (1.18) and all NOEFF runs (1.63–1.98) failed it.
- Post hoc, we found that the gate had been passed on the easy channels. On the eight heat channels that the test scores, every FULL agent's forward model was no better than predicting no change: 0.98–1.01 times the NO-CHANGE error (Table 6). Excluding only the efference copy already raised the ratios to 0.77–0.85.

The trained agents therefore never had a competent predictor of the channels the test measures. This fact frames everything that follows.

**Pre-registered hypotheses.** None was supported (Table 6):

- *H1* (self-prediction) was met by 0 of 5 FULL runs. The effects ranged from −0.004 to +0.001, and every interval included 0.
- *H2* (omission surprise) was met by 0 of 5.
- *H3a* (self-blind specificity) was met by 0 of 5.
- *H3b* was not applicable in 4 of 5 runs, because relPE(OTHER) was not below relPE(SPONT).

At the moment of the lamp change, the FULL agents' relative prediction error was about 1 in every condition (Figure 3): SELF 0.996, OTHER 0.994, SPONT 0.994, OTHER-ONPAD 1.002 and SPONT-ONPAD 1.001. Consistent with their competence on the heat channels, the forward models did not predict lamp changes at all, whatever their cause. This is different from predicting all causes equally well.

**Table 6.** Study 2 FULL runs: forward-model error relative to NO-CHANGE on all channels (the pre-registered gate) and on the heat channels the test scores (post hoc), survival, and the pre-registered H1 effect (relPE(SPONT) − relPE(SELF), mean [95% CI]). No run met any hypothesis.

| Run | Error ratio, all channels (gate ≤ 0.8) | Error ratio, heat channels | Survived 60 s | H1 effect |
|---|---|---|---|---|
| FULL seed 0 | 0.54 (passed) | 0.98 | 0.90 | −0.004 [−0.015, 0.007] |
| FULL seed 1 | 0.47 (passed) | 0.99 | 0.90 | −0.002 [−0.017, 0.013] |
| FULL seed 2 | 0.69 (passed) | 1.01 | 0.85 | −0.002 [−0.020, 0.016] |
| FULL seed 3 | 0.64 (passed) | 1.01 | 0.40 | +0.001 [−0.008, 0.011] |
| FULL seed 4 | 1.18 (failed) | 1.01 | 0.15 | −0.001 [−0.010, 0.009] |
| COMPARATOR (positive control) | — | — | — | +1.026 [1.011, 1.040] |

::figure Figure3 | Four line plots of relative prediction error at the lamp change for five conditions. FULL agents lie at 1 for every condition. Untrained networks lie above 1. The comparator is near 0 for SELF and near 1 for all other conditions. The no-change predictor is exactly 1 everywhere.

**Figure 3.** How surprising is the same lamp change, depending on its cause? Relative prediction error of the distal heat prediction at the lamp change (0 = fully predicted; 1 = no better than predicting no change; symmetric-log axis). The hand-built COMPARATOR predicts only self-caused changes. Trained FULL agents behave like the NO-CHANGE predictor in every condition: they do not anticipate lamp changes at all.

**Validity checks.** All three checks came out as required. Figure 4 shows the per-run effects of every predictor.

- *V1 passed*: UNTRAINED networks met no hypothesis in 4 or more of 5 runs. Random networks did, however, produce "significant" single-run effects in 3 of 15 hypothesis tests, which shows why a multi-run pass rule is necessary.
- *V2 passed*: COMPARATOR relPE was 0.004 for SELF against 1.030 for SPONT, an H1 effect of +1.026 [1.011, 1.040]. It met H2, and self-blinding raised its relPE for SELF to 0.924, the expected dissociation.
- *V3*: the POSITION RULE attributed every OTHER-ONPAD and SPONT-ONPAD change to itself (accuracy 0.00 on both), so a position shortcut fails the dissociation trials.

::figure Figure4 | Four forest plots, one per hypothesis, with one row per run. Rows for FULL, NOEFF, NOFWD, UNTRAINED and COMPARATOR show effect estimates with 95 percent confidence intervals. Only the comparator lies clearly on the predicted side for H1, H2 and H3a; FULL intervals all include zero.

**Figure 4.** Pre-registered effects per run (95% bootstrap intervals; positive = predicted direction; symmetric-log axes). Filled markers count toward the verdict: the interval excludes 0, and the run is gated and applicable. FULL intervals include 0 for every hypothesis. A few untrained and NOFWD runs show isolated "significant" effects, which the 4-of-5 rule absorbs.

**Why no self-prediction?** An ecological check suggests that self-caused lamp changes were almost absent from the agents' experience. In 250 free-running episodes (50 per FULL run), the agents entered the pad 26 times, against 1,378 entries by the other robot and 638 spontaneous toggles. A strategy analysis (20 episodes per run) showed that the surviving agents did 94–96% of their charging while the lamp was off, and waited near the charger while it was on. They had learned to let the other robot and chance switch the lamp for them, and toggled it themselves only 0.00–0.20 times per episode on average. Lamp changes occurred on fewer than 1% of time steps, and self-caused ones were rarer still. A next-observation loss averaged over all channels therefore gives little pressure to model them.

**Tests expected to be fooled (T1 and probes).**
- *Body versus world (T1):* after an internal shock, the share of prediction error on the body channels was 0.96 for NO-CHANGE and 0.86 for FULL, against 0.00–0.08 after world events. Because the body has dedicated interoceptive channels, a predictor that knows nothing separates body events from world events.
- *Behaviour after the events* did not differ by condition: FULL agents moved 4.97–4.99 m toward the charger in the following 5 s.
- *Probes:* linear probes decoded "who caused the lamp change" with 100% accuracy at lags of 1, 10 and 40 steps. They did so from trained FULL agents, from UNTRAINED networks and from the raw input alike (Figure 5). Event type was decoded at 0.59–0.74 by all three feature sets, where chance was 0.33.

Decodability therefore gave no evidence beyond what the raw input already contained.

::figure Figure5 | Two line plots of cross-validated decoding accuracy against memory lag. Left: who caused the lamp change, decoded at 1.0 at lags 1, 10 and 40 by FULL agents, untrained networks and raw input alike. Right: what happened (world, body or nothing), decoded at about 0.6 to 0.75 by all three feature sets; chance is one third.

**Figure 5.** Exploratory probes. Left: the cause of a lamp change is decodable at ceiling from trained agents, untrained networks and raw input alike. Right: event type is decoded similarly well by all feature sets. Decodable information is present in the input and is not evidence of a self-model.

**Exploratory analysis (not pre-registered).** In scripted walks with no lamp change, the FULL agents' heat predictions depended specifically on self-motion signals. Self-blinding increased their prediction error in 4 of 5 runs (for example, from 1.66 to 2.50 times the no-change error), whereas other-blinding had no effect (1.66 to 1.66). The predictions were nevertheless worse than predicting no change (ratios 1.47–3.11). We treat this as hypothesis-generating only.

## 3.3 Sensitivity of the agency test (post hoc)

With perfect timing, the test was highly sensitive (Table 7; Figure 6). Blending in 2% of the comparator's prediction was enough to meet H1 and H3a in 4 of 5 runs. The fifth run, FULL seed 4, failed the gate and never counts. From w = 0.1, H2 was also met.

With realistic imprecision, more of the self-model was needed:
- H1 was met from w = 0.05, 0.1 and 0.25 when the pad edge was misjudged by σ = 0.05, 0.1 and 0.2 m respectively.
- H2 needed w = 0.25–1.
- The dissociation H3a was the least robust. At σ = 0.2 m it never reached the pass rule: when the intact prediction is often mistimed, freezing the self-motion signals costs little.

Every real FULL run's H1 interval lay below +0.016. Depending on the timing precision assumed, this bound corresponds to anticipating less than about 1% (exact timing) to 6% (σ = 0.2 m) of a self-caused change. Within the resolution the test was shown to have, the Study 2 null result is informative. But it concerns agents whose forward models did not predict the heat channels at all.

**Table 7.** Post-hoc sensitivity analysis: the smallest blend weight w at which each hypothesis was met by 4 of 5 runs, for self-models of decreasing timing precision. The last column gives the weight at which the mean H1 effect equals the real agents' largest upper confidence bound (+0.016).

| Self-model | H1 met from | H2 met from | H3a met from | Real agents' bound corresponds to |
|---|---|---|---|---|
| Exact timing | w = 0.02 | w = 0.1 | w = 0.02 | w ≈ 0.01 |
| Pad-edge error σ = 0.05 m (≈0.6 steps) | w = 0.05 | w = 0.25 | w = 0.02 | w ≈ 0.02 |
| σ = 0.1 m (≈1.3 steps) | w = 0.1 | w = 0.25 | w = 0.05 | w ≈ 0.03 |
| σ = 0.2 m (≈2.5 steps) | w = 0.25 | w = 1 | not reached | w ≈ 0.06 |

::figure Figure6 | Two line plots against blend weight on a symmetric-log axis, one line per self-model precision from exact timing to a 0.2 metre pad-edge error. Left: the mean H1 effect rises with the blend weight, most steeply for exact timing (to about 1.0 at w equals 1) and least for the least precise self-model (to about 0.13); the real agents' largest upper confidence bound, 0.016, is marked near zero. Right: the number of runs meeting H1 reaches the pass rule of 4 at w equals 0.02, 0.05, 0.1 and 0.25 for the four precision levels.

**Figure 6.** Sensitivity of the pre-registered agency test (post hoc). Each trained FULL agent's heat prediction is blended with a self-model's (weight w); the self-model times self-caused changes exactly or with a per-trial pad-edge error of σ = 0.05–0.2 m. (a) Mean H1 effect; the arrow marks the largest upper confidence bound of the real agents. (b) Number of runs meeting H1; the pass rule requires 4 of 5, and the gated-out run never counts.

## 3.4 Study 2b: the agents did not discover the necessary action

The manipulation check failed. Self-caused toggles per free-running episode were 0.00, 0.04, 0.22, 0.90 and 0.04 across the five FULL runs, and no run reached the pre-registered 1.0. All five FULL runs failed the competence gate (0.99–1.35 times the NO-CHANGE error). On the heat channels they were again no better than predicting no change (1.00–1.03).

Only two agents survived any held-out episodes. Three never learned to charge; two charged almost only while the lamp was off, and only one of these regularly used the switch. As registered, the hypotheses were evaluated regardless: H1–H3 were each met in 0 of 5 FULL runs, and V1–V3 again passed. Ignoring the gate, the perfectly timed sensitivity analysis detected a 2% blend in 5 of 5 runs, and the agents' H1 intervals lay below +0.033. The full report is in the Supplementary Material (Section S7).

## 3.5 Study 1b: the learners settled into doing nothing

- *Q1, trade-off:* the marker did not separate the learners from the reflexes. The score was 0.00 [0.00, 0.00] in all five seeds, because the learners never crossed the heat wall and never reached the charger in the trade-off world.
- *Q3, sensitization:* not estimable, because the learners were almost never harmed; no episode contained encounters both before and after harm.
- *Survival:* no learner survived a single 90 s foraging episode.

The trajectories (Figure 7) show why. The learners walked away from the charger to the far wall and waited there until their energy ran out, with lifetimes of 74–81 s of the 90 s episode. Their exploration noise had shrunk to a standard deviation of about 0.1, and the stochastic training policy behaved in the same way as the deterministic one. Within the fixed budget, the learners converged on a local optimum: by moving little, they reduced both energy expenditure and the risk of heat damage.

::figure Figure7 | Five panels, one per learned seed, each showing five trajectories in the foraging world. Trajectories lead away from the charger in the upper right to the bottom or left wall, where most end in a cross marking death.

**Figure 7.** Study 1b: the first five foraging episodes of each learning agent (deterministic policy). Circles mark starts and crosses deaths. The agents move away from the charger (upper right) to the far wall and wait there until their energy runs out.

## 3.6 Methodological findings

**Test worlds must be verified, not assumed.** The trade-off world, as first specified in the design brief, did not pose a trade-off.
- At top speed, crossing the heat wall cost only 0.007 damage.
- The supposedly impossible detour was survivable at the lowest start energy: a scripted agent arrived at the charger with 0.041 energy to spare.

We therefore changed the wall from 58 °C with σ = 0.35 m to 60 °C with σ = 0.5 m, and the lowest start energy from 0.15 to 0.08. Both changes were verified analytically and with scripted runs in the physics engine before any marker was measured (Supplementary Material, Section S5).

**Markers must be scored at the moment of decision.** When need changes during a trial, a score based on the starting state can reverse the sign of a genuine trade-off (Section 3.1).

**Worlds must make the tested capacity useful.** The Study 2 agents' failure to use the switch was not a quirk of learning. The scripted design check showed that switching was not worth it in that world (−0.04 [−0.09, +0.01]). A test of whether an agent predicts the consequences of its own actions presupposes that acting pays, and this can be checked before training.

**Competence checks must target the measured channels.** A gate averaged over all channels was passed by forward models that were useless on the channels the test scores (Section 3.2).

**Control agents must be competent.** As first specified, the withdrawal reflex reversed its *commanded* heading on every trigger. It therefore oscillated inside heat sources until it died: all 28 of its deaths in 30 episodes were from damage. A control that fails in this way makes markers look more discriminating than they are. We used a memoryless fix, which reverses the *actual* direction of motion and keeps escaping while the heat is falling, and report both versions in the repository.

# 4 Discussion

**Every behavioural marker we tested was met by a minimal mechanism.** The mechanisms that met them were:

- anticipatory avoidance, by a reflex that compares the current temperature with the previous one;
- motivational trade-off, by a reflex whose withdrawal is vetoed by one threshold on energy;
- sensitization, by a reflex with one bit of state set by harm.

Two further observations point the same way. Body-versus-world discrimination was met by a predictor that expects nothing to change, because the body has dedicated interoceptive channels. "Self/other" information in internal states was met by untrained networks and by the raw input.

None of this shows that anticipation, trade-offs, sensitization or internal representations are irrelevant to sentience. It shows that, taken one at a time, such observations carry little evidential weight unless minimal mechanisms fail them. This is a concrete, testable form of the gaming problem (Birch, 2024). Artificial life is well placed to test it, because the minimal mechanism can be built, run through exactly the same battery, and inspected. We suggest that any proposal to use a behavioural or decoding marker as evidence about an artificial system should report the marker's performance on reflex, random and untrained controls matched to the system's sensors and body.

Sentience frameworks do not rely on single markers; they weigh several together (Birch et al., 2021; Crump et al., 2022). Our three minimal mechanisms are independent and compatible, so a single agent could implement all of them with one bit of memory. We did not test such a combined agent. Frameworks that weigh markers jointly would need to be evaluated against it before a pattern across markers is taken as evidence.

The published criterion that our minimal mechanisms do *not* meet is associative learning (criterion 7): learning that a neutral cue predicts harm, or learning a new way to avoid it. Our sensitizing reflex changes its threshold, but it learns no association. Ginsburg and Jablonka (2019) argue that an open-ended form of associative learning is the transition marker for minimal consciousness, and Feinberg and Mallatt (2016) tie the origin of consciousness to the evolution of complex brains and senses. These views make associative learning the natural next target for a minimal-mechanism audit.

A second lesson concerns measurement. The trade-off score, computed as it commonly is from the starting state, missed a genuine trade-off, because need changed within the trial. The standard sensitization metric was biased by about +9 °C, because of how encounters are split. Neither problem is specific to artificial agents. Animals also change state within a trial, and the same splitting bias applies to any before/after-harm comparison. Here, however, both problems can be diagnosed exactly, because the ground truth is known.

**Tests of agency can be made robust.** The pre-registered agency test was not fooled:

- it detected a known comparator mechanism;
- it rejected random networks;
- it exposed a position shortcut;
- it detected a self-model contributing 2% of the prediction with exact timing, and 5–25% with realistic timing errors.

Its dissociation logic, freezing self-motion signals versus other-agent signals, provides causal rather than merely correlational evidence about which signals a prediction depends on. This matters because decoding, the most common way of looking for "self" information in networks, failed badly here: the cause of a lamp change was decodable at ceiling from networks that had never been trained. The dissociation was, however, the component most sensitive to imprecise timing. A test that relies on it needs either a precise self-model or more trials.

**The limiting factor was the learners, not the tests.** Survival training plus a generic next-observation loss produced agents that failed in three distinct ways:

- in Study 2 they *free-rode*, letting the other robot and chance change the world for them;
- in Study 2b they *failed to discover* a necessary action;
- in Study 1b they *settled into doing nothing* until they starved.

In none of these cases did the agents gather the experience from which a self-prediction could be learned. Their forward models also did not learn the heat channels the test measures, which a gate averaged over all channels failed to reveal.

This is an ecological point as much as a computational one. A capacity to predict the consequences of one's own actions can be learned only by an agent that acts, in a world where acting makes a difference, often enough to be worth modelling. Our pre-registered negative results caution against assuming that self-models emerge "for free" from homeostatic training. They also suggest an order of work:
1. verify that the world makes the capacity useful (a cheap scripted check);
2. verify that the learner exercises the capacity (a manipulation check) and predicts the measured channels (a targeted competence check);
3. only then test for the internal signature.

These results complement recent work in which homeostatic agents develop integrated behaviour (Yoshida, Daikoku, et al., 2024; Yoshida, Kanazawa, & Kuniyoshi, 2024), and in which behavioural observations of such an agent are weighed as evidence about affect (Solms et al., 2026). Our contribution is not a claim about what such agents can or cannot do in general. It is a set of tools and controls that makes such claims testable, together with a demonstration of how easily standard behavioural observations can be produced without the capacity they are taken to indicate.

**What would count as a positive result?** Under our pre-registered criteria, a learning agent would show a functional sense of agency if four conditions held together, in at least four of five independently trained runs that pass the competence and manipulation checks. It would have to:

- predict self-caused changes better than spontaneous ones (H1);
- register surprise when an expected self-caused change fails to occur (H2);
- lose this advantage specifically when its self-motion signals are frozen (H3a);
- predict other-caused changes from the other agent's signals (H3b).

Each element rules out a different shortcut. H1 alone could reflect position, and H2 alone could reflect a generic expectation that something changes after movement. H3a and H3b establish which signals the prediction depends on. Even this full pattern would be evidence of a comparator-like mechanism, which the hand-built positive control shows can be implemented in a few lines of code. On the two-step account of agency, it would correspond to the feeling of agency rather than a judgement of agency (Synofzik et al., 2008), and not to self-awareness in any richer sense. This illustrates the general point: the more precisely a marker is specified, the more clearly one can see which minimal mechanism would satisfy it, and hence what further evidence is needed.

**Beyond embodied agents.** The same logic applies to other artificial systems. Keeling et al. (2024) found that several large language models make threshold-like trade-offs between points and stipulated pain or pleasure in a text-based game. Our results do not bear directly on language models, whose behaviour is shaped by human-generated text rather than by homeostatic need. But our motivational reflex shows how the evidential weight of such a finding could be assessed. One would construct minimal systems that could produce the same pattern, for example by mapping the stated stakes to choices through a threshold, and show that they fail the test.

**Paths to positive tests.** Positive tests of the agency marker require learners that reliably forage, act on the world and model the measured channels. Candidate routes include:
- longer training, curricula or exploration bonuses;
- prediction objectives weighted toward the channels that matter;
- agents with explicit world models;
- evolving populations under ecological pressures, in the tradition of evolved minimal agents (Beer, 1996; Egbert et al., 2012).

Each should be pre-registered separately and evaluated with the same validated battery, including the competence and sensitivity checks. The exploratory hint that heat predictions depend on self-motion signals (Study 2) did not replicate consistently in Study 2b and should itself be tested prospectively.

**Scope.** All results are functional. Nothing here bears on whether any agent has subjective experience. Passing or failing these tests is evidence about mechanisms, not about feelings. Our claim is methodological: a marker that a minimal mechanism passes cannot, on its own, distinguish a system that has a capacity from one that does not.

**Limitations.**
- The body is a disc with no limbs, and each study used a single environment.
- There were five training runs per variant and one fixed, untuned training budget, which our learners did not master.
- The other robot was scripted rather than learning.
- The minimal controls, the decision-time trade-off analysis, the heat-channel competence check and the sensitivity analyses were all added after the pre-registered studies. The imprecise self-model is only one way to model partial learning.
- We did not test an agent combining all three minimal mechanisms.
- The pre-registrations were time-stamped in version control rather than on an independent registry.

A different agent, objective or training budget could produce a different result, and our negative results about learners should be read as results about these learners.

# 5 Conclusion

Behavioural and decoding markers of sentience need to be benchmarked against minimal mechanisms before they are used as evidence. In a physics-simulated homeostatic agent, each behavioural marker we tested was met by a mechanism with at most one bit of memory:
- anticipatory avoidance, by a one-step reflex;
- motivational trade-off, by a single energy threshold;
- sensitization, by a single bit of state set by harm.

Two standard measurements were also misleading: a trade-off score that ignored within-trial changes of need, and a sensitization metric biased in agents without memory. A pre-registered, prediction-based test of the sense of agency could be made valid and sensitive, with explicit positive, negative and shortcut controls. Generic homeostatic learning agents, however, did not acquire the capacity it measures, or even competent predictions of the measured channels. The code, pre-registrations, trained models and raw data are openly available, so that other agents can be run through the same validated battery.

# Use of Generative AI

::noindent In accordance with the *Artificial Life* policy on generative AI, we state that generative AI was used extensively in this work. The system was Claude Opus 5.5 (Anthropic, 2026; model identifier claude-opus-5-5), accessed through the Claude Code application at https://claude.ai between 22 and 26 September 2026. It was used for:

- writing the simulation, agent, training and analysis code from a specification written by the author(s);
- proposing elements of the experimental design, including the validity controls, the competence gate, the drafts of both pre-registration documents and the design checks;
- proposing the post-hoc analyses (the minimal controls, the decision-time trade-off analysis, the heat-channel competence check and the sensitivity analyses), in response to a critical review of an earlier draft that the author(s) requested from the same system;
- running the experiments and analyses;
- producing all figures and tables;
- drafting the text of this article and of the Supplementary Material.

The research questions, the initial design brief and all decisions about what to run and report were the author(s)'. The code is covered by 90 automated tests, and every number in the article is generated by scripts from saved raw data. [FILL: Describe accurately and specifically what the author(s) personally checked. For example: which parts of the code were read and verified, which analyses were re-run independently, whether every number in the text was checked against the result files, and whether every reference was checked against its source.] The author(s) take full responsibility for the content of this article. Generative AI is not an author of this work.

# Acknowledgements

::noindent [FILL: Acknowledge people who helped but are not authors, or write "None."]

# Funding

::noindent [FILL: Name each funder and grant number, or write "This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors."]

# Competing Interests

::noindent [FILL: Declare any competing interests, or write "The author(s) declare no competing interests."]

# Author Contributions (CRediT)

::noindent [FILL: For each author, list their CRediT roles, for example: Conceptualization, Methodology, Software, Validation, Formal analysis, Investigation, Data curation, Writing – original draft, Writing – review & editing, Visualization, Supervision, Project administration, Funding acquisition. Contributions made with generative AI must be consistent with the section Use of Generative AI.]

# Data and Code Availability

::noindent The following are openly available at [FILL: public repository URL] and archived at [FILL: Zenodo DOI], under the [FILL: licence, for example MIT for code and CC BY 4.0 for data] licence:
- all code;
- both pre-registration documents with their version-control history;
- the trained models, raw trial data and result tables;
- the scripts that regenerate every figure and table.

The Supplementary Material lists the commands that reproduce each study.

# Ethics Statement

::noindent This study is entirely computational. It involved no human participants, no animals and no personal data, so ethical approval was not required.

# References

::refs
Anthropic. (2026). *Claude Opus 5.5* [Large language model]. https://claude.ai
Ashby, W. R. (1952). *Design for a brain*. Chapman & Hall.
Barandiaran, X. E., Di Paolo, E., & Rohde, M. (2009). Defining agency: Individuality, normativity, asymmetry, and spatio-temporality in action. *Adaptive Behavior*, *17*(5), 367–386. https://doi.org/10.1177/1059712309343819
Beer, R. D. (1996). Toward the evolution of dynamical neural networks for minimally cognitive behavior. In P. Maes, M. J. Mataric, J.-A. Meyer, J. Pollack, & S. W. Wilson (Eds.), *From animals to animats 4: Proceedings of the Fourth International Conference on Simulation of Adaptive Behavior* (pp. 421–429). MIT Press.
Berg, H. C., & Brown, D. A. (1972). Chemotaxis in *Escherichia coli* analysed by three-dimensional tracking. *Nature*, *239*(5374), 500–504. https://doi.org/10.1038/239500a0
Birch, J. (2024). *The edge of sentience: Risk and precaution in humans, other animals, and AI*. Oxford University Press. https://doi.org/10.1093/9780191966729.001.0001
Birch, J., Burn, C., Schnell, A., Browning, H., & Crump, A. (2021). *Review of the evidence of sentience in cephalopod molluscs and decapod crustaceans*. LSE Consulting.
Blakemore, S.-J., Wolpert, D. M., & Frith, C. D. (1998). Central cancellation of self-produced tickle sensation. *Nature Neuroscience*, *1*(7), 635–640. https://doi.org/10.1038/2870
Braitenberg, V. (1984). *Vehicles: Experiments in synthetic psychology*. MIT Press.
Butlin, P., Long, R., Elmoznino, E., Bengio, Y., Birch, J., Constant, A., Deane, G., Fleming, S. M., Frith, C., Ji, X., Kanai, R., Klein, C., Lindsay, G., Michel, M., Mudrik, L., Peters, M. A. K., Schwitzgebel, E., Simon, J., & VanRullen, R. (2023). *Consciousness in artificial intelligence: Insights from the science of consciousness* (arXiv:2308.08708). arXiv. https://doi.org/10.48550/arXiv.2308.08708
Caterina, M. J., Schumacher, M. A., Tominaga, M., Rosen, T. A., Levine, J. D., & Julius, D. (1997). The capsaicin receptor: A heat-activated ion channel in the pain pathway. *Nature*, *389*(6653), 816–824. https://doi.org/10.1038/39807
Cho, K., van Merriënboer, B., Gulcehre, C., Bahdanau, D., Bougares, F., Schwenk, H., & Bengio, Y. (2014). Learning phrase representations using RNN encoder–decoder for statistical machine translation. In *Proceedings of the 2014 Conference on Empirical Methods in Natural Language Processing* (pp. 1724–1734). Association for Computational Linguistics. https://doi.org/10.3115/v1/D14-1179
Crump, A., Browning, H., Schnell, A., Burn, C., & Birch, J. (2022). Sentience in decapod crustaceans: A general framework and review of the evidence. *Animal Sentience*, *7*(32), Article 1. https://doi.org/10.51291/2377-7478.1691
Di Paolo, E. A. (2000). Homeostatic adaptation to inversion of the visual field and other sensorimotor disruptions. In J.-A. Meyer, A. Berthoz, D. Floreano, H. Roitblat, & S. W. Wilson (Eds.), *From animals to animats 6: Proceedings of the Sixth International Conference on Simulation of Adaptive Behavior* (pp. 440–449). MIT Press.
Efron, B., & Tibshirani, R. J. (1993). *An introduction to the bootstrap*. Chapman & Hall.
Egbert, M. D., Barandiaran, X. E., & Di Paolo, E. A. (2012). Behavioral metabolution: The adaptive and evolutionary potential of metabolism-based chemotaxis. *Artificial Life*, *18*(1), 1–25. https://doi.org/10.1162/ARTL_a_00047
Elwood, R. W., & Appel, M. (2009). Pain experience in hermit crabs? *Animal Behaviour*, *77*(5), 1243–1246. https://doi.org/10.1016/j.anbehav.2009.01.028
Feinberg, T. E., & Mallatt, J. M. (2016). *The ancient origins of consciousness: How the brain created experience*. MIT Press.
Ginsburg, S., & Jablonka, E. (2019). *The evolution of the sensitive soul: Learning and the origins of consciousness*. MIT Press.
Keeling, G., Street, W., Stachaczyk, M., Zakharova, D., Comsa, I. M., Sakovych, A., Logothetis, I., Zhang, Z., Agüera y Arcas, B., & Birch, J. (2024). *Can LLMs make trade-offs involving stipulated pain and pleasure states?* (arXiv:2411.02432). arXiv. https://doi.org/10.48550/arXiv.2411.02432
Keramati, M., & Gutkin, B. (2014). Homeostatic reinforcement learning for integrating reward collection and physiological stability. *eLife*, *3*, e04811. https://doi.org/10.7554/eLife.04811
Man, K., & Damasio, A. (2019). Homeostasis and soft robotics in the design of feeling machines. *Nature Machine Intelligence*, *1*(10), 446–452. https://doi.org/10.1038/s42256-019-0103-7
Schulman, J., Moritz, P., Levine, S., Jordan, M., & Abbeel, P. (2016). High-dimensional continuous control using generalized advantage estimation. In *Proceedings of the 4th International Conference on Learning Representations*. https://doi.org/10.48550/arXiv.1506.02438
Schulman, J., Wolski, F., Dhariwal, P., Radford, A., & Klimov, O. (2017). *Proximal policy optimization algorithms* (arXiv:1707.06347). arXiv. https://doi.org/10.48550/arXiv.1707.06347
Sneddon, L. U., Elwood, R. W., Adamo, S. A., & Leach, M. C. (2014). Defining and assessing animal pain. *Animal Behaviour*, *97*, 201–212. https://doi.org/10.1016/j.anbehav.2014.09.007
Solms, M., Grimbly, S. J., Bassett, B., Boonstra, E., Hodson, R., Kuske, N., Mahadew, K., Rosman, B., van Hoof, C., & Shock, J. (2026). Inferring affective consciousness in an artificial agent: A case study. *Journal of Consciousness Studies*, *33*(7–8), 14–34.
Synofzik, M., Vosgerau, G., & Newen, A. (2008). Beyond the comparator model: A multifactorial two-step account of agency. *Consciousness and Cognition*, *17*(1), 219–239. https://doi.org/10.1016/j.concog.2007.03.010
Todorov, E., Erez, T., & Tassa, Y. (2012). MuJoCo: A physics engine for model-based control. In *2012 IEEE/RSJ International Conference on Intelligent Robots and Systems* (pp. 5026–5033). IEEE. https://doi.org/10.1109/IROS.2012.6386109
Towers, M., Kwiatkowski, A., Terry, J., Balis, J. U., De Cola, G., Deleu, T., Goulão, M., Kallinteris, A., Krimmel, M., KG, A., Perez-Vicente, R., Pierré, A., Schulhoff, S., Tai, J. J., Tan, H., & Younis, O. G. (2024). *Gymnasium: A standard interface for reinforcement learning environments* (arXiv:2407.17032). arXiv. https://doi.org/10.48550/arXiv.2407.17032
von Holst, E., & Mittelstaedt, H. (1950). Das Reafferenzprinzip: Wechselwirkungen zwischen Zentralnervensystem und Peripherie. *Naturwissenschaften*, *37*(20), 464–476. https://doi.org/10.1007/BF00622503
Wilson, E. B. (1927). Probable inference, the law of succession, and statistical inference. *Journal of the American Statistical Association*, *22*(158), 209–212. https://doi.org/10.1080/01621459.1927.10502953
Wittenburg, N., & Baumeister, R. (1999). Thermal avoidance in *Caenorhabditis elegans*: An approach to the study of nociception. *Proceedings of the National Academy of Sciences*, *96*(18), 10477–10482. https://doi.org/10.1073/pnas.96.18.10477
Yoshida, N., Daikoku, T., Nagai, Y., & Kuniyoshi, Y. (2024). Emergence of integrated behaviors through direct optimization for homeostasis. *Neural Networks*, *177*, Article 106379. https://doi.org/10.1016/j.neunet.2024.106379
Yoshida, N., Kanazawa, H., & Kuniyoshi, Y. (2024). *Synthesising integrated robot behaviour through reinforcement learning for homeostasis* [Preprint]. bioRxiv. https://doi.org/10.1101/2024.06.03.597087
::endrefs
