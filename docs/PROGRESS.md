# Progress

## Repository and foundation

- Workspace inspected: no existing source files to preserve.
- GitHub account verified as `cadmieldubic`; private repository created at `https://github.com/cadmieldubic/doodlesteps` with ADMIN permission.
- Local Git initialized on `main`; HTTPS `origin` configured.
- Required docs, scene/API contract, environment template, and safe ignores added.
- Network permission and `.git` write permission granted for the requested operations.

## Implemented

- FastAPI endpoints, strict finite numeric vector models, JSON trust-boundary revalidation, unique IDs, complexity limits, and a safe OpenAI two-stage structured vision/drawing pipeline.
- Bounded memory-only multipart uploads, actual MIME/content/pixel/animation validation, orientation correction and metadata-free1280px JPEG preprocessing.
- Safe provider errors, generation deadlines, bounded rate/concurrency controls, foreign-origin rejection before paid work, no-store headers, and restricted local CORS.
- Hand-authored puppy36/flower29/house31-stroke demos, each with six progressive groups and encouraging instructions.
- Responsive React workbook, finished/guide views, immutable cumulative geometry, previous/new/individual stroke emphasis, line reveal, navigation/thumbnails, completion/restart, original-photo reference, and printable worksheet.
- Photo/camera selection, preview/replace/remove, missing-key guidance, decode validation/timeout, request cancellation, and stale-photo/result race protection. No demo substitutes for an uploaded photo.
- Exact setup/run/verification scripts, pinned dependency files, workspace-local caches and test artifacts, API/architecture docs, and ten-photo evaluation checklist.
- Private CI workflow with read-only repository permission; no live credentials and no deployment.

## Remaining verification

Complete CI browser execution and final visual polish, then record final commit/push/PR state. Actual live photo generation/recognizability requires a privately configured API key and the ten-photo evaluation; no key has been exposed or fabricated.

## Limitations

No live API credentials have been configured or requested in chat. Live AI visual quality requires a later private `.env` configuration and ten-photo evaluation. No deployment is authorized.

Local Playwright Chromium startup is blocked by macOS Mach IPC restrictions in the Codex terminal sandbox (not a filesystem permission issue). The local command was attempted with one-failure cutoff:1 launch failure,17 cases did not run. The supported in-app browser is used for manual checks; private GitHub Linux CI is configured to run all18 cases. No broad disk access has been requested.

`ai_available` reports key configuration only, not successful provider authorization. Unsuitable/personal-photo classification is AI instructed and still needs live validation. Hardware camera capture and physical printing remain device-dependent.

## Checks run so far

- Pytest:141 passed; includes real SDK parsing over mocked HTTP transport, no paid calls.
- Python Ruff and compilation:passed. Two non-failing test warnings are recorded (upstream Starlette/httpx deprecation; deliberately invalid Pydantic fixture).
- Vitest:26 passed, including upload/result replacement races and no demo fallback.
- TypeScript, ESLint, and Vite production build:passed. Bundle about315KB JS (93KB gzip),29KB CSS (7.5KB gzip).
- Bash syntax and Git whitespace checks:passed.
- Local HTTP health/config/demos:200; no-key config correctly false.
- In-app browser:all puppy steps, reveal, prior-stroke accumulation (2,8,13,19,28,36), completion and restart passed; finished scenes visually reviewed.375px lesson has48px controls;320px/375px layouts showed no horizontal overflow. Latest instructional text verified16px with improved contrast.

## Milestone records

Records will include commit, branch, verified push state, actual tests, and next task.

### Milestone 1 — verified

- Commit `4c85ebec5e3b7a4b707555366641c81b8bc42841`, branch `main`.
- Push succeeded; `git ls-remote origin refs/heads/main` matched local HEAD. GitHub confirmed PRIVATE visibility and default branch `main`.
- Checks: staged whitespace check; `.gitignore` matched root/backend `.env`, Python virtualenv, node_modules, build output, and scratch image paths.
- No application tests were applicable before application source existed.
- Next task: implement and test vector engine, demo lessons, and tutor UI on `feat/drawing-tutor`.
