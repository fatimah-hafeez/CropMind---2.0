"""PLACEHOLDER. Temporary stand-in for Fatima's ImageDiagnosisService.

It never reads the image and decides nothing by itself. It returns a fixed
placeholder answer, chosen when the stub is created. Delete it when the real
service is connected.
"""

from app.stubs.stub_results import OUTCOMES, ImagePrediction, placeholder_label
from results.assessment_result import OUTCOME_DISEASE_MATCHED, SOURCE_IMAGE_MODEL
from results.class_labels import CROPS
from results.errors import DiagnosisError

# A fixed made-up number. It is not a real threshold.
PLACEHOLDER_CONFIDENCE = 0.50


class StubImageService:
    def __init__(self, outcome=OUTCOME_DISEASE_MATCHED, fail=False):
        if outcome not in OUTCOMES:
            raise ValueError(f"Unknown outcome: {outcome}")
        self.outcome = outcome
        self.fail = fail

    def predict(self, image, crop):
        """Same call as the real service: predict(image, crop)."""
        if self.fail:
            raise DiagnosisError("The photo could not be checked. Please try again.")
        if crop not in CROPS:
            raise ValueError(f"Unknown crop: {crop}")
        return ImagePrediction(
            source=SOURCE_IMAGE_MODEL,
            crop=crop,
            outcome=self.outcome,
            disease=placeholder_label(crop, self.outcome),
            confidence=PLACEHOLDER_CONFIDENCE,
        )