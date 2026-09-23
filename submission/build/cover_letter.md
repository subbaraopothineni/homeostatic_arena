::noindent [FILL: Date of submission]

::noindent The Editors-in-Chief
::noindent *Artificial Life*
::noindent The MIT Press

Dear Editors,

We submit the manuscript **"Which Behavioural Markers of Sentience and Self-Awareness Can a Simple Mechanism Fake? Pre-Registered Tests With Homeostatic Agents"** for consideration as an *Article* in *Artificial Life*.

Behavioural markers developed for animal sentience are increasingly proposed as evidence about artificial systems. The manuscript uses a core method of artificial life, building minimal synthetic agents, to test which of these markers simple mechanisms can pass. It then asks whether a pre-registered, prediction-based test of self/other distinction can be made valid and sensitive. We believe the work will interest readers concerned with embodiment, homeostasis, self-models and the evaluation of artificial agents.

We confirm that the manuscript is original, that it is not published or under consideration elsewhere, and that all authors have approved its submission. [FILL: If you post a preprint (for example on arXiv), add: "A preprint of this manuscript is available at <URL>."] All code, pre-registrations, trained models and raw data are openly available ([FILL: repository URL and DOI]).

In accordance with the journal's policy on generative AI, we disclose that generative AI (Claude Opus 5.5, Anthropic; accessed 22–23 September 2026) was used extensively. It wrote the simulation and analysis code, proposed parts of the experimental design, ran the analyses, produced the figures and drafted the text. This use is labelled and cited in a dedicated section of the manuscript and on its title page. The authors take full responsibility for the content.

[FILL: Optional — suggested or excluded reviewers, if you want to name them here as well as in the submission form.]

Thank you for considering our manuscript.

Sincerely,

[FILL: Corresponding author's name, affiliation, e-mail address and ORCID]

::pagebreak

# Extended Abstract

**Topic and fit.** The article asks which behavioural markers of sentience and self-awareness can be passed by minimal mechanisms. Animal-welfare science uses markers such as anticipatory avoidance, motivational trade-offs and sensitization, and these are now being proposed for AI. Artificial life is the natural venue because the question can only be answered synthetically: we build the simplest agents that could produce each marker, run them through the same tests, and inspect them. The test bed is an embodied, physics-simulated homeostatic agent whose only reward is drive reduction.

**Research question.** (1) Do four animal-sentience markers discriminate hard-wired reflexes from more complex agents? (2) Pre-registered: do recurrent agents trained with a self-supervised forward model predict self-caused sensory changes better than identical changes caused by another agent or by chance, as the reafference principle predicts? Two follow-up studies, also pre-registered, ask the same questions when acting on the world is necessary and when the markers are applied to learning agents.

**Research built upon.** The synthetic-minimal-model tradition (Ashby's homeostat; Braitenberg's vehicles), self-modelling robots (Bongard, Zykov and Lipson), homeostatic reinforcement learning (Keramati and Gutkin; Yoshida and colleagues), feeling-machine proposals (Man and Damasio), and a recent case study of affect in an artificial agent (Solms and colleagues). [FILL: add any Artificial Life journal articles you consider closest to this work.]

**Novelty.** (a) Evidence that a widely used marker, anticipatory avoidance, is passed perfectly by a memoryless one-step reflex, and that a standard sensitization metric is biased by about 9 °C in agents without memory. (b) A self/other test whose own validity is demonstrated: a hand-built comparator passes, untrained networks fail, a position shortcut is exposed, and a sensitivity analysis shows it detects an agent that anticipates only 2% of its self-caused changes. (c) Three pre-registered negative results: generic homeostatic learners free-rode on another agent, failed to discover a necessary action, or settled into inactivity, so they never acquired the capacity the test measures. (d) Practical lessons: verify test worlds, verify that the tested capacity is useful, and use competent controls.

**Why it matters to ALife.** Claims that artificial agents have sentience-relevant or self-model-like properties are becoming common. Our results show that several standard observations can be produced without the capacity they are taken to indicate, and they provide an open, validated battery and a set of controls for testing such claims. They also make an ecological point: a self-prediction can be learned only by an agent that acts, in a world where acting pays.

**Methodology.** MuJoCo physics with functional analogues of nociception, tissue damage and energy; reflex, random and untrained controls; recurrent PPO agents with a forward-model loss (five seeds per condition); pre-registration of hypotheses, controls and pass rules (effects must hold in at least 4 of 5 runs); bootstrap and Wilson confidence intervals; ablation-based double dissociations; and scripted design checks. All claims are functional; none concern subjective experience.
