"""The real image service. It replaces StubImageService in app/main.py.

predict(image, crop) has the same call as the stub and returns an
ImagePrediction. The service applies the confidence rule itself, so the screen
never sees a threshold.

The rule (frozen in A10, numbers in image_module/settings.py):
  1. Take the best class among the 9 classes of the selected crop.
  2. Its confidence is the raw probability the model gave it.
  3. If the best class is the crop's Healthy class, the confidence must reach
     T_HEALTHY. For any other class it must reach T_DISEASE.
  4. Otherwise the outcome is no match: the disease field is empty and the
     confidence is still returned (the screen does not show it).
"""

from image_module import settings
from image_module.image_classifier import ImageClassifier
from results.assessment_result import (
    OUTCOME_DISEASE_MATCHED,
    OUTCOME_HEALTHY_MATCHED,
    OUTCOME_NO_MATCH,
    SOURCE_IMAGE_MODEL,
)
from results.class_labels import CROPS
from results.image_prediction import ImagePrediction


def healthy_label(crop):
    return f"{crop}_Healthy"


def decide(crop, probabilities, t_disease, t_healthy):
    """Apply the rule. Returns (outcome, disease, confidence).

    probabilities: (label, raw probability) pairs of the selected crop.
    """
    label, confidence = max(probabilities, key=lambda pair: pair[1])
    is_healthy = label == healthy_label(crop)
    needed = t_healthy if is_healthy else t_disease
    if confidence < needed:
        return OUTCOME_NO_MATCH, "", confidence
    if is_healthy:
        return OUTCOME_HEALTHY_MATCHED, label, confidence
    return OUTCOME_DISEASE_MATCHED, label, confidence


class ImageDiagnosisService:
    def __init__(self, classifier, t_disease=settings.T_DISEASE, t_healthy=settings.T_HEALTHY):
        for name, value in (("t_disease", t_disease), ("t_healthy", t_healthy)):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")
        if t_healthy < t_disease:
            raise ValueError("t_healthy must not be lower than t_disease")
        self._classifier = classifier
        self._t_disease = t_disease
        self._t_healthy = t_healthy

    def predict(self, image, crop):
        """Same call as the stub: predict(image, crop) returns ImagePrediction."""
        if crop not in CROPS:
            raise ValueError(f"Unknown crop: {crop}")
        probabilities = self._classifier.crop_probabilities(image, crop)
        outcome, disease, confidence = decide(crop, probabilities, self._t_disease, self._t_healthy)
        return ImagePrediction(
            source=SOURCE_IMAGE_MODEL,
            crop=crop,
            outcome=outcome,
            disease=disease,
            confidence=confidence,
        )


def create_image_service():
    """The real service with the settings of image_module/settings.py."""
    return ImageDiagnosisService(ImageClassifier(settings.MODEL_PATH))
