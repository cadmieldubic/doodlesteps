# REST and drawing contract (v1)

Base URL `/api`. Frontend Vite proxy forwards `/api` to local FastAPI on port 8000.

- `GET /api/health` → `{status: "ok"}`.
- `GET /api/config` → `{ai_available: boolean, max_upload_bytes: number, supported_formats: ["image/jpeg", "image/png", "image/webp"]}`. No secrets.
- `GET /api/demos` → full `Lesson[]` (three small scenes).
- `GET /api/demos/{id}` → one Lesson; known ids `puppy`, `flower`, `house`.
- `POST /api/lessons` multipart field `image` → Lesson. Errors `{detail: string}` with appropriate 4xx/5xx codes.

## Models

All objects reject extra fields. Coordinates are finite numeric values in 0..1000. Point: `{x, y}`. Fixed viewBox `0 0 1000 1000`.

`Analysis`: `{subject: string, recognizable_features: string[], simplifications: string[], proportions: string, composition: string, difficulty: "easy" | "medium", suitable: boolean, reason: string}`. Text/list lengths bounded. Unsuitable photos do not proceed to construction.

`Lesson`: `{schema_version: "1", id: string, source: "demo" | "ai", title: string, subject: string, description: string, analysis: Analysis, groups: StrokeGroup[]}`.

`StrokeGroup`: `{id: string, title: string, instruction: string, strokes: Stroke[]}`. 4–6 groups, each 1–16 strokes, total ≤64, unique group IDs and globally unique stroke IDs. Instructions short (≤240 characters).

Every stroke includes `{id: string, kind, color: "graphite" | "lavender" | "peach" | "mint", width: number (2..12), opacity: number (0.2..1)}`. All fields required (no model-output defaults). No fill except explicitly enumerated color or `none` in ellipse/polygon/bezier.

- `line`: `{start: Point, end: Point}`
- `polyline`: `{points: Point[]}` (2..16)
- `ellipse`: `{center: Point, rx: number (>0, ≤500), ry: number (>0, ≤500), fill: "none" | palette color}`; full bounds stay within canvas.
- `polygon`: `{points: Point[]}` (3..16), `fill`.
- `bezier`: `{start: Point, segments: [{control1: Point, control2: Point, end: Point}] (1..6), closed: boolean, fill}`.

SVG `d` strings are constructed locally from validated numeric Bézier coordinates. No arbitrary model SVG, HTML, JavaScript, URLs, filters, transforms, or path strings accepted. The same primitive object is used unchanged across every cumulative rendering.
