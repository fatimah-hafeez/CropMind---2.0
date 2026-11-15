"""PLACEHOLDER. Temporary pieces for the stubs, easy to delete later.

Delete this file when Fatima's results/image_prediction.py and Areeba's
results/text_assessment.py exist. Their classes should have the same names
and fields, so only the import lines change.
"""

from dataclasses import dataclass

from results.assessment_result import (
    OUTCOME_DISEASE_MATCHED,
    OUTCOME_HEALTHY_MATCHED,
    OUTCOME_NO_MATCH,
    AssessmentResult,
)

OUTCOMES = (OUTCOME_DISEASE_MATCHED, OUTCOME_HEALTHY_MATCHED, OUTCOME_NO_MATCH)


def placeholder_label(crop, outcome):
    """The invented label a stub returns. No real disease name is used."""
    if outcome == OUTCOME_DISEASE_MATCHED:
        return f"{crop}_Placeholder_Disease"
    if outcome == OUTCOME_HEALTHY_MATCHED:
        return f"{crop}_Healthy"
    return ""  # no_match has no disease


@dataclass
class ImagePrediction(AssessmentResult):
    """AssessmentResult plus the confidence of the image model, 0 to 1."""

    confidence: float


@dataclass
class TextAssessment(AssessmentResult):
    """AssessmentResult plus a short written explanation."""

    explanation: str