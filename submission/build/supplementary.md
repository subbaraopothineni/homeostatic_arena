::title Supplementary Material

::center for "Which Behavioural Markers of Sentience and Self-Awareness Can a Simple Mechanism Fake? Pre-Registered Tests With Homeostatic Agents"

::center [FILL: Author names, as on the manuscript]

# Contents

::noindent This document collects the materials that support the article. Sections S1 and S2 reproduce the two pre-registration documents verbatim, including their append-only deviation logs. Sections S3–S8 reproduce the analysis reports generated automatically by the code from saved raw data. Section S9 gives additional Study 1 tables, and Sections S10 and S11 give the version-control history and the commands that reproduce every result. Figures referred to in the reports are included in the code and data archive at the paths given. As in the article, every measurement is functional and makes no claim about subjective experience. The generative-AI disclosure in the article applies equally to this document.

- S1. Pre-registration for Study 2 (verbatim)
- S2. Pre-registration for Studies 2b and 1b (verbatim)
- S3. Study 2: full generated report
- S4. Study 2: exploratory analyses (not pre-registered)
- S5. Study 1 trade-off world: design check
- S6. Post-hoc sensitivity analyses (Studies 2 and 2b)
- S7. Study 2b: full generated report and exploratory analyses
- S8. Study 1b: full generated report and exploratory analyses
- S9. Study 1: additional tables (100 seeds; literal reflex)
- S10. Version-control history
- S11. Software and reproduction commands

::pagebreak

# S1. Pre-Registration for Study 2 (Verbatim)

::noindent Source: `docs/preregistration_v0.2.md`, first committed as `d70a2fe` on 22 September 2026 at 19:38 (UTC−7), before any Study 2 code or data existed. Later commits only appended to its deviations section.

::include docs/preregistration_v0.2.md

::pagebreak

# S2. Pre-Registration for Studies 2b and 1b (Verbatim)

::noindent Source: `docs/preregistration_v0.2b.md`, committed as `3486e57` on 23 September 2026 at 06:32 (UTC−7), before any Study 2b or Study 1b agent was trained. Later commits only appended to its deviations section.

::include docs/preregistration_v0.2b.md

::pagebreak

# S3. Study 2: Full Generated Report

::include results/v02/report.md

::pagebreak

# S4. Study 2: Exploratory Analyses (Not Pre-Registered)

::include results/v02/exploratory.md

::pagebreak

# S5. Study 1 Trade-Off World: Design Check

::noindent Output of the analytic and simulated design check of the trade-off world (`results/design_check.txt`). It was run after the wall and the lowest start energy were changed from the design brief (see Section 3.6 of the article).

::code results/design_check.txt

::pagebreak

# S6. Post-Hoc Sensitivity Analyses

## S6.1 Study 2

::include results/v02/sensitivity.md

## S6.2 Study 2b

::include results/v02b/sensitivity.md

::pagebreak

# S7. Study 2b: Full Generated Report and Exploratory Analyses

::include results/v02b/report.md

::include results/v02b/exploratory.md

::pagebreak

# S8. Study 1b: Full Generated Report and Exploratory Analyses

::include results/study1b/report.md

::include results/study1b/exploratory.md

::pagebreak

# S9. Study 1: Additional Tables

{{STUDY1_TABLES}}

::pagebreak

# S10. Version-Control History

::noindent The commit history of the repository at the time this document was built (short hash, commit time in UTC−7, and message); later commits are in the public repository. Pre-registrations are `d70a2fe` (Study 2) and `3486e57` (Studies 2b and 1b). Git timestamps are set by the committing author and are not independent proof of timing. We therefore publish the full history so that the order of pre-registration, code, training and results can be inspected. One commit message (of the Study 2 pre-registration) was amended once, to repair a truncated message, before any training; the document content was not changed.

{{GITLOG}}

# S11. Software and Reproduction Commands

::noindent Software: Python 3.14.4 on WSL Ubuntu 26.04 (CPU only), MuJoCo 3.14.0, Gymnasium 1.3.0, NumPy 2.5.3, PyTorch 2.14.0 (CPU build) and Matplotlib 3.11.2. The exact versions of every package are listed in `requirements-lock.txt`, and minimum versions in `requirements.txt`. The code includes 86 automated tests (`python -m pytest`). The commands below run from the repository root and regenerate every result, table and figure.

- Study 1: `python -m experiments.run_baseline --seeds 30 --out results/` and, for robustness, `--seeds 100 --out results/seeds100`.
- Study 2 training: `bash experiments/train_all.sh` (FULL 0–4, NOEFF 0–2, NOFWD 0–2; 3 × 10⁶ steps each).
- Study 2 tests and report: `python -m experiments.run_v02`.
- Study 2b: `WORLD=agency_b OUT=results/v02b/models bash experiments/train_all.sh`, then `python -m experiments.run_v02 --models results/v02b/models --out results/v02b --world agency_b`.
- Study 1b: `WORLD=study1 OUT=results/study1b/models RUNS="FULL:0 FULL:1 FULL:2 FULL:3 FULL:4" bash experiments/train_all.sh`, then `python -m experiments.run_baseline --seeds 30 --agents --learned results/study1b/models --out results/study1b` and `python -m experiments.report_study1b`.
- Post-hoc and exploratory analyses: `python -m experiments.sensitivity_v02`, `python -m experiments.explore_v02`, `python -m experiments.explore_study1b` and `python -m experiments.necessity_check`.
- Manuscript figures (vector PDF and 600 dpi PNG): `python submission/build/make_figures.py`.
