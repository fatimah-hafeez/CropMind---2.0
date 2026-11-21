"""Tests of the classifier's own logic with a fake model. No TensorFlow is needed.

Reading a real photo and loading the real model are checked by
scripts/check_image_service.py instead.
"""

import numpy as np
import pytest

from image_module import image_classifier
from image_module.image_classifier import CHECK_ERROR, UNAVAILABLE_ERROR, ImageClassifier
from results.class_labels import CROPS, LABELS_BY_CROP
from results.errors import DiagnosisError


class FakeModel:
    def __init__(self, probs=None, error=None):
        self.probs = np.arange(27, dtype="float64") / 100 if probs is None else np.asarray(probs, dtype="float64")
        self.error = error

    def predict(self, batch, verbose=0, batch_size=1):
        if self.error:
            raise self.error
        return np.array([self.probs])


def classifier_with(model):
    clf = ImageClassifier("not_used.keras")
    clf._model = model  # already "loaded"
    clf._to_tensor = lambda image: np.zeros((224, 224, 3), dtype="uint8")
    return clf


@pytest.mark.parametrize("crop", CROPS)
def test_returns_the_nine_raw_probabilities_of_the_crop_in_class_order(crop):
    pairs = classifier_with(FakeModel()).crop_probabilities("photo", crop)
    start = CROPS.index(crop) * 9
    assert [label for label, _ in pairs] == list(LABELS_BY_CROP[crop])
    assert [p for _, p in pairs] == pytest.approx([(start + i) / 100 for i in range(9)])


def test_probabilities_are_not_renormalised():
    pairs = classifier_with(FakeModel()).crop_probabilities("photo", "Cotton")
    assert sum(p for _, p in pairs) == pytest.approx(0.36)  # 0.00 + 0.01 + ... + 0.08


def test_unknown_crop_is_rejected():
    with pytest.raises(ValueError):
        classifier_with(FakeModel()).crop_probabilities("photo", "Rice")


def test_a_model_failure_gives_a_plain_diagnosis_error():
    clf = classifier_with(FakeModel(error=RuntimeError("secret detail at C:\\path")))
    with pytest.raises(DiagnosisError) as caught:
        clf.crop_probabilities("photo", "Wheat")
    assert str(caught.value) == CHECK_ERROR


def test_invalid_probabilities_give_a_diagnosis_error():
    probs = np.arange(27, dtype="float64") / 100
    probs[20] = np.nan
    with pytest.raises(DiagnosisError):
        classifier_with(FakeModel(probs)).crop_probabilities("photo", "Wheat")


def test_a_missing_model_file_gives_a_plain_diagnosis_error(tmp_path):
    missing = tmp_path / "no_such_model.keras"
    clf = ImageClassifier(missing)
    with pytest.raises(DiagnosisError) as caught:
        clf.crop_probabilities("photo", "Wheat")
    assert str(caught.value) == UNAVAILABLE_ERROR
    assert str(missing) not in str(caught.value)


def test_a_wrong_label_list_stops_the_classifier(monkeypatch):
    monkeypatch.setattr(image_classifier, "ALL_LABELS", image_classifier.ALL_LABELS[:-1])
    with pytest.raises(RuntimeError):
        ImageClassifier("not_used.keras")
