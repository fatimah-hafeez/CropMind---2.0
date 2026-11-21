"""Tests of the confidence rule. No model and no TensorFlow are needed."""

import pytest

from image_module import settings
from image_module.image_diagnosis_service import ImageDiagnosisService, decide
from results.assessment_result import (
    OUTCOME_DISEASE_MATCHED,
    OUTCOME_HEALTHY_MATCHED,
    OUTCOME_NO_MATCH,
    SOURCE_IMAGE_MODEL,
)
from results.class_labels import CROPS, LABELS_BY_CROP
from results.errors import DiagnosisError
from results.image_prediction import ImagePrediction


class FakeClassifier:
    """Returns fixed raw probabilities, like the real classifier would."""

    def __init__(self, best_label=None, confidence=0.0, error=None):
        self.best_label = best_label
        self.confidence = confidence
        self.error = error
        self.calls = []

    def crop_probabilities(self, image, crop):
        self.calls.append((image, crop))
        if self.error:
            raise self.error
        # The best label gets the confidence; the others stay clearly lower.
        return tuple(
            (label, self.confidence if label == self.best_label else self.confidence / 10)
            for label in LABELS_BY_CROP[crop]
        )


def service_for(crop, label, confidence):
    return ImageDiagnosisService(FakeClassifier(f"{crop}_{label}", confidence))


def test_frozen_thresholds():
    assert settings.T_DISEASE == 0.80
    assert settings.T_HEALTHY == 0.85


@pytest.mark.parametrize("crop", CROPS)
def test_disease_above_threshold_is_matched(crop):
    disease = next(label for label in LABELS_BY_CROP[crop] if not label.endswith("_Healthy"))
    result = ImageDiagnosisService(FakeClassifier(disease, 0.93)).predict("photo", crop)
    assert isinstance(result, ImagePrediction)
    assert result.source == SOURCE_IMAGE_MODEL
    assert result.crop == crop
    assert result.outcome == OUTCOME_DISEASE_MATCHED
    assert result.disease == disease
    assert result.confidence == pytest.approx(0.93)


@pytest.mark.parametrize("crop", CROPS)
def test_healthy_above_threshold_is_matched(crop):
    result = service_for(crop, "Healthy", 0.90).predict("photo", crop)
    assert result.outcome == OUTCOME_HEALTHY_MATCHED
    assert result.disease == f"{crop}_Healthy"


@pytest.mark.parametrize("crop", CROPS)
def test_disease_below_threshold_is_no_match_with_confidence(crop):
    disease = next(label for label in LABELS_BY_CROP[crop] if not label.endswith("_Healthy"))
    result = ImageDiagnosisService(FakeClassifier(disease, 0.79)).predict("photo", crop)
    assert result.outcome == OUTCOME_NO_MATCH
    assert result.disease == ""
    assert result.confidence == pytest.approx(0.79)


def test_healthy_is_stricter_than_disease():
    # 0.82 is enough for a disease but not for Healthy.
    healthy = service_for("Wheat", "Healthy", 0.82).predict("photo", "Wheat")
    disease = service_for("Wheat", "Septoria", 0.82).predict("photo", "Wheat")
    assert healthy.outcome == OUTCOME_NO_MATCH
    assert disease.outcome == OUTCOME_DISEASE_MATCHED


def test_confidence_exactly_on_the_threshold_is_accepted():
    assert service_for("Wheat", "Septoria", 0.80).predict("photo", "Wheat").outcome == OUTCOME_DISEASE_MATCHED
    assert service_for("Wheat", "Healthy", 0.85).predict("photo", "Wheat").outcome == OUTCOME_HEALTHY_MATCHED


def test_low_raw_probabilities_are_rejected():
    # A photo of the wrong crop leaves little probability on this crop's classes.
    result = service_for("Cotton", "Curl_Virus", 0.05).predict("photo", "Cotton")
    assert result.outcome == OUTCOME_NO_MATCH
    assert result.disease == ""


def test_the_best_class_decides_not_the_first():
    probabilities = (("Wheat_Blast", 0.30), ("Wheat_Healthy", 0.88), ("Wheat_Septoria", 0.40))
    outcome, disease, confidence = decide("Wheat", probabilities, 0.80, 0.85)
    assert (outcome, disease) == (OUTCOME_HEALTHY_MATCHED, "Wheat_Healthy")
    assert confidence == pytest.approx(0.88)


def test_the_service_passes_photo_and_crop_to_the_classifier():
    classifier = FakeClassifier("Wheat_Blast", 0.95)
    ImageDiagnosisService(classifier).predict("the photo", "Wheat")
    assert classifier.calls == [("the photo", "Wheat")]


def test_unknown_crop_is_rejected_before_any_work():
    classifier = FakeClassifier("Wheat_Blast", 0.95)
    with pytest.raises(ValueError):
        ImageDiagnosisService(classifier).predict("photo", "Rice")
    assert classifier.calls == []


def test_a_classifier_failure_reaches_the_caller_as_diagnosis_error():
    service = ImageDiagnosisService(FakeClassifier(error=DiagnosisError("The photo could not be read.")))
    with pytest.raises(DiagnosisError):
        service.predict("photo", "Wheat")


@pytest.mark.parametrize(
    "t_disease, t_healthy",
    [(-0.1, 0.85), (0.80, 1.1), (0.90, 0.80)],
)
def test_bad_thresholds_are_rejected(t_disease, t_healthy):
    with pytest.raises(ValueError):
        ImageDiagnosisService(FakeClassifier(), t_disease, t_healthy)
