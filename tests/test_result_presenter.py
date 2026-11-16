from app.crop_mind_app import CROP_CHOICES
from app.result_presenter import (
    DISPLAY_CROPS,
    TEXT_HEALTHY,
    TEXT_NO_MATCH,
    ResultPresenter,
)
from app.stubs.stub_image_service import StubImageService
from app.stubs.stub_text_service import StubTextService
from results.assessment_result import (
    OUTCOME_DISEASE_MATCHED,
    OUTCOME_HEALTHY_MATCHED,
    OUTCOME_NO_MATCH,
)
from results.class_labels import CROPS, LABELS_BY_CROP


def image_result(outcome, crop="Wheat"):
    return StubImageService(outcome=outcome).predict(None, crop)


def text_result(outcome, crop="Wheat"):
    return StubTextService(outcome=outcome).analyse("yellow spots", crop)


# Words for crops and labels

def test_sugarcane_is_shown_as_sugarcane():
    presenter = ResultPresenter()
    assert presenter.display_crop("SugarCane") == "Sugarcane"
    assert presenter.display_crop("Wheat") == "Wheat"
    assert presenter.display_crop("Cotton") == "Cotton"


def test_label_loses_its_crop_prefix_and_underscores():
    presenter = ResultPresenter()
    assert presenter.display_disease("Wheat_Brown_Rust", "Wheat") == "Brown Rust"
    assert presenter.display_disease("SugarCane_Red_Rot", "SugarCane") == "Red Rot"
    assert presenter.display_disease("Cotton_Leaf_Hopper_Jassids", "Cotton") == "Leaf Hopper Jassids"


def test_label_without_the_prefix_only_loses_its_underscores():
    assert ResultPresenter().display_disease("Other_Label", "Wheat") == "Other Label"


def test_every_real_label_becomes_plain_words():
    presenter = ResultPresenter()
    for crop in CROPS:
        for label in LABELS_BY_CROP[crop]:
            shown = presenter.display_disease(label, crop)
            assert shown != ""
            assert "_" not in shown
            assert not shown.startswith(crop)
        assert presenter.display_disease(f"{crop}_Healthy", crop) == "Healthy"


def test_presenter_and_controller_agree_on_crop_spelling():
    assert {service: shown for shown, service in CROP_CHOICES.items()} == DISPLAY_CROPS


# Image results

def test_image_disease_match_lines():
    lines = ResultPresenter().result_lines(image_result(OUTCOME_DISEASE_MATCHED))
    assert lines == [
        ("Source", "Image model"),
        ("Crop", "Wheat"),
        ("Outcome", "Placeholder Disease"),
        ("Confidence", "50%"),
    ]


def test_image_healthy_match_lines():
    lines = ResultPresenter().result_lines(image_result(OUTCOME_HEALTHY_MATCHED))
    assert lines == [
        ("Source", "Image model"),
        ("Crop", "Wheat"),
        ("Outcome", TEXT_HEALTHY),
        ("Confidence", "50%"),
    ]


def test_image_no_match_shows_no_disease_and_no_confidence():
    lines = ResultPresenter().result_lines(image_result(OUTCOME_NO_MATCH))
    assert lines == [
        ("Source", "Image model"),
        ("Crop", "Wheat"),
        ("Outcome", TEXT_NO_MATCH),
    ]


# Text results

def test_text_disease_match_lines():
    result = text_result(OUTCOME_DISEASE_MATCHED)
    lines = ResultPresenter().result_lines(result)
    assert lines == [
        ("Source", "AI workflow"),
        ("Crop", "Wheat"),
        ("Outcome", "Placeholder Disease"),
        ("Explanation", result.explanation),
    ]


def test_text_healthy_match_lines():
    result = text_result(OUTCOME_HEALTHY_MATCHED)
    lines = ResultPresenter().result_lines(result)
    assert lines == [
        ("Source", "AI workflow"),
        ("Crop", "Wheat"),
        ("Outcome", TEXT_HEALTHY),
        ("Explanation", result.explanation),
    ]


def test_text_no_match_shows_the_explanation_and_never_a_confidence():
    result = text_result(OUTCOME_NO_MATCH)
    lines = ResultPresenter().result_lines(result)
    assert lines == [
        ("Source", "AI workflow"),
        ("Crop", "Wheat"),
        ("Outcome", TEXT_NO_MATCH),
        ("Explanation", result.explanation),
    ]


def test_sugarcane_is_shown_as_sugarcane_in_a_result():
    lines = ResultPresenter().result_lines(image_result(OUTCOME_DISEASE_MATCHED, "SugarCane"))
    assert ("Crop", "Sugarcane") in lines
    assert ("Outcome", "Placeholder Disease") in lines