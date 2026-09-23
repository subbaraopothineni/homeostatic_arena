# Publishing the code and data (GitHub + Zenodo DOI)

*Artificial Life* follows the MIT Press research-data policy. All data behind the
findings must be cited and made publicly available where possible, and a Data
Availability Statement is strongly encouraged. The manuscript already contains one,
with three `[FILL]` markers: the repository URL, the DOI and the licence. This page
explains how to get those three things.

## What is in this folder

| File | What it is |
|---|---|
| `homeostatic_arena_code_data.zip` | All code, tests, documentation, pre-registrations, trained models, raw data and result tables, as committed (no virtual environments or build tools). About 35 MB (47 MB unpacked). |
| `homeostatic_arena_history.bundle` | The complete git history in one file, including the pre-registration commits cited in the paper (`d70a2fe`, `3486e57`). Anyone can restore it with `git clone homeostatic_arena_history.bundle`. |
| `CITATION.cff.template` | Citation metadata for GitHub and Zenodo. Fill it in and copy it to the repository root as `CITATION.cff`. |
| `HOWTO_GitHub_Zenodo.md` | This page. |

Both archives are rebuilt by `bash submission/build/make_archives.sh` after any new commit.

## Before you publish: two decisions

1. **Licence.** This is your decision; the repository currently has no licence. A common choice is:
   - **MIT** for the code;
   - **CC BY 4.0** for the data, results and documents.

   On GitHub, choose *Add file → Create new file*, name it `LICENSE`, then click *Choose a license template*. Add a sentence to the README about the data licence.
2. **E-mail address in the history.** Every commit records its author as
   `v-pothinenis <cloudataarchitect83@gmail.com>`. Publishing the repository makes that
   address public.
   - **Do not rewrite the history to change it.** The paper cites commit hashes as proof of pre-registration, and rewriting the history changes every hash.
   - If the address must not be public, tell the editor, and publish the zip only (it contains no author e-mail). You then lose the checkable pre-registration timestamps.

## Option A (recommended): GitHub + Zenodo release

1. Create an empty **public** repository on GitHub, for example `homeostatic_arena`. Do not add a README or licence yet.
2. Push the existing history from the repository root:

   ```bash
   git remote add origin https://github.com/<your-account>/homeostatic_arena.git
   git push -u origin main
   ```

3. Add the `LICENSE`, and the filled-in `CITATION.cff`, in the root of the repository.
4. Go to https://zenodo.org, log in with GitHub, open *Account → GitHub*, and switch the repository **on**.
5. On GitHub, create a **release** (*Releases → Draft a new release*), for example with tag `v1.0-submission`. Zenodo archives it automatically and assigns a **DOI**.
6. Copy the repository URL, DOI and licence into:
   - the manuscript: *Data and Code Availability*;
   - the cover letter;
   - `06_declarations/Declarations_for_submission_form.md`.

## Option B: Zenodo upload only

On https://zenodo.org, choose *New upload* and upload both files in this folder.
- **Resource type:** Software, or Dataset.
- **Licence:** your choice.
- **Authors:** the same as the paper.

Publish the record to get the DOI. You can reserve the DOI first (*Reserve DOI*) and put it in the manuscript before publishing.

## Tip

Keep the record open for reviewers. Some reviewers try to reproduce the results with the
commands in Supplementary Material, Section S11. `requirements-lock.txt` pins the exact
package versions that produced the results.
