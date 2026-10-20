# Isolated online demonstration configuration

**Status: live on Render Free; anonymous UI/API smoke checks passed on 20 October 2026.**

[Open live application](https://p17888-res6011-software-demo.onrender.com)

## Render service configuration

- Source: this public repository, branch `main`.
- Root directory: repository root (leave the Render root-directory field empty).
- Runtime: Python 3.14.8; original package constraints require Python >=3.14,<3.15.
- Compute plan: explicitly **Free**; do not accept a paid default.
- Build: `python -m pip install -r artefact/P17888_Artefact_Submission/artefact/requirements-lock.txt`.
- Start: `python -m uvicorn deployment.asgi:app --host 0.0.0.0 --port $PORT --workers 1 --no-access-log`.
- Health path: `/health`.
- No persistent disk, external database, paid add-on, analytics, new domain, login feature or keep-alive job.

`render.yaml` records these values. The new service's Free plan and settings were read back after creation. Auto-deploy is disabled. Account-level overage behavior cannot be inferred merely from `plan: free`; review billing before future changes and do not upgrade automatically. No existing service or billing plan was changed for this demonstration.

## Data and origin

The ASGI adapter imports the original `app.main.create_app` and original seed. Lifespan creates a separate SQLite file under the host's temporary directory. Repository queries remain read-only. The file can disappear on restart or sleep and is rebuilt at the next startup; no persistence of user data is intended or claimed.

The original UI, assets and API share one HTTPS origin. A separate GitHub Pages frontend is unnecessary for this option. No fake recommendation endpoint, wildcard CORS or rewrite of the engine is added. HTTPS is provided by the host.

## Limits and privacy

Render Free services sleep after 15 minutes without inbound traffic and can take approximately one minute to wake. Runtime storage is ephemeral. Free compute has monthly instance-hour and other usage limits. Supplementary bandwidth/build charges can depend on account payment/spend configuration. Verify the actual account before deploying; never upgrade automatically.

Do not enter real personal or medical information. The frozen UI retains local-prototype wording; a hosted copy would send requests to the remote backend. The app does not store conversations or log raw input, but a hosting provider can retain technical/IP/access logs. No claim of clinical safety, usability-study results or public-service reliability is made.

## Verification and future redeploys

The accepted verification used a fresh anonymous/headless browser against the real HTTPS URL: `/health`, `/api/taxonomy`, original HTML/CSS/JS bytes, supported requests and explanation, reset, no match, ambiguity, unsupported input, both configured diagnosis/treatment noun boundaries, strict malformed-input rejection, keyboard focus and no horizontal overflow at 320/390/1280 pixels. There were zero relevant browser/CORS errors. Canonical responses before/after the other smoke cases had the same SHA-256. No claim of direct inspection of the live temporary SQLite file is made.

Recheck the affected flow after a future authorized redeploy. These are deployment smoke checks, not a rerun or extension of the historical 83 tests. Do not rerun benchmarks or take thesis screenshots as part of this publication task.

Root README and repository homepage link to the verified live URL. A successful build alone was not treated as application verification.

## Stop/remove only the new demonstration

The new service is named `p17888-res6011-software-demo`. Its exact service/workspace identifiers are retained in the private control audit. Before a later stop/removal, verify the service's identity and source repository. Use that service's Render settings to suspend it, or delete only that new service after explicit user authorization. Do not identify deletion targets by a guessed name, and do not delete the canonical software, thesis, GitHub repository or other hosting projects. No stop or deletion was performed for this delivery.

Official references: [FastAPI deployment](https://render.com/docs/deploy-fastapi), [Python versions](https://render.com/docs/python-version), [Blueprint specification](https://render.com/docs/blueprint-spec), [Free plan limits](https://render.com/docs/free).
