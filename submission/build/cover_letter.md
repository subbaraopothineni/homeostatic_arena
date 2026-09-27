::noindent [FILL: Date of submission]

::noindent The Editors-in-Chief
::noindent *Artificial Life*
::noindent The MIT Press

Dear Editors,

We submit the manuscript **"Behavioural Markers of Sentience Are Met by Minimal Mechanisms: Validated and Pre-Registered Tests With Homeostatic Agents"** for consideration as an *Article* in *Artificial Life*.

Behavioural markers developed for animal sentience are increasingly proposed as evidence about artificial systems. The manuscript uses a core method of artificial life, building minimal synthetic agents, to test which of these markers simple mechanisms can meet. Each behavioural marker we tested was met by a mechanism with at most one bit of memory. Two standard measurements also proved misleading. The manuscript then shows how a pre-registered, prediction-based test of the sense of agency can be validated with positive, negative and shortcut controls and a sensitivity analysis. We believe the work will interest readers concerned with embodiment, homeostasis, agency and the evaluation of artificial agents.

We confirm that the manuscript is original, that it is not published or under consideration elsewhere, and that all authors have approved its submission. [FILL: If you post a preprint, add: "A preprint of this manuscript is available at <URL>."] All code, pre-registrations, trained models and raw data are openly available ([FILL: repository URL and DOI]).

In accordance with the journal's policy on generative AI, we disclose that generative AI (Claude Opus 5.5, Anthropic; accessed 22–26 September 2026) was used extensively. It wrote the simulation and analysis code, proposed parts of the experimental design and the post-hoc analyses, ran the analyses, produced the figures and drafted the text. This use is labelled and cited in a dedicated section of the manuscript and on its title page. [FILL: one sentence on what you personally verified.] The authors take full responsibility for the content.

[FILL: Optional — suggested or excluded reviewers, if you want to name them here as well as in the submission form.]

Thank you for considering our manuscript.

Sincerely,

[FILL: Corresponding author's name, affiliation, e-mail address and ORCID]

::pagebreak

# Extended Abstract

**Topic and fit.** Which behavioural markers of sentience can minimal mechanisms meet? Animal-welfare frameworks use behavioural criteria such as motivational trade-offs, and these are now being proposed for AI. Artificial life is the natural venue, because the question can only be answered synthetically: we build the simplest agents that could produce each marker, run them through the same tests, and inspect them. The test bed is a physics-simulated homeostatic agent whose only reward is drive reduction.

**Research question.**
1. Do behavioural sentience markers discriminate minimal mechanisms from richer ones?
2. Pre-registered: do recurrent agents with a self-supervised forward model predict self-caused sensory changes better than identical changes with other causes, as the comparator account of the sense of agency predicts?

Two further pre-registered studies test learning agents when acting is necessary, and on the behavioural markers.

**Research built upon.**
- Minimal-agent and homeostasis work in artificial life: Ashby; Braitenberg; Beer's minimally cognitive agents; Di Paolo's homeostatic adaptation; metabolism-based chemotaxis (Egbert, Barandiaran and Di Paolo, *Artificial Life*, 2012); and the account of agency of Barandiaran, Di Paolo and Rohde.
- Homeostatic reinforcement learning (Keramati and Gutkin; Yoshida and colleagues).
- Sentience frameworks (Birch et al.; Crump et al.).

[FILL: add any further *Artificial Life* journal articles you consider closest.]

**Novelty.**
- **(a) Minimal mechanisms meet every behavioural marker tested.** Each needs at most one bit of memory: a one-step thermotactic reflex (anticipatory avoidance), a reflex vetoed by low energy (trade-off), and a reflex with one bit set by harm (sensitization).
- **(b) Two measurement pitfalls.** A standard trade-off score reverses the sign of a genuine trade-off when need changes within a trial, and a standard sensitization metric is biased by about +9 °C.
- **(c) An agency test whose validity is demonstrated.** A hand-built comparator passes, untrained networks fail and a position shortcut is exposed. The test detects a self-model contributing 2–25% of the prediction, depending on its timing precision.
- **(d) Three pre-registered negative results about learners.** The learners free-rode on another agent, failed to discover a necessary action, or became inactive. A competence gate averaged over all channels hid the fact that their forward models were useless on the measured channels.

**Why it matters to ALife.** Claims that artificial agents show sentience-relevant or agency-like properties are becoming common. Our results show that standard observations can be produced without the capacity they are taken to indicate, and they provide an open, validated battery, minimal controls and competence checks for testing such claims.

**Methodology.**
- MuJoCo physics with functional analogues of nociception, damage and energy.
- Reflex, minimal, random and untrained controls.
- Recurrent PPO agents with a forward-model loss.
- Pre-registered hypotheses and pass rules (at least 4 of 5 runs), and post-hoc analyses labelled as such.
- Bootstrap and Wilson intervals, ablation-based dissociations and scripted design checks.

All claims are functional; none concern subjective experience.
