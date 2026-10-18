import io
from copy import deepcopy

import pytest
from backend.app.models import Analysis, Lesson
from PIL import Image


@pytest.fixture
def analysis_data():
    return {
        "subject": "floppy-eared puppy",
        "recognizable_features": ["two soft floppy ears", "small round nose"],
        "simplifications": ["one rounded head", "no fur texture"],
        "proportions": "A rounded head is wider than the little body.",
        "composition": "Centered with room around the ears and paws.",
        "difficulty": "easy",
        "suitable": True,
        "reason": "",
    }


@pytest.fixture
def analysis(analysis_data):
    return Analysis.model_validate(analysis_data)


@pytest.fixture
def lesson_data(analysis_data):
    base = {"color": "graphite", "width": 6, "opacity": 1}
    strokes = [
        {
            **base,
            "id": "head",
            "kind": "ellipse",
            "center": {"x": 500, "y": 400},
            "rx": 220,
            "ry": 180,
            "fill": "none",
        },
        {
            **base,
            "id": "tail",
            "kind": "line",
            "start": {"x": 650, "y": 650},
            "end": {"x": 730, "y": 600},
        },
        {
            **base,
            "id": "paw",
            "kind": "polyline",
            "points": [{"x": 370, "y": 650}, {"x": 360, "y": 700}, {"x": 420, "y": 700}],
        },
        {
            **base,
            "id": "nose",
            "kind": "polygon",
            "points": [{"x": 470, "y": 410}, {"x": 530, "y": 410}, {"x": 500, "y": 445}],
            "fill": "graphite",
        },
        {
            **base,
            "id": "smile",
            "kind": "bezier",
            "start": {"x": 460, "y": 460},
            "segments": [
                {
                    "control1": {"x": 480, "y": 485},
                    "control2": {"x": 520, "y": 485},
                    "end": {"x": 540, "y": 460},
                }
            ],
            "closed": False,
            "fill": "none",
        },
    ]
    return {
        "schema_version": "1",
        "id": "test-lesson",
        "source": "ai",
        "title": "A soft little puppy",
        "subject": analysis_data["subject"],
        "description": "Draw the puppy's rounded head, paws and gentle smile.",
        "analysis": deepcopy(analysis_data),
        "groups": [
            {
                "id": f"step-{index + 1}",
                "title": f"Friendly shape {index + 1}",
                "instruction": "Draw this gentle shape. You're doing beautifully!",
                "strokes": [stroke],
            }
            for index, stroke in enumerate(strokes)
        ],
    }


@pytest.fixture
def lesson(lesson_data):
    return Lesson.model_validate(lesson_data)


@pytest.fixture
def png_bytes():
    image = Image.new("RGB", (120, 80), "peachpuff")
    buffer = io.BytesIO()
    image.save(buffer, "PNG")
    return buffer.getvalue()
