"""PLACEHOLDER. Temporary stand-in for Areeba's TextDiagnosisService.

It never reads the symptoms and decides nothing by itself. It returns a fixed
placeholder answer, chosen when the stub is created. Delete it when the real
service is connected.
"""

from app.stubs.stub_results import OUTCOMES, TextAssessment, placeholder_label
from results.assessment_result import (
    OUTCOME_DISEASE_MATCHED,
    OUTCOME_HEALTHY_MATCHED,
    OUTCOME_NO_MATCH,
    SOURCE_AI_WORKFLOW,
)
from results.class_labels import CROPS
from results.errors import DiagnosisError

PLACEHOLDER_EXPLANATIONS = {
    OUTCOME_DISEASE_MATCHED: "Placeholder explanation for a disease match.",
    OUTCOME_HEALTHY_MATCHED: "Placeholder explanation for a healthy match.",
    OUTCOME_NO_MATCH: (
        "Placeholder explanation: the description did not clearly fit a listed disease."
    ),
}


class StubTextService:
    def __init__(self, outcome=OUTCOME_DISEASE_MATCHED, fail=False):
        if outcome not in OUTCOMES:
            raise ValueError(f"Unknown outcome: {outcome}")
        self.outcome = outcome
        self.fail = fail

    def analyse(self, symptoms, crop):
        """Same call as the real service: analyse(symptoms, crop)."""
        if self.fail:
            raise DiagnosisError("The description could not be checked. Please try again.")
        if crop not in CROPS:
            raise ValueError(f"Unknown crop: {crop}")
        return TextAssessment(
            source=SOURCE_AI_WORKFLOW,
            crop=crop,
            outcome=self.outcome,
            disease=placeholder_label(crop, self.outcome),
            explanation=PLACEHOLDER_EXPLANATIONS[self.outcome],
        )