# DoodleSteps

A private drawing tutor that turns non-personal photographs into playful, progressive sketch lessons for beginners aged about 6–10. Three deterministic demo lessons (puppy, flower, house) work without credentials. Real photo generation uses a configurable two-stage OpenAI pipeline.

## Start on this Mac

Open a terminal in the project workspace and run:

```sh
bash scripts/dev.sh
```

Open **http://127.0.0.1:5173**. Keep the terminal running; press Control-C to stop both applications. API documentation is at **http://127.0.0.1:8000/docs**.

## First setup on another machine

Install Python 3.12+, Node.js 22.12+, and pnpm 11.25+. The scripts can also find the bundled Codex runtimes on this Mac.

```sh
bash scripts/setup.sh
bash scripts/dev.sh
```

Setup creates `backend/.venv`, installs pinned Python and JavaScript dependencies, and installs Chromium inside ignored `work/playwright` for browser tests. The project has no database or migrations.

To start the applications separately:

```sh
# Terminal 1, from the project root:
backend/.venv/bin/python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload --no-access-log

# Terminal 2:
cd frontend
pnpm dev --host 127.0.0.1 --port 5173
```

## Use the tutor

Choose a labeled puppy, flower, or house demo. Preview the finished drawing, switch to the guide, and copy each group onto paper. Use **Show Next Line** to reveal one stroke, **Previous**/**Next** to move through the lesson, and **Print drawing guide** for a clean worksheet. The completion view lets you restart or begin another lesson.

Upload a JPEG, PNG, or WebP (up to 8 MB by default), or use the camera option on a supported phone. Preview, replace, or remove the photo before requesting a lesson. Desktop camera support depends on the browser/device's file-capture behavior.

## Enable real photo lessons

Demos need no external credentials. To enable live generation, an adult developer should run:

```sh
cp .env.example .env
```

Edit `.env` **locally** and set `OPENAI_API_KEY`, then restart the backend. Never paste the key in chat or put it in frontend configuration. The selected models must support image input and Responses structured output; model access and API billing depend on your OpenAI account. `OPENAI_VISION_MODEL` and `OPENAI_DRAWING_MODEL` are independently configurable.

The service analyzes the actual photo, identifies its distinguishing features, then constructs one validated scene with 4–6 groups. The AI is instructed to flag unsuitable, busy, or personal images; rejected analyses return guidance. This classification still needs live evaluation, so always choose non-personal images. When AI is unavailable, it returns an error and keeps the three demos available. It never presents an unrelated demo as your photo's drawing.

## Configuration

See `.env.example`. All variables are backend-only:

| Variable | Purpose |
|---|---|
| `OPENAI_API_KEY` | Optional secret; empty means demos only |
| `OPENAI_VISION_MODEL` / `OPENAI_DRAWING_MODEL` | Vision analysis and drawing-construction models |
| `OPENAI_TIMEOUT_SECONDS` | Overall generation timeout |
| `OPENAI_MAX_OUTPUT_TOKENS` | Construction response token cap |
| `MAX_UPLOAD_BYTES` | Maximum image file size |
| `MAX_IMAGE_PIXELS` / `MAX_IMAGE_DIMENSION` | Decoding safety limit and sanitized maximum dimension |
| `AI_REQUESTS_PER_MINUTE` / `AI_MAX_CONCURRENT` | Local request and concurrency controls |
| `CORS_ORIGINS` | Comma-separated development origins |

## Verify

```sh
bash scripts/verify.sh
```

This runs backend tests/lint/compilation, frontend unit tests/type checks/lint/production build, Playwright browser tests, and whitespace checks. Automated AI tests use mocked SDK responses, without paid calls. See `docs/PROGRESS.md` for actual results and `docs/VISUAL_EVALUATION.md` for ten-photo visual-quality acceptance.

Verified: **141 backend tests, 26 frontend tests, and 18 desktop/mobile browser tests** passed, along with lint, type checks, Python compilation, and production build. [Private CI evidence](https://github.com/cadmieldubic/doodlesteps/actions/runs/37988321250).

Live AI generation and photo-to-sketch resemblance have **not** been verified without a configured API key. Valid JSON alone is not evidence of a good drawing. The API implementation and error handling are tested with mocks; the deterministic demo drawings are evaluated separately in the browser.

## Project layout

```text
backend/              FastAPI, image preprocessing, AI stages, scene models, tests
frontend/             React, runtime validation, SVG renderer, tutor, worksheet, tests
scripts/              Setup, local development, and verification helpers
docs/                 Plan, progress, architecture, API contract, quality evaluation
.env.example          Configuration template with no real credentials
AGENTS.md             Engineering and source-control conventions
```

See `docs/ARCHITECTURE.md` and `docs/CONTRACT.md` for system/data flow and REST schemas. GitHub's primary branch is `main`; substantial work uses feature branches and pull requests. Secrets, dependencies, local environment files, uploads, and build artifacts are ignored.

Private, adult-supervised testing only. Do not upload faces, personal documents, or sensitive images. No public deployment, accounts, database, or persistent image storage.

The backend removes metadata, corrects image orientation, and downsizes before sending the sanitized image to OpenAI. Browser previews exist only for the active session. Upload bodies are bounded before multipart parsing, and the parser is configured to keep uploads in memory. The application does not retain uploads. `store=False` is used for AI responses, but this does not establish zero provider retention. Review provider policies, parental consent, child safety, privacy, accessibility, and data handling before release. This MVP does not claim production child-safety compliance.

Private GitHub CI runs the same checks on Linux, including desktop/mobile Chromium tests, without live API credentials or deployment. On this Mac, Codex's terminal sandbox blocks Chromium's Mach process initialization; use a normal Terminal for `bash scripts/verify.sh`, or review the private CI run. Broader filesystem permission is not required for that restriction.

Future improvements: larger live-photo visual evaluation, expert-authored stroke guidance/examples, optional adult cropping/subject selection, richer accessibility and localized instructions, and a reviewed safety/privacy design before any release.

API implementation references: [OpenAI structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses) and [image inputs](https://developers.openai.com/api/docs/guides/images-vision).
