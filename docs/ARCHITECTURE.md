# Architecture

React/Vite serves a local browser interface. FastAPI serves a documented REST API. The browser fetches deterministic demo lessons or posts one photograph to the backend. No database or image store is used.

An ASGI guard limits actual upload bytes before multipart parsing, including chunked requests. The parser's spool threshold is above the bounded request size, so uploads stay in memory; forms are closed before AI work begins. Image bytes are decoded with Pillow under pixel limits, oriented, resized, and re-encoded in memory without metadata. Only the sanitized image is sent to OpenAI. Stage A identifies subject, distinguishing traits, simplifications, proportions, composition, and suitability. Stage B creates one restricted vector scene split into 4–6 teaching groups. Pydantic validates all output before return; Zod validates it again in the browser.

Generation POSTs reject foreign/null browser origins before parsing or provider calls. A per-client sliding window and concurrent-request cap protect paid AI work, with bounded/expiring limiter state. Pillow processing runs in a threadpool. Provider errors are mapped to safe messages. Suitability is model-instructed and remains subject to live evaluation; it is not a verified personal-image detector.

The SVG renderer creates only known React elements from numbers and enumerated colors. Previous groups are muted, current strokes highlighted, and individual strokes revealed. Printing and the finished view read the exact same geometry. Deterministic demos are explicitly marked and never masquerade as AI output.

Secrets stay in root `.env` and are read only by the backend. Uploads live in memory for the request; browser previews live only for the active session. Upstream requests use `store=False`. Provider-side retention must be assessed separately before release.

See `CONTRACT.md` for the data contract and `PLAN.md` for acceptance criteria. Final implementation details and verification are tracked in `PROGRESS.md`.
