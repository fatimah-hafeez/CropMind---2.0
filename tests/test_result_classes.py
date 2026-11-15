from dataclasses import dataclass

import pytest

from results.assessment_result import (
    OUTCOME_DISEASE_MATCHED,
    OUTCOME_HEALTHY_MATCHED,
    OUTCOME_NO_MATCH,
    SOURCE_AI_WORKFLOW,
    SOURCE_IMAGE_MODEL,
    AssessmentResult,
)
from results.errors import DiagnosisError


def test_source_texts_match_the_agreement():
    assert SOURCE_IMAGE_MODEL == "Image model"
    assert SOURCE_AI_WORKFLOW == "AI workflow"


def test_outcome_words_match_the_agreement():
    assert OUTCOME_DISEASE_MATCHED == "disease_matched"
    assert OUTCOME_HEALTHY_MATCHED == "healthy_matched"
    assert OUTCOME_NO_MATCH == "no_match"


def test_result_holds_its_four_fields():
    result = AssessmentResult(
        source=SOURCE_IMAGE_MODEL,
        crop="Wheat",
        outcome=OUTCOME_DISEASE_MATCHED,
        disease="Placeholder_Disease",
    )
    assert result.source == "Image model"
    assert result.crop == "Wheat"
    assert result.outcome == "disease_matched"
    assert result.disease == "Placeholder_Disease"


def test_no_match_result_has_an_empty_disease():
    result = AssessmentResult(
        source=SOURCE_AI_WORKFLOW,
        crop="Cotton",
        outcome=OUTCOME_NO_MATCH,
        disease="",
    )
    assert result.disease == ""


def test_result_cannot_be_built_without_a_field():
    with pytest.raises(TypeError):
        AssessmentResult(
            source=SOURCE_IMAGE_MODEL,
            crop="Wheat",
            outcome=OUTCOME_NO_MATCH,
        )


def test_a_subclass_can_add_a_required_field():
    # Fatima and Areeba extend the result with confidence or explanation.
    @dataclass
    class WithConfidence(AssessmentResult):
        confidence: float

    result = WithConfidence(
        source=SOURCE_IMAGE_MODEL,
        crop="Wheat",
        outcome=OUTCOME_HEALTHY_MATCHED,
        disease="Placeholder_Healthy",
        confidence=0.9,
    )
    assert result.confidence == 0.9
    assert isinstance(result, AssessmentResult)


def test_diagnosis_error_carries_its_message():
    error = DiagnosisError("The photo could not be read. Please try another one.")
    assert str(error) == "The photo could not be read. Please try another one."


def test_diagnosis_error_can_be_raised_and_caught():
    with pytest.raises(DiagnosisError) as caught:
        raise DiagnosisError("Something went wrong. Please try again.")
    assert str(caught.value) == "Something went wrong. Please try again."