# Software provenance

## Canonical private source

- Archive: `P17888_Artefact_Submission.zip`.
- SHA-256: `ba4e5b3c8f9364b4e2eb44ac56ddb85e70459c876a8524fa9f8b3d897901cd4b`.
- Size: 1,329,825 bytes; 81 files, 80 internal checksums.
- Original final release commit: `8a17fe65bce2121e76571fe2938ab7c930a0274f`.
- Original final tag: `artefact-final-submission-verified`.

The public import commit is a new commit and is **not** the original release commit. No original Git history is imported. Original release tags and the local archive are unchanged.

## Explicit software-only selection

38 original files are admitted, each byte-for-byte identical to the archive. For every admitted entry, mapping is:

`<original archive path>` → `artefact/<original archive path>`.

Thus the archive's `P17888_Artefact_Submission/artefact/` directory remains nested, rather than being flattened. The complete admitted paths, sizes and hashes are in `SOFTWARE_FILES_SHA256.json`.

Included categories are the entire application/static UI/schema/seeds/source inventory, original package/runtime descriptors and README, five technical design/data/UI documents, eight original code-test files, and two original benchmark/checkpoint scripts. Scripts are published as source, not executed as part of this import.

43 original entries are not published. Academic governance, report handoff, mixed academic audit documents, release packaging/evidence material and screenshots are not required to run the software. Two original test files that also check the private academic/package evidence are excluded rather than edited or represented as runnable proof without their dependencies. The complete original suite and all source originals remain preserved privately. The historical release total is 83 tests; no new 83-test pass or public-subset test total is claimed.

Some unchanged original documentation and data-provenance fields refer to those local evidence files. A reference is not an assertion that the referenced private document has been published. Original technical documents can describe the older local configuration; deployment differences are stated separately below.

The original ZIP itself is not publicly downloadable here because it contains excluded academic material. No altered archive has been given its filename or checksum. GitHub's generated source-code download is a download of this public subset, not the canonical submission ZIP.

## Separate deployment additions

- `deployment/asgi.py`: imports `create_app` from the unchanged snapshot; selects an isolated temporary SQLite path outside the snapshot. Original startup validation/construction, read-only request access, API, ranking, boundary rules, stored outputs and UI are retained.
- `deployment/README.md`: configuration, limits, verification and shutdown guidance for a future isolated demonstration.
- `render.yaml`: one Free Python web service, locked dependencies, one Uvicorn worker, platform host/port, disabled Uvicorn access log and health path. No disk, paid service, database migration, account, history or analytics resource is requested.
- Root documentation/manifest and Git attributes/ignore settings: publication controls, not changes to original files.

The whole-app same-origin option avoids modifying the frontend for a Pages subpath or different API URL and avoids unnecessary CORS middleware. The isolated demonstration is available at https://p17888-res6011-software-demo.onrender.com. Anonymous headless-browser checks on 20 October 2026 confirmed the actual UI/API flow, predefined output fields, reset and controlled outcome cases. Original HTML/CSS/JS served by the host were compared byte-for-byte with the snapshot. This is deployment evidence, not a new result for the historical 83-test suite or a hosting performance benchmark.

Data-integrity evidence consists of unchanged source/seed hashes, original read-only request access and matching canonical response hashes before and after smoke scenarios. A direct hash of the running host's temporary database file was not measured; no SSH/admin/file-reading endpoint was added to obtain it.

The original interface describes a local prototype. A hosted demonstration sends input to the remote host, which can produce infrastructure logs. That distinction does not change the original application bytes and must not be hidden in evaluation of an online copy.

No new licence is added; existing attribution and data use notes remain unchanged. This technical provenance document does not certify legal permissions, academic authorship, ethics extensions or submission compliance.
