import io

from PIL import Image

from app.crop_mind_app import (
    IMAGE_MODE,
    STATUS_ANALYSING_IMAGE,
    STATUS_ANALYSING_TEXT,
    STATUS_CHECKING_IMAGE,
    STATUS_CHECKING_TEXT,
    TEXT_MODE,
    CropMindApp,
)
from app.stubs.stub_image_service import StubImageService
from app.stubs.stub_text_service import StubTextService


def good_image():
    """A tiny real PNG, built in memory, with a file name."""
    buffer = io.BytesIO()
    Image.new("RGB", (10, 10), "green").save(buffer, format="PNG")
    file = io.BytesIO(buffer.getvalue())
    file.name = "leaf.png"
    return file


def make_app(image_service=None, text_service=None):
    return CropMindApp(
        image_service=image_service or StubImageService(),
        text_service=text_service or StubTextService(),
    )


def test_image_route_reports_its_progress_in_order():
    messages = []
    make_app().assess(IMAGE_MODE, "Wheat", image=good_image(), report=messages.append)
    assert messages == [STATUS_CHECKING_IMAGE, STATUS_ANALYSING_IMAGE]


def test_text_route_reports_its_progress_in_order():
    messages = []
    make_app().assess(TEXT_MODE, "Wheat", symptoms="yellow spots", report=messages.append)
    assert messages == [STATUS_CHECKING_TEXT, STATUS_ANALYSING_TEXT]


def test_invalid_image_stops_after_the_checking_message():
    messages = []
    make_app().assess(IMAGE_MODE, "Wheat", image=None, report=messages.append)
    assert messages == [STATUS_CHECKING_IMAGE]


def test_invalid_text_stops_after_the_checking_message():
    messages = []
    make_app().assess(TEXT_MODE, "Wheat", symptoms="   ", report=messages.append)
    assert messages == [STATUS_CHECKING_TEXT]


def test_a_failing_service_still_reports_that_it_was_analysing():
    messages = []
    app = make_app(image_service=StubImageService(fail=True))
    result, error = app.assess(IMAGE_MODE, "Wheat", image=good_image(), report=messages.append)
    assert messages == [STATUS_CHECKING_IMAGE, STATUS_ANALYSING_IMAGE]
    assert result is None
    assert error is not None