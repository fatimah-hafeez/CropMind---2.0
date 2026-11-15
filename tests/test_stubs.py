import io

import pytest

from app.stubs.stub_image_service import PLACEHOLDER_CONFIDENCE, StubImageService
from app.stubs.stub_results import placeholder_label
from app.stubs.stub_text_service import StubTextService
from results.assessment_result import (
    OUTCOME_DISEASE_MATCHED,
    OUTCOME_HEALTHY_MATCHED,
    OUTCOME_NO_MATCH,
    SOURCE_AI_WORKFLOW,
    SOURCE_IMAGE_MODEL,
)
from results.class_labels import ALL_LABELS, CROPS
from results.errors import DiagnosisError


# Image stub

def test_image_stub_returns_a_disease_match_by_default():
    result = StubImageService().predict(io.BytesIO(b"x"), "Wheat")
    assert result.source == SOURCE_IMAGE_MODEL
    assert result.crop == "Wheat"
    assert result.outcome == OUTCOME_DISEASE_MATCHED
    assert result.disease == "Wheat_Placeholder_Disease"
    assert result.confidence == PLACEHOLDER_CONFIDENCE


def test_image_stub_can_return_a_healthy_match():
    result = StubImageService(outcome=OUTCOME_HEALTHY_MATCHED).predict(None, "Cotton")
    assert result.outcome == OUTCOME_HEALTHY_MATCHED
    assert result.disease == "Cotton_Healthy"


def test_image_stub_no_match_has_no_disease_but_still_a_confidence():
    result = StubImageService(outcome=OUTCOME_NO_MATCH).predict(None, "SugarCane")
    assert result.outcome == OUTCOME_NO_MATCH
    assert result.disease == ""
    assert result.confidence == PLACEHOLDER_CONFIDENCE


def test_image_stub_does_not_touch_the_file():
    file = io.BytesIO(b"some bytes")
    StubImageService().predict(file, "Wheat")
    assert file.tell() == 0


def test_image_stub_failure_raises_a_plain_diagnosis_error():
    with pytest.raises(DiagnosisError) as caught:
        StubImageService(fail=True).predict(None, "Wheat")
    assert str(caught.value) == "The photo could not be checked. Please try again."


def test_image_stub_rejects_the_screen_spelling_of_a_crop():
    with pytest.raises(ValueError):
        StubImageService().predict(None, "Sugarcane")


def test_image_stub_rejects_an_unknown_outcome():
    with pytest.raises(ValueError):
        StubImageService(outcome="no_mach")


# Text stub

def test_text_stub_returns_a_disease_match_by_default():
    result = StubTextService().analyse("yellow spots", "Wheat")
    assert result.source == SOURCE_AI_WORKFLOW
    assert result.crop == "Wheat"
    assert result.outcome == OUTCOME_DISEASE_MATCHED
    assert result.disease == "Wheat_Placeholder_Disease"
    assert result.explanation != ""


def test_text_stub_can_return_a_healthy_match():
    result = StubTextService(outcome=OUTCOME_HEALTHY_MATCHED).analyse("looks fine", "Cotton")
    assert result.outcome == OUTCOME_HEALTHY_MATCHED
    assert result.disease == "Cotton_Healthy"


def test_text_stub_no_match_has_no_disease_but_an_explanation():
    result = StubTextService(outcome=OUTCOME_NO_MATCH).analyse("odd symptoms", "SugarCane")
    assert result.outcome == OUTCOME_NO_MATCH
    assert result.disease == ""
    assert result.explanation != ""


def test_text_result_never_carries_a_confidence():
    result = StubTextService().analyse("yellow spots", "Wheat")
    assert not hasattr(result, "confidence")


def test_text_stub_failure_raises_a_plain_diagnosis_error():
    with pytest.raises(DiagnosisError) as caught:
        StubTextService(fail=True).analyse("yellow spots", "Wheat")
    assert str(caught.value) == "The description could not be checked. Please try again."


def test_text_stub_rejects_the_screen_spelling_of_a_crop():
    with pytest.raises(ValueError):
        StubTextService().analyse("yellow spots", "Sugarcane")


# Placeholder labels

def test_placeholder_disease_labels_are_not_real_labels():
    for crop in CROPS:
        assert placeholder_label(crop, OUTCOME_DISEASE_MATCHED) not in ALL_LABELS