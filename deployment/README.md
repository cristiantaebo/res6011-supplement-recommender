# Isolated online demonstration configuration

**Status: configuration prepared; no hosting service or live URL has been created or verified.**

## Intended Render service

- Source: this public repository, branch `main`.
- Root directory: repository root (leave the Render root-directory field empty).
- Runtime: Python 3.14.8; original package constraints require Python >=3.14,<3.15.
- Compute plan: explicitly **Free**; do not accept a paid default.
- Build: `python -m pip install -r artefact/P17888_Artefact_Submission/artefact/requirements-lock.txt`.
- Start: `python -m uvicorn deployment.asgi:app --host 0.0.0.0 --port $PORT --workers 1 --no-access-log`.
- Health path: `/health`.
- No persistent disk, external database, paid add-on, analytics, new domain, login feature or keep-alive job.

`render.yaml` records these values. Do not create a service until the authenticated account, intended workspace, free allocation and supplementary-usage/spend settings have been checked. Account-level overage behavior cannot be inferred merely from `plan: free`. Do not change any existing service or billing plan.

## Data and origin

The ASGI adapter imports the original `app.main.create_app` and original seed. Lifespan creates a separate SQLite file under the host's temporary directory. Repository queries remain read-only. The file can disappear on restart or sleep and is rebuilt at the next startup; no persistence of user data is intended or claimed.

The original UI, assets and API share one HTTPS origin. A separate GitHub Pages frontend is unnecessary for this option. No fake recommendation endpoint, wildcard CORS or rewrite of the engine is added. HTTPS is provided by the host.

## Limits and privacy

Render Free services sleep after 15 minutes without inbound traffic and can take approximately one minute to wake. Runtime storage is ephemeral. Free compute has monthly instance-hour and other usage limits. Supplementary bandwidth/build charges can depend on account payment/spend configuration. Verify the actual account before deploying; never upgrade automatically.

Do not enter real personal or medical information. The frozen UI retains local-prototype wording; a hosted copy would send requests to the remote backend. The app does not store conversations or log raw input, but a hosting provider can retain technical/IP/access logs. No claim of clinical safety, usability-study results or public-service reliability is made.

## Required verification after hosting authorization

Use a fresh anonymous/headless browser against the real HTTPS URL. Check `/health`, `/api/taxonomy`, CSS/JS, a supported request and explanation, reset, no match, ambiguity, unsupported input and configured medical-boundary response. Confirm actual frontend → API → unchanged engine/data behavior and no relevant console/CORS errors. These are deployment smoke checks, not a rerun or extension of the historical 83 tests. Do not rerun benchmarks or take thesis screenshots.

Only after these checks should root README and repository homepage contain the actual live URL. A successful build alone is insufficient.

## Stop/remove only the new demonstration

No service ID exists yet. Once a new service is created, record its exact ID/workspace and verify the source repository before acting. To stop it later, use that service's Render settings to suspend it, or delete only that new service after explicit user authorization. Do not identify deletion targets by a guessed name, and do not delete the canonical software, thesis, GitHub repository or other hosting projects.

Official references: [FastAPI deployment](https://render.com/docs/deploy-fastapi), [Python versions](https://render.com/docs/python-version), [Blueprint specification](https://render.com/docs/blueprint-spec), [Free plan limits](https://render.com/docs/free).
