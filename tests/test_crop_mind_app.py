import io

from PIL import Image

from app.crop_mind_app import IMAGE_MODE, MSG_UNEXPECTED, TEXT_MODE, CropMindApp
from app.input_validator import InputValidator
from app.stubs.stub_image_service import StubImageService
from app.stubs.stub_text_service import StubTextService
from results.assessment_result import (
    OUTCOME_DISEASE_MATCHED,
    OUTCOME_HEALTHY_MATCHED,
    OUTCOME_NO_MATCH,
    SOURCE_AI_WORKFLOW,
    SOURCE_IMAGE_MODEL,
)


def good_image():
    """A tiny real PNG, built in memory, with a file name."""
    buffer = io.BytesIO()
    Image.new("RGB", (10, 10), "green").save(buffer, format="PNG")
    file = io.BytesIO(buffer.getvalue())
    file.name = "leaf.png"
    return file


class CountingImage(StubImageService):
    """The image stub, counting how often it is called."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.calls = 0

    def predict(self, image, crop):
        self.calls += 1
        return super().predict(image, crop)


class CountingText(StubTextService):
    """The text stub, counting how often it is called."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.calls = 0

    def analyse(self, symptoms, crop):
        self.calls += 1
        return super().analyse(symptoms, crop)


class BrokenService:
    """A service that fails in a way nobody planned."""

    def predict(self, image, crop):
        raise RuntimeError("secret technical details")

    def analyse(self, symptoms, crop):
        raise RuntimeError("secret technical details")


def make_app(image_service=None, text_service=None):
    return CropMindApp(
        image_service=image_service or StubImageService(),
        text_service=text_service or StubTextService(),
    )


# The nine paths of the plan

def test_image_disease_match():
    app = make_app(image_service=StubImageService(outcome=OUTCOME_DISEASE_MATCHED))
    result, error = app.assess(IMAGE_MODE, "Wheat", image=good_image())
    assert error is None
    assert result.source == SOURCE_IMAGE_MODEL
    assert result.outcome == OUTCOME_DISEASE_MATCHED
    assert result.disease == "Wheat_Placeholder_Disease"


def test_image_healthy_match():
    app = make_app(image_service=StubImageService(outcome=OUTCOME_HEALTHY_MATCHED))
    result, error = app.assess(IMAGE_MODE, "Cotton", image=good_image())
    assert error is None
    assert result.outcome == OUTCOME_HEALTHY_MATCHED
    assert result.disease == "Cotton_Healthy"


def test_image_no_match_is_a_result_and_not_an_error():
    app = make_app(image_service=StubImageService(outcome=OUTCOME_NO_MATCH))
    result, error = app.assess(IMAGE_MODE, "Wheat", image=good_image())
    assert error is None
    assert result.outcome == OUTCOME_NO_MATCH
    assert result.disease == ""


def test_text_disease_match():
    app = make_app(text_service=StubTextService(outcome=OUTCOME_DISEASE_MATCHED))
    result, error = app.assess(TEXT_MODE, "Wheat", symptoms="yellow spots")
    assert error is None
    assert result.source == SOURCE_AI_WORKFLOW
    assert result.outcome == OUTCOME_DISEASE_MATCHED
    assert result.disease == "Wheat_Placeholder_Disease"


def test_text_healthy_match():
    app = make_app(text_service=StubTextService(outcome=OUTCOME_HEALTHY_MATCHED))
    result, error = app.assess(TEXT_MODE, "Cotton", symptoms="looks fine")
    assert error is None
    assert result.outcome == OUTCOME_HEALTHY_MATCHED
    assert result.disease == "Cotton_Healthy"


def test_text_no_match_is_a_result_and_not_an_error():
    app = make_app(text_service=StubTextService(outcome=OUTCOME_NO_MATCH))
    result, error = app.assess(TEXT_MODE, "Wheat", symptoms="odd symptoms")
    assert error is None
    assert result.outcome == OUTCOME_NO_MATCH
    assert result.disease == ""


def test_missing_image_shows_the_validator_message():
    result, error = make_app().assess(IMAGE_MODE, "Wheat", image=None)
    assert result is None
    assert error == InputValidator.MSG_NO_FILE


def test_wrong_file_type_shows_the_validator_message():
    file = io.BytesIO(b"some bytes")
    file.name = "leaf.pdf"
    result, error = make_app().assess(IMAGE_MODE, "Wheat", image=file)
    assert result is None
    assert error == InputValidator.MSG_WRONG_TYPE


def test_empty_text_shows_the_validator_message():
    result, error = make_app().assess(TEXT_MODE, "Wheat", symptoms="   ")
    assert result is None
    assert error == InputValidator.MSG_EMPTY_TEXT


def test_image_service_failure_shows_its_plain_message():
    app = make_app(image_service=StubImageService(fail=True))
    result, error = app.assess(IMAGE_MODE, "Wheat", image=good_image())
    assert result is None
    assert error == "The photo could not be checked. Please try again."


def test_text_service_failure_shows_its_plain_message():
    app = make_app(text_service=StubTextService(fail=True))
    result, error = app.assess(TEXT_MODE, "Wheat", symptoms="yellow spots")
    assert result is None
    assert error == "The description could not be checked. Please try again."


# Rules of the plan

def test_only_the_image_service_runs_in_image_mode():
    image_service, text_service = CountingImage(), CountingText()
    app = make_app(image_service, text_service)
    app.assess(IMAGE_MODE, "Wheat", image=good_image(), symptoms="ignored")
    assert image_service.calls == 1
    assert text_service.calls == 0


def test_only_the_text_service_runs_in_text_mode():
    image_service, text_service = CountingImage(), CountingText()
    app = make_app(image_service, text_service)
    app.assess(TEXT_MODE, "Wheat", image=good_image(), symptoms="yellow spots")
    assert image_service.calls == 0
    assert text_service.calls == 1


def test_invalid_input_never_reaches_a_service():
    image_service, text_service = CountingImage(), CountingText()
    app = make_app(image_service, text_service)
    app.assess(IMAGE_MODE, "Wheat", image=None)
    app.assess(TEXT_MODE, "Wheat", symptoms="")
    assert image_service.calls == 0
    assert text_service.calls == 0


def test_screen_spelling_of_sugarcane_is_changed_for_the_services():
    app = make_app()
    result, error = app.assess(TEXT_MODE, "Sugarcane", symptoms="yellow spots")
    assert error is None
    assert result.crop == "SugarCane"


def test_unexpected_failure_shows_a_fixed_message_and_prints_details_to_the_terminal(capsys):
    app = make_app(image_service=BrokenService())
    result, error = app.assess(IMAGE_MODE, "Wheat", image=good_image())
    assert result is None
    assert error == MSG_UNEXPECTED
    assert "secret technical details" not in error
    assert "secret technical details" in capsys.readouterr().err


def test_unknown_crop_shows_the_fixed_message():
    result, error = make_app().assess(TEXT_MODE, "Rice", symptoms="yellow spots")
    assert result is None
    assert error == MSG_UNEXPECTED


def test_unknown_mode_shows_the_fixed_message():
    result, error = make_app().assess("Voice diagnosis", "Wheat")
    assert result is None
    assert error == MSG_UNEXPECTED