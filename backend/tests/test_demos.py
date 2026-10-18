"""Exercise the public demo contract without credentials or image uploads."""

import pytest

from app.demos import DEMO_LESSONS, DEMOS, get_demo
from app.models import Lesson


@pytest.mark.parametrize("identifier", ["puppy", "flower", "house"])
def test_demo_can_round_trip_through_the_api_without_credentials(identifier, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    lesson = get_demo(identifier)
    assert lesson is not None
    assert lesson.source == "demo"
    assert Lesson.model_validate_json(lesson.model_dump_json()) == lesson
    assert all(group.instruction.strip() for group in lesson.groups)


def test_sample_collection_has_three_distinct_complete_subjects():
    assert set(DEMOS) == {"puppy", "flower", "house"}
    assert len({lesson.subject for lesson in DEMO_LESSONS}) == 3
    for lesson in DEMO_LESSONS:
        # Each final scene includes expressive contours, rather than a collection
        # of unrelated circles, and retains room for six teachable stages.
        assert len(lesson.groups) == 6
        assert any(stroke.kind == "bezier" for group in lesson.groups for stroke in group.strokes)
        assert sum(len(group.strokes) for group in lesson.groups) <= 64


def test_unknown_subject_never_silently_becomes_an_unrelated_sample():
    assert get_demo("uploaded-photo") is None
    assert get_demo("") is None
