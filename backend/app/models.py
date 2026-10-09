"""A small, numeric-only drawing language shared with the browser.

The model may describe geometry, never SVG markup. Every model-output field is
required and every object forbids unknown keys. A plain union deliberately emits
``anyOf`` for OpenAI Structured Outputs; each member has its own literal kind.
"""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Coordinate = Annotated[float, Field(strict=True, ge=0, le=1000, allow_inf_nan=False)]
Identifier = Annotated[
    str, Field(min_length=1, max_length=64, pattern=r"^[a-zA-Z0-9][a-zA-Z0-9_-]*$")
]
ShortText = Annotated[str, Field(min_length=1, max_length=180)]
PaletteColor = Literal["graphite", "lavender", "peach", "mint"]
FillColor = Literal["none", "graphite", "lavender", "peach", "mint"]


class StrictModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        strict=True,
        str_strip_whitespace=True,
        revalidate_instances="always",
    )


class Point(StrictModel):
    x: Coordinate
    y: Coordinate


class BezierSegment(StrictModel):
    control1: Point
    control2: Point
    end: Point


class StrokeBase(StrictModel):
    id: Identifier
    color: PaletteColor
    width: Annotated[float, Field(strict=True, ge=2, le=12, allow_inf_nan=False)]
    opacity: Annotated[float, Field(strict=True, ge=0.2, le=1, allow_inf_nan=False)]


class LineStroke(StrokeBase):
    kind: Literal["line"]
    start: Point
    end: Point


class PolylineStroke(StrokeBase):
    kind: Literal["polyline"]
    points: Annotated[list[Point], Field(min_length=2, max_length=16)]


class EllipseStroke(StrokeBase):
    kind: Literal["ellipse"]
    center: Point
    rx: Annotated[float, Field(strict=True, gt=0, le=500, allow_inf_nan=False)]
    ry: Annotated[float, Field(strict=True, gt=0, le=500, allow_inf_nan=False)]
    fill: FillColor

    @model_validator(mode="after")
    def stays_on_canvas(self) -> "EllipseStroke":
        if not (
            0 <= self.center.x - self.rx <= self.center.x + self.rx <= 1000
            and 0 <= self.center.y - self.ry <= self.center.y + self.ry <= 1000
        ):
            raise ValueError("Ellipse bounds must stay inside the 1000-unit canvas")
        return self


class PolygonStroke(StrokeBase):
    kind: Literal["polygon"]
    points: Annotated[list[Point], Field(min_length=3, max_length=16)]
    fill: FillColor


class BezierStroke(StrokeBase):
    kind: Literal["bezier"]
    start: Point
    segments: Annotated[list[BezierSegment], Field(min_length=1, max_length=6)]
    closed: bool
    fill: FillColor

    @model_validator(mode="after")
    def only_closed_shapes_are_filled(self) -> "BezierStroke":
        if self.fill != "none" and not self.closed:
            raise ValueError("A filled Bézier shape must be closed")
        return self


Stroke = LineStroke | PolylineStroke | EllipseStroke | PolygonStroke | BezierStroke


class StrokeGroup(StrictModel):
    id: Identifier
    title: Annotated[str, Field(min_length=1, max_length=80)]
    instruction: Annotated[str, Field(min_length=1, max_length=240)]
    strokes: Annotated[list[Stroke], Field(min_length=1, max_length=16)]


class Analysis(StrictModel):
    subject: Annotated[str, Field(min_length=1, max_length=120)]
    recognizable_features: Annotated[list[ShortText], Field(min_length=1, max_length=10)]
    simplifications: Annotated[list[ShortText], Field(min_length=1, max_length=10)]
    proportions: Annotated[str, Field(min_length=1, max_length=400)]
    composition: Annotated[str, Field(min_length=1, max_length=400)]
    difficulty: Literal["easy", "medium"]
    suitable: bool
    reason: Annotated[str, Field(max_length=240)]


class Lesson(StrictModel):
    schema_version: Literal["1"]
    id: Identifier
    source: Literal["demo", "ai"]
    title: Annotated[str, Field(min_length=1, max_length=80)]
    subject: Annotated[str, Field(min_length=1, max_length=120)]
    description: Annotated[str, Field(min_length=1, max_length=500)]
    analysis: Analysis
    groups: Annotated[list[StrokeGroup], Field(min_length=4, max_length=6)]

    @model_validator(mode="after")
    def coherent_blueprint(self) -> "Lesson":
        group_ids = [group.id for group in self.groups]
        stroke_ids = [stroke.id for group in self.groups for stroke in group.strokes]
        if len(group_ids) != len(set(group_ids)):
            raise ValueError("Each group needs a unique ID")
        if len(stroke_ids) != len(set(stroke_ids)):
            raise ValueError("Stroke IDs must be globally unique")
        if len(stroke_ids) > 64:
            raise ValueError("A lesson may have at most 64 strokes")
        if not self.analysis.suitable:
            raise ValueError("A lesson cannot be built from an unsuitable analysis")
        return self
