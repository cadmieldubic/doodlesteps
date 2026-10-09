# Architecture

React/Vite serves a local browser interface. FastAPI serves a documented REST API. The browser fetches deterministic demo lessons or posts one photograph to the backend. No database or image store is used.

Image bytes are size-checked, decoded with Pillow under pixel limits, oriented, resized, and re-encoded without metadata. Only the sanitized image is sent to OpenAI. Stage A identifies subject, distinguishing traits, simplifications, proportions, composition, and suitability. Stage B creates one restricted vector scene split into 4–6 teaching groups. Pydantic validates all output before return; Zod validates it again in the browser.

The SVG renderer creates only known React elements from numbers and enumerated colors. Previous groups are muted, current strokes highlighted, and individual strokes revealed. Printing and the finished view read the exact same geometry. Deterministic demos are explicitly marked and never masquerade as AI output.

Secrets stay in root `.env` and are read only by the backend. Uploads live in memory for the request; browser previews live only for the active session. Upstream requests use `store=False`. Provider-side retention must be assessed separately before release.

See `CONTRACT.md` for the data contract and `PLAN.md` for acceptance criteria. Final implementation details and verification are tracked in `PROGRESS.md`.
