# Progress

## Repository and foundation

- Workspace inspected: no existing source files to preserve.
- GitHub account verified as `cadmieldubic`; private repository created at `https://github.com/cadmieldubic/doodlesteps` with ADMIN permission.
- Local Git initialized on `main`; HTTPS `origin` configured.
- Required docs, scene/API contract, environment template, and safe ignores added.
- Network permission and `.git` write permission granted for the requested operations.

## Implemented

- FastAPI endpoints, strict finite numeric vector models, JSON trust-boundary revalidation, unique IDs, complexity limits, and a safe OpenAI two-stage structured vision/drawing pipeline.
- Bounded memory-only multipart uploads, actual MIME/content/pixel/animation validation, orientation correction and metadata-free 1280px JPEG preprocessing.
- Safe provider errors, generation deadlines, bounded rate/concurrency controls, foreign-origin rejection before paid work, no-store headers, and restricted local CORS.
- Hand-authored demos: puppy 36 strokes, flower 29, house 31; each has six progressive groups and encouraging instructions. Visual polish removed flower petal intersections and attached the puppy's torso to its head.
- Responsive React workbook, finished/guide views, immutable cumulative geometry, previous/new/individual stroke emphasis, line reveal, navigation/thumbnails, completion/restart, original-photo reference, and printable worksheet.
- Photo/camera selection, preview/replace/remove, missing-key guidance, decode validation/timeout, request cancellation, and stale-photo/result race protection. No demo substitutes for an uploaded photo.
- Exact setup/run/verification scripts, pinned dependency files, workspace-local caches and test artifacts, API/architecture docs, and ten-photo evaluation checklist.
- Private CI workflow with read-only repository permission; no live credentials and no deployment.

## Remaining live evaluation

Implementation and automated verification are complete. Actual live photo generation/recognizability requires a privately configured API key and the ten-photo evaluation; no key has been exposed or fabricated. Physical camera capture, paper drawing by a child, and physical printer output still need device/user evaluation.

## Limitations

No live API credentials have been configured or requested in chat. Live AI visual quality requires a later private `.env` configuration and ten-photo evaluation. No deployment is authorized.

Local Playwright Chromium startup is blocked by macOS Mach IPC restrictions in the Codex terminal sandbox (not a filesystem permission issue). The local command was attempted with one-failure cutoff: 1 launch failure, 17 cases did not run. Private GitHub Linux CI successfully ran all 18 cases; the supported in-app browser also supplied manual checks. No broad disk access has been requested.

`ai_available` reports key configuration only, not successful provider authorization. Unsuitable/personal-photo classification is AI instructed and still needs live validation. Hardware camera capture and physical printing remain device-dependent.

## Checks run so far

- Pytest:141 passed; includes real SDK parsing over mocked HTTP transport, no paid calls.
- Python Ruff and compilation:passed. Two non-failing test warnings are recorded (upstream Starlette/httpx deprecation; deliberately invalid Pydantic fixture).
- Vitest:26 passed, including upload/result replacement races and no demo fallback.
- TypeScript, ESLint, and Vite production build:passed. Bundle about315KB JS (93KB gzip),29KB CSS (7.5KB gzip).
- Bash syntax and Git whitespace checks:passed.
- Local HTTP health/config/demos:200; no-key config correctly false.
- In-app browser: all three demos completed; puppy reveal, accumulation (2, 8, 13, 19, 28, 36), completion and restart passed. Finished scenes were visually reviewed. At 375px, lesson controls measured 48px; 320px/375px layouts showed no horizontal overflow. Latest instructional text verified at 16px with improved contrast. Local photo preview/removal and disabled no-key generation passed.
- Private Linux CI: 141 backend tests, 26 frontend tests, 18 desktop/mobile Playwright tests, lint, TypeScript, Python compilation, and production build all passed in [run 37988321250](https://github.com/cadmieldubic/doodlesteps/actions/runs/37988321250).

## Milestone records

Records will include commit, branch, verified push state, actual tests, and next task.

### Milestone 1 — verified

- Commit `4c85ebec5e3b7a4b707555366641c81b8bc42841`, branch `main`.
- Push succeeded; `git ls-remote origin refs/heads/main` matched local HEAD. GitHub confirmed PRIVATE visibility and default branch `main`.
- Checks: staged whitespace check; `.gitignore` matched root/backend `.env`, Python virtualenv, node_modules, build output, and scratch image paths.
- No application tests were applicable before application source existed.
- Next task: implement and test vector engine, demo lessons, and tutor UI on `feat/drawing-tutor`.

### Milestone 2 — verified and pushed

- Commit `ffd7bee3a224c2cbd52cdb634b7e3f572ec902c3`, branch `feat/drawing-tutor`.
- Push succeeded and `git ls-remote origin refs/heads/feat/drawing-tutor` matched HEAD.
- Local checks: 141 backend tests; 26 frontend tests; Ruff, Python compilation, TypeScript, ESLint, production build, Bash syntax, staged whitespace/secret-path checks passed.
- Browser suite passed in private Linux CI (18 tests) after the narrow local process restriction was identified. Demo scenes also visually reviewed in the in-app browser and as numeric-scene renders.
- Next task: finalize verification documentation and open the review PR.

### Milestone 3 — integration and delivery

- Two-stage real SDK parsing verified with mocked HTTP responses; API/frontend integration and all three demos verified against the real backend in desktop/mobile Chromium CI.
- Upload replacement races and foreign-origin paid-work trigger fixed and regression-tested. No live API credentials were used.
- Actual setup/run instructions, project conventions, architecture, contract, progress, and ten-photo evaluation checklist completed.
- Delivery documentation is committed on `feat/drawing-tutor`; exact final commit/push/PR identifiers are recorded in the generated delivery report and chat because a commit cannot include its own hash.
- Next development task: privately configure an OpenAI key and perform the ten-photo recognizability/teachability evaluation before considering release work.
