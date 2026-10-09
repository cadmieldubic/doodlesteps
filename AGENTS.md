# DoodleSteps engineering conventions

This is a private, adult-supervised drawing-tutor prototype. Keep all source in this workspace. Do not deploy it publicly.

- Backend: Python 3.12+, FastAPI, Pydantic, Pillow, official OpenAI SDK. Frontend: React, TypeScript, Vite, Tailwind, Lucide, Zod.
- Treat `docs/CONTRACT.md` as the scene/API contract. Render validated numeric primitives with React SVG elements; never insert model markup or arbitrary SVG paths.
- A lesson has one immutable blueprint, split into 4–6 ordered groups. Steps reveal that geometry cumulatively.
- Demo lessons are always labeled demo. An uploaded photo must never secretly receive a demo lesson.
- No accounts, databases, persistent image storage, frontend API keys, or logging image contents. Re-encode uploads without metadata.
- Use `main` as the primary branch, feature branches for substantial work, and PRs for merge review. Never force-push, delete branches, or rewrite remote history without explicit approval.
- Before each milestone commit, run applicable backend tests, frontend tests, lint, typecheck, build, and integration checks. Record actual results in `docs/PROGRESS.md`; record limitations honestly.
- Never commit `.env`, secrets, virtual environments, `node_modules`, build artifacts, or uploaded photos. Inspect staged files before committing.
- Root owns Git operations and milestone documentation. Parallel contributors edit only their assigned files.

Commands (after dependency installation):

```sh
backend/.venv/bin/python -m pytest backend/tests
backend/.venv/bin/python -m ruff check backend
cd frontend
pnpm test
pnpm lint
pnpm typecheck
pnpm build
pnpm test:e2e
```
