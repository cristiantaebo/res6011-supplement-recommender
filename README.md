# AI-Based Chatbot for Personalised Non-Medical Supplement Recommendations

[Source code](https://github.com/cristiantaebo/res6011-supplement-recommender)

**Live application: not deployed or verified yet.** A hosting account and its no-additional-cost configuration must be verified first. No static page is presented as a working recommendation service.

This P17888 software prototype uses a real Python/FastAPI backend, SQLite, and vanilla HTML/CSS/JavaScript. Controlled phrases select predefined criteria; integer rules rank stored product records and return stored explanations. There is no LLM or generated recommendation content.

This is an informational, non-medical academic demonstration, not a health assessment, clinical service or commercial product. It cannot establish individual suitability, safety or effectiveness. Do not enter personal information, symptoms or medical details. Its boundary patterns are finite, not comprehensive medical-language recognition.

## Software layout

- [`artefact/P17888_Artefact_Submission/artefact/`](artefact/P17888_Artefact_Submission/artefact/) — selected original software files, with original relative paths and exact bytes.
- [`SOFTWARE_FILES_SHA256.json`](SOFTWARE_FILES_SHA256.json) — SHA-256 and source-path mapping for all 38 admitted original files.
- [`SOFTWARE_PROVENANCE.md`](SOFTWARE_PROVENANCE.md) — public-subset boundary and provenance.
- [`deployment/`](deployment/) and [`render.yaml`](render.yaml) — separate hosting configuration; not part of the frozen release.

The complete original submission ZIP is retained privately. It also contains academic governance/report handoff material and is **not** uploaded here or silently rebuilt. This repository is a software-only subset, not an identical copy of all 81 files in that ZIP. It contains no dissertation, declaration, correspondence, university teaching documents or private academic audits.

## Run locally

Use CPython 3.14.x and an isolated virtual environment. From the selected original software directory:

```powershell
cd artefact/P17888_Artefact_Submission/artefact
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --no-access-log
```

Open `http://127.0.0.1:8000/`. Startup builds an ignored SQLite database from the unchanged curated seed. Requests use read-only database access. The independent synthetic fixture is also preserved.

An example supported request is `mixable option vegetarian labelled powder`. Other controlled cases include `tablet option` (no match), `portable option` (ambiguous), `unlisted criterion` (unsupported), and `mixable option diagnosis` (boundary). These describe existing behavior, not new test results from this publication task.

The original [README](artefact/P17888_Artefact_Submission/artefact/README.md) is retained unchanged as historical software documentation. Its references to local operation and 83-test release verification describe the complete canonical release, not a newly verified public test total. Two files that check academic/package evidence, the associated private evidence and report-related documents are excluded. The eight admitted test files are unchanged. No historical test suite or benchmark was rerun for source publication.

## Online demonstration configuration

The prepared Render configuration runs the **whole original application on one Python host**. The UI and API remain on the same HTTPS origin; GitHub Pages is not used as a pretend Python backend. The separate ASGI adapter only selects the original code path and a temporary demonstration database path. It does not replace or modify the matching engine, data, API contracts or interface.

The intended compute plan is Render Free, with no database service or persistent disk. Account-level cost/usage settings must still be verified before creating it. Free services can sleep after inactivity; their SQLite runtime file is ephemeral and is reconstructed from the original seed. No keep-alive pings are configured. See [deployment instructions and limitations](deployment/README.md).

The frozen interface retains its original local-prototype wording. On an online copy, requests would be sent to its remote Python host, and that provider may retain technical access logs. The application has no accounts, history, analytics or raw-input logging; this is not a promise of zero hosting-provider logs. No additional data collection is configured.

No new licence, redistribution permission, authorship claim or institutional endorsement is asserted. Existing source notes and attributions remain unchanged. Public source can be read and copied; visitors are not granted write access to this repository.
