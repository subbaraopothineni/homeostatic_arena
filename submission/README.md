# Submission package: *Artificial Life* (MIT Press)

**Paper:** "Which Behavioural Markers of Sentience and Self-Awareness Can a Simple Mechanism
Fake? Pre-Registered Tests With Homeostatic Agents"

This folder holds everything needed to submit the paper. The parts that only you can supply
are marked **`[FILL: …]`**, highlighted in yellow in the Word files, and listed in
**`CHECKLIST.md`**. Work through that checklist first.

## Where to submit, and why

**Recommended target: *Artificial Life*** (MIT Press; the journal of the International
Society for Artificial Life).
- **Scope fit.** The paper uses the core artificial-life method: building minimal synthetic agents to test what behaviour really requires. It also covers embodiment, homeostasis and self-models.
- **AI policy fits how this work was done.** *Artificial Life* allows generative AI when every use is labelled and formally cited, and the paper does both. Generative AI wrote the code and drafted the text, and many journals restrict that (see the alternatives).
- **Cost.** It is a subscription journal with an *optional* open-access fee. There is no mandatory charge.
- **Format.** Word or LaTeX is accepted. The manuscript is submitted as a PDF.

**Alternatives considered:**

| Venue | Pros | Cons |
|---|---|---|
| *Neuroscience of Consciousness* (Oxford) | Scope explicitly includes machines | Fully open access, with a charge of $2,364. Oxford's AI policy requires written permission for AI-generated content and forbids AI from doing primary authorial work, which conflicts with how this paper was produced. |
| arXiv preprint (in addition to the journal) | Free, fast, citable | A new author needs endorsement (see `07_preprint_arxiv/ARXIV_HOWTO.md`) |

## What *Artificial Life* requires, and where this package meets it

| Requirement | In this package |
|---|---|
| Article length: 6,000–12,000 words | The main text is 6,441 words (Introduction to Conclusion) |
| An abstract covering what was done, why, how, the findings and the outcome | 246 words, with no citations |
| 5–6 keywords | 6, on the title page |
| APA 7th edition citations and references | Throughout |
| The whole manuscript single-column and double-spaced, including abstract, references and captions | `01_manuscript/Manuscript.docx` (tables are single-spaced for readability) |
| Figures as vector PDF, or at least 600 dpi for line art | `02_figures/`: each figure as vector `.pdf` and as a 600 dpi `.png` |
| A cover letter with a one-page, self-contained "extended abstract" answering the journal's questions | `03_cover_letter/Cover_Letter.docx` (page 2) |
| Generative AI "prominently, explicitly and unambiguously labelled", with the source cited | The title page, the section *Use of Generative AI*, and the reference Anthropic (2026) |
| MIT Press data policy: data cited and public, with a data availability statement | The manuscript section, plus `05_code_and_data/` |
| Word or LaTeX source at acceptance | The Word files are the sources; the Markdown sources are in `build/` |

## Folder contents

| Folder or file | Contents | Upload? |
|---|---|---|
| `CHECKLIST.md` | Everything you must provide or do, in order | — |
| `01_manuscript/Manuscript.docx` | The complete manuscript: title page, abstract, text, 6 tables, 7 embedded figures with captions and alt text, declarations, references. Line-numbered and double-spaced. | **Yes** (as a PDF; see the checklist) |
| `02_figures/Figure1–7.pdf / .png` | High-resolution figure files (vector and 600 dpi) | **Yes**, if the form asks for separate figure files |
| `03_cover_letter/Cover_Letter.docx` | Cover letter and one-page extended abstract | **Yes** |
| `04_supplementary/Supplementary_Material.docx` | Pre-registrations (verbatim), full generated reports, design checks, sensitivity analyses, extra tables, version history, reproduction commands | **Yes**, as supplementary material |
| `05_code_and_data/` | Code-and-data zip, git-history bundle, citation template, and a guide to getting a DOI | Publish on GitHub/Zenodo; put the link in the paper |
| `06_declarations/` | Paste-ready text for every form field; suggested-reviewers template | Paste into the form |
| `07_preprint_arxiv/` | Preprint version, plain-text abstract, arXiv guide | Optional |
| `build/` | The scripts that produced all of the above | No |

## How to submit (summary; details in `CHECKLIST.md`)

1. Complete every item in `CHECKLIST.md`.
2. Save the manuscript as PDF (*File → Save As → PDF* in Word, or in Word for the web).
3. Go to the journal's ScholarOne site, https://mc.manuscriptcentral.com/artificiallife. Confirm the link on the [submission-guidelines page](https://direct.mit.edu/artl/pages/submission-guidelines).
4. Create an account (use your ORCID), then start a new submission:
   - article type: **Article**;
   - paste the title, abstract and keywords;
   - add the authors;
   - upload the manuscript PDF, the cover letter, the supplementary material and, if asked, the figures;
   - paste the statements from `06_declarations/`.
5. Check the PDF proof that ScholarOne builds, then submit.

## Rebuilding after edits

Edit the Markdown sources in `build/`, not the Word files. Then run, from the repository root:

```bash
python submission/build/make_figures.py        # figures (in the project's Python environment)
node submission/build/build_docs.js            # the four Word files
bash submission/build/make_archives.sh         # code-and-data archives (after committing)
```

`build_docs.js` needs Node.js with the `docx` package: run `npm install` in `build/`.
Small wording fixes can also be made directly in Word. In that case, remember that the
Markdown sources no longer match.

## Sources used for the journal requirements (checked 23 September 2026)

- *Artificial Life* submission guidelines: https://direct.mit.edu/artl/pages/submission-guidelines
- *Artificial Life* Overleaf template (article lengths, APA 7, 5–6 keywords, 600 dpi): https://www.overleaf.com/latex/templates/artificial-life-journal-submission-template/zhhhjdgvhryt
- MIT Press publication ethics (AI cannot be an author): https://direct.mit.edu/journals/pages/publication-ethics
- *Artificial Life* editorial on large language models and generative AI: https://direct.mit.edu/artl/article/29/2/141/116359/Editorial-What-Have-Large-Language-Models-and
- arXiv endorsement policy update (21 January 2026): https://blog.arxiv.org/2026/01/21/attention-authors-updated-endorsement-policy/

The guidelines page blocks automated access, so some details come from search summaries and
the official template. Before submitting, open the guidelines page yourself and check it
against this list.
