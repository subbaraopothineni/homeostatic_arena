# Submission checklist

Work through the sections in order. Every **`[FILL: …]`** in the Word files is highlighted in
yellow; search for `FILL` (Ctrl+F) to find them. When you are done, no `FILL` may remain in
any file you upload.

## A. Information only you can provide

| # | Item | Where it goes |
|---|---|---|
| A1 | **Author names and order** | Manuscript title page; cover letter (signature); Supplementary title page; `CITATION.cff` |
| A2 | **Affiliation** of each author: department, institution, city, country | Manuscript title page |
| A3 | **ORCID iD** for each author (free at https://orcid.org) | Manuscript title page; submission form |
| A4 | **Corresponding author:** postal address and e-mail | Manuscript title page; cover letter |
| A5 | **Funding:** funder and grant number, or "no specific grant" | Manuscript *Funding*; form |
| A6 | **Competing interests**, or "none" | Manuscript; form |
| A7 | **Author contributions** (CRediT roles) | Manuscript; form |
| A8 | **Acknowledgements**, or "None" | Manuscript |
| A9 | **What you personally verified.** One or two true sentences, for example "I read all analysis code, re-ran Study 1, and checked every number and reference against the result files and sources." | Manuscript *Use of Generative AI*; form |
| A10 | **Repository URL, DOI and licence** (from step B1 and `05_code_and_data/HOWTO_GitHub_Zenodo.md`) | Manuscript *Data and Code Availability*; cover letter; form |
| A11 | **Date** of submission | Cover letter |
| A12 | (Optional) *Artificial Life* journal papers you consider closest to this work | Extended abstract, "Research built upon" |
| A13 | (Optional) Suggested and excluded reviewers | `06_declarations/Suggested_Reviewers.md`; form |
| A14 | (Optional) Preprint link, if you post one | Cover letter; form |

## B. Decisions

- [ ] **B1. Licence** for the code and data (for example MIT for code and CC BY 4.0 for data), and publication of the repository. See `05_code_and_data/HOWTO_GitHub_Zenodo.md`, including the note that the git history shows the e-mail address `cloudataarchitect83@gmail.com`.
- [ ] **B2. Preprint:** yes or no, and when. See `07_preprint_arxiv/ARXIV_HOWTO.md`. New arXiv authors need an endorser.
- [ ] **B3. Open access.** *Artificial Life* offers optional open access for a fee, and this is usually decided at acceptance. There is no charge to submit.

## C. Verification: your responsibility as the author

Generative AI produced the code, analyses and draft. The journal and arXiv hold the authors
fully responsible for every claim, so do the following before you submit.

- [ ] **C1. Read the whole manuscript and supplement.** Make sure you understand, agree with and can defend every claim. Reviewers will ask about the methods and statistics.
- [ ] **C2. Check the numbers.** Every number in the text comes from these files:
  - Study 1: `results/summary.csv` and `results/seeds100/summary.csv`;
  - Study 2: `results/v02/report.md`, `exploratory.md` and `sensitivity.md`;
  - Study 2b: `results/v02b/report.md`;
  - Study 1b: `results/study1b/report.md`.
- [ ] **C3. Check the references.** Open each DOI, and confirm the authors, year, title and journal. They were checked online on 23 September 2026. Pay particular attention to Solms et al. (2026), which has no DOI in the list; add one if the journal page shows it.
- [ ] **C4. Re-run something yourself.** At minimum, run `python -m pytest` (86 tests) and `python -m experiments.run_baseline --seeds 30 --out /tmp/check` (about a minute; it reproduces Study 1). Compare the output with `results/summary.csv`.
- [ ] **C5. Open the Word files** (`Manuscript.docx`, `Cover_Letter.docx`, `Supplementary_Material.docx`) and look through every page. The files pass Office-schema validation, but they could not be rendered on this machine. Check that:
  - figures appear near their first mention;
  - tables fit the page;
  - line numbers and page numbers show.
- [ ] **C6. Extended abstract length.** The cover letter's extended abstract must fit on **one page**. If it runs over, shorten it.
- [ ] **C7. Read the official guidelines page yourself:** https://direct.mit.edu/artl/pages/submission-guidelines. The page blocks automated access, so the requirements in `README.md` were assembled from search summaries and the official Overleaf template. Look for anything new: blinding, file types, statements.
- [ ] **C8. No `FILL` left** in any file you upload (Ctrl+F `FILL`).

## D. Submitting on ScholarOne

1. **Convert to PDF.** Open `01_manuscript/Manuscript.docx` in Word or Word for the web, then choose *File → Save As → PDF*. Do the same for the cover letter and the supplementary material if the form asks for PDFs.
2. **Open** https://mc.manuscriptcentral.com/artificiallife and confirm the link on the guidelines page. Create an account, preferably linked to your ORCID.
3. **Start a new submission:**
   - type **Article**;
   - title, abstract and keywords (from `06_declarations/Declarations_for_submission_form.md`);
   - authors and affiliations.
4. **Upload:**
   - the manuscript PDF, marked as the main document;
   - the cover letter;
   - `Supplementary_Material` (supplementary file);
   - the figures from `02_figures/`, if separate figure files are requested (use the `.pdf` vector versions, or the 600 dpi `.png`).
5. **Paste the statements** from `06_declarations/`:
   - generative-AI use;
   - data availability;
   - competing interests;
   - funding;
   - ethics;
   - CRediT roles;
   - originality.
6. **If the form asks for a blinded manuscript** (not expected for this journal), make a copy. Remove the author block from the title page, and the repository URL, before converting it to PDF.
7. **Check** the PDF proof that the system builds, then **submit**. Save the confirmation e-mail.

## E. After submission

- Do not change the published repository release that the paper cites. Put later changes in a new release.
- Keep `submission/build/` so that you can rebuild the documents quickly during revision (see `README.md`, "Rebuilding after edits").
- When reviews arrive, answer every point in a response letter, and mark the changes in the revised manuscript.
