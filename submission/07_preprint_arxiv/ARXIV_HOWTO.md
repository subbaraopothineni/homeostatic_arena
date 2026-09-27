# Posting a preprint on arXiv (optional)

A preprint makes the work public and citable while the journal reviews it. Posting one is
your decision, and it is not required for submission.

## Files in this folder

| File | Use |
|---|---|
| `Preprint.docx` | The manuscript without line numbers and at 1.15 spacing. Fill in the same `[FILL]` values as the manuscript, then save as PDF. |
| `abstract_plain.txt` | The abstract as plain text (about 1,700 characters; arXiv's limit is 1,920), for the arXiv abstract field. |

## 1. Check the journal's preprint policy first

Before posting, read the "preprint" wording on the *Artificial Life* submission-guidelines
page (https://direct.mit.edu/artl/pages/submission-guidelines). If it is unclear, ask the
editorial office. Most MIT Press journals accept manuscripts that have been posted as
preprints, but we could not confirm this for *Artificial Life*, because the page blocks
automated access. If you post, say so in the cover letter; there is a `[FILL]` for it.

## 2. Endorsement (required for new arXiv authors)

arXiv changed its policy on 21 January 2026
(https://blog.arxiv.org/2026/01/21/attention-authors-updated-endorsement-policy/):
- A first-time submitter needs **endorsement from an established arXiv author** in the same endorsement domain.
- An institutional e-mail address alone is no longer enough.
- arXiv staff cannot endorse you.
- A submission that needs endorsement but lacks it is held, not rejected.

To get endorsed:
1. Create your arXiv account.
2. Start the submission in your primary category. arXiv then shows an endorsement code.
3. Send the code to someone who has published on arXiv in that domain and knows your work, for example a supervisor, co-author or colleague.

Endorsement domains follow the top-level archives. Endorsement in computer science (`cs.*`)
does not count for quantitative biology (`q-bio.*`).

## 3. Categories (suggested)

- **Primary:** `cs.AI` (Artificial Intelligence), or `cs.NE` (Neural and Evolutionary Computing).
- **Cross-list:** `q-bio.NC` (Neurons and Cognition), and optionally `cs.RO` (Robotics).

## 4. Licence

For a paper that will be published in a journal later, the safest choice is arXiv's
default: the **arXiv.org perpetual, non-exclusive licence**. It does not conflict with a later
copyright or licence agreement with the journal. A CC BY 4.0 licence is more open, but it
cannot be withdrawn later, so check the journal's terms before choosing it.

## 5. Generative AI

arXiv holds the authors fully responsible for everything in a submission, including any
text or results produced with generative AI:
- AI tools cannot be authors.
- AI use should be disclosed. The manuscript already does this.
- Content that the authors have not checked can be removed by moderators.

Read the whole paper and verify every number and reference before posting (see
`../CHECKLIST.md`).

## 6. Submission steps

1. Fill in `Preprint.docx` (all `[FILL]` markers), then save it as PDF: in Word, choose *File → Save As → PDF*. arXiv accepts PDF files that were not produced from TeX.
2. Go to https://arxiv.org/submit, then:
   - choose the licence and the primary category;
   - upload the PDF;
   - enter the metadata: title, authors and the abstract from `abstract_plain.txt`.
3. **Comments** field, for example: "<N> pages, 7 figures, 7 tables. Submitted to Artificial Life. Code and data: <URL/DOI>".
4. Check the preview and submit. The paper normally appears within one or two working days.
5. Add the arXiv link to the cover letter and to the submission form.
