import json
from copy import deepcopy

import pytest
from backend.app.models import Analysis, Lesson, Point
from openai.lib._pydantic import to_strict_json_schema
from pydantic import ValidationError


def test_all_primitives_validate_and_round_trip(lesson_data):
    lesson = Lesson.model_validate(lesson_data)
    assert Lesson.model_validate_json(lesson.model_dump_json()) == lesson
    assert {stroke.kind for group in lesson.groups for stroke in group.strokes} == {
        "line",
        "polyline",
        "ellipse",
        "polygon",
        "bezier",
    }


@pytest.mark.parametrize("value", [-1, 1001, float("nan"), float("inf"), "20", True])
def test_coordinates_reject_outside_nonfinite_and_coerced_values(value):
    with pytest.raises(ValidationError):
        Point(x=value, y=20)


def test_numeric_integer_coordinates_remain_valid():
    assert Point(x=0, y=1000).model_dump() == {"x": 0.0, "y": 1000.0}


@pytest.mark.parametrize("scope", ["lesson", "analysis", "group", "stroke", "point", "segment"])
def test_unknown_fields_are_rejected_at_every_depth(lesson_data, scope):
    targets = {
        "lesson": lesson_data,
        "analysis": lesson_data["analysis"],
        "group": lesson_data["groups"][0],
        "stroke": lesson_data["groups"][0]["strokes"][0],
        "point": lesson_data["groups"][0]["strokes"][0]["center"],
        "segment": lesson_data["groups"][4]["strokes"][0]["segments"][0],
    }
    targets[scope]["svg"] = "<svg onload='alert(1)'/>"
    with pytest.raises(ValidationError):
        Lesson.model_validate(lesson_data)


@pytest.mark.parametrize("missing", ["id", "kind", "color", "width", "opacity", "fill"])
def test_model_output_fields_have_no_defaults(lesson_data, missing):
    del lesson_data["groups"][0]["strokes"][0][missing]
    with pytest.raises(ValidationError):
        Lesson.model_validate(lesson_data)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("color", "red"),
        ("color", "url(https://example.com)"),
        ("width", 1),
        ("width", 13),
        ("opacity", 0.1),
        ("opacity", 1.1),
        ("rx", 0),
        ("rx", 501),
        ("fill", "#ffffff"),
        ("kind", "path"),
        ("id", "bad id"),
        ("id", ""),
        ("id", "a" * 65),
    ],
)
def test_bad_stroke_parameters_are_rejected(lesson_data, field, value):
    lesson_data["groups"][0]["strokes"][0][field] = value
    with pytest.raises(ValidationError):
        Lesson.model_validate(lesson_data)


def test_ellipse_full_bounds_are_checked(lesson_data):
    lesson_data["groups"][0]["strokes"][0]["center"]["x"] = 20
    with pytest.raises(ValidationError, match="Ellipse bounds"):
        Lesson.model_validate(lesson_data)


@pytest.mark.parametrize("where", ["group", "stroke"])
def test_duplicate_identifiers_are_rejected(lesson_data, where):
    groups = lesson_data["groups"]
    if where == "group":
        groups[1]["id"] = groups[0]["id"]
    else:
        groups[1]["strokes"][0]["id"] = groups[0]["strokes"][0]["id"]
    with pytest.raises(ValidationError, match="unique"):
        Lesson.model_validate(lesson_data)


@pytest.mark.parametrize("count", [3, 7])
def test_group_count_bounds(lesson_data, count):
    groups = lesson_data["groups"]
    lesson_data["groups"] = (groups * 2)[:count]
    with pytest.raises(ValidationError):
        Lesson.model_validate(lesson_data)


def test_total_complexity_limit_is_checked(lesson_data):
    for index, group in enumerate(lesson_data["groups"]):
        prototype = group["strokes"][0]
        group["strokes"] = [{**deepcopy(prototype), "id": f"stroke-{index}-{j}"} for j in range(13)]
    with pytest.raises(ValidationError, match="64 strokes"):
        Lesson.model_validate(lesson_data)


@pytest.mark.parametrize("count", [0, 17])
def test_per_group_complexity_limit(lesson_data, count):
    prototype = lesson_data["groups"][0]["strokes"][0]
    lesson_data["groups"][0]["strokes"] = [
        {**deepcopy(prototype), "id": f"stroke-{j}"} for j in range(count)
    ]
    with pytest.raises(ValidationError):
        Lesson.model_validate(lesson_data)


def test_open_bezier_cannot_have_a_fill(lesson_data):
    lesson_data["groups"][4]["strokes"][0]["fill"] = "peach"
    with pytest.raises(ValidationError, match="must be closed"):
        Lesson.model_validate(lesson_data)


@pytest.mark.parametrize("field,value", [("suitable", "true"), ("suitable", 1)])
def test_analysis_booleans_are_strict(analysis_data, field, value):
    analysis_data[field] = value
    with pytest.raises(ValidationError):
        Analysis.model_validate(analysis_data)


def test_unsuitable_analysis_cannot_form_a_lesson(lesson_data):
    lesson_data["analysis"]["suitable"] = False
    with pytest.raises(ValidationError, match="unsuitable"):
        Lesson.model_validate(lesson_data)


def test_text_bounds_prevent_unbounded_model_output(lesson_data):
    lesson_data["groups"][0]["instruction"] = "a" * 241
    with pytest.raises(ValidationError):
        Lesson.model_validate(lesson_data)


@pytest.mark.parametrize("model", [Analysis, Lesson])
def test_official_sdk_emits_strict_provider_compatible_schema(model):
    schema = to_strict_json_schema(model)

    def walk(value):
        if isinstance(value, dict):
            if value.get("type") == "object":
                assert value["additionalProperties"] is False
                assert set(value["required"]) == set(value["properties"])
            assert "oneOf" not in value
            assert "default" not in value
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(schema)
    assert "<svg" not in json.dumps(schema)
