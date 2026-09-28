# Modelling Financial Markets (MFM) / Modelarea piețelor financiare

Master's course, Faculty of Cybernetics, Statistics and Economic Informatics,
Bucharest University of Economic Studies. Instructor: Daniel Traian Pele.

Course website: https://danpele.github.io/MFM/ (EN) · https://danpele.github.io/MFM/index_ro.html (RO)

## Structure

| Path | Content |
|---|---|
| `index.html`, `index_ro.html` | Course website (EN / RO), rendered from `assets/course-data.js` |
| `assets/showcase.js` | Key formulas (grouped by theme) and the chart gallery on the home page |
| `assets/quizzes/<id>.js` | Quiz question banks (EN + RO), one file per chapter id |
| `EN/Courses`, `RO/Cursuri` | Lecture slides (Beamer) |
| `EN/Seminars`, `RO/Seminarii` | Seminar slides (Beamer) |
| `latex/preamble.tex` | Shared Beamer preamble (same design as SFM / TSA) |
| `notebooks/EN`, `notebooks/RO` | Lecture and seminar notebooks (Colab-ready) |
| `Quantlets/Ch_NN` | Quantlets: one folder per chart, with `Metainfo.txt` and a self-contained notebook |
| `charts/` | Charts used in the slides (PDF + PNG, transparent) |
| `project/EN`, `project/RO` | Templates for the team project: `AI_USE.md`, `AI_ERRORS.md` |
| `data/market/` | Daily market series used by the charts and notebooks (see `data/manifest.csv`) |

## Rebuilding Chapter 13

```bash
cd Quantlets/Ch_13
python3 generate_all_charts.py      # all ch13_* charts (about 10 minutes)
python3 build_quantlets.py          # Quantlet folders
cd ../../notebooks && python3 build_notebooks.py
cd ../EN/Courses && pdflatex chapter13_machine_learning.tex   # run twice
```

## Quiz login

The quizzes require "Sign in with Google" with an ASE account (@ase.ro / @stud.ase.ro).
`assets/config.js` holds the OAuth client ID (Google Cloud project "MFM Quiz Login") and the URL of the
Apps Script web app that verifies the Google token and writes each score to the instructor's Google Sheet
(the script is kept outside this repository).

## Data

- Charts, Quantlets and notebooks read the saved files in `data/` (locally or from the GitHub raw URL).
- Public macro and on-chain series are read online directly in the code.

## Student vs instructor material

- Seminar slides: each `.tex` builds the **student** PDF (no results, linked on the site); the `*_solutions.tex` wrapper builds the **instructor** PDF.
- Seminar notebooks: after building and executing them, run `python3 notebooks/split_seminar_notebooks.py` (chapters 1 and 13; chapter 0 is split by `build_notebooks_ch0.py`). The full notebook is kept as `*_solutions.ipynb`; the student notebook keeps the tasks and setup cells, with empty cells instead of solutions.
- All `*_solutions.*` files are git-ignored and are not published.
