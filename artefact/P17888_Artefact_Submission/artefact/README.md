# P17888 controlled non-medical matching prototype

This is the local artefact for **AI-Based Chatbot for Personalised Non-Medical Supplement Recommendations**. It maps exact controlled phrases to a versioned SQLite dataset, applies predefined integer rules, ranks matching records deterministically and displays only stored product, recipe and explanation text.

It is an informational academic prototype—not medical advice. It does not diagnose, treat, establish suitability/safety/effectiveness, use generative AI, create accounts, store conversation history, collect personal data or perform analytics. It is not configured for public or commercial deployment.

## Requirements

- Windows with CPython 3.14.x (`py -3.14`)
- No account, API key, database server, Node toolchain or secret

The original verified runtime was CPython 3.14.6. Final submission reproduction used CPython 3.14.7. Exact direct and transitive Python packages are in `requirements-lock.txt`.

## Clean setup

From this `artefact` directory:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m pytest -q
```

The app rebuilds the ignored runtime SQLite database deterministically from `app/db/seed.curated.json` at startup. No manual database step is required.

## Run locally

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --no-access-log
```

Open `http://127.0.0.1:8000/`. The `--no-access-log` option preserves the approved log-minimisation design; application events contain only event code, duration, data version and outcome class.

Useful local endpoints:

- `/` — vanilla conversational UI
- `/api/taxonomy` — active controlled choices and disclaimer
- `/api/recommend` — strict `{ "text": "..." }` request
- `/health` — non-sensitive local health status
- `/docs` — generated API documentation

## Data and deterministic behavior

- Default demonstration data: `curated-v1`, three public-secondary product records with field-level source review.
- Regression fixture: `synthetic-v1`, kept separate from curated data.
- Generated `.sqlite3` files, caches and raw generated test output are ignored.
- The browser does not calculate recommendations and stores no request/history.
- Ranking is score descending, matched-rule count descending, then product ID ascending; maximum three results.

See `docs/SOURCE_CURATION.md`, `docs/SCORING_WORKED_EXAMPLE.md`, `docs/DATA_MODEL.md` and `evidence/EVIDENCE_INDEX.md`.

## Verification

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m scripts.run_benchmark
```

Testing uses predefined/synthetic scenarios only. No participant, survey, interview, human usability or personal-data testing was performed.

Final submission verification retains all 76 original tests and adds seven regressions (83 total). See `docs/FINAL_SUBMISSION_REPAIR.md` and `evidence/final_submission_verification.json`. The old `artefact-i08-verified` tag is historical; the separately verified final release uses `artefact-final-submission-verified`.

## Known limitations

The controlled vocabulary and curated dataset are intentionally small; exact public pages may change after the recorded access date. Static accessibility/browser checks are not a conformance certification. The prototype makes no individual or clinical assessment. See `docs/LIMITATIONS_AND_OBJECTIVES.md` for the evidence-led evaluation input.

Request boundary handling recognises configured whole phrases plus exact diagnosis/treatment noun guards. It is finite, not general medical-language understanding. Additional unrecognised wording can be ignored when a supported alias is present; only wholly unrecognised criteria produce UNSUPPORTED_INPUT. Final report claims must retain this limitation.
