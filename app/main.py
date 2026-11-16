from app.crop_mind_app import CropMindApp
from app.stubs.stub_image_service import StubImageService
from app.stubs.stub_text_service import StubTextService

# TEMPORARY. For trying the screen with the stubs only.
# Remove these two lines and the stubs when the real services arrive.
# STUB_OUTCOME is one of: "disease_matched", "healthy_matched", "no_match".
STUB_OUTCOME = "disease_matched"
# Set to True to simulate a service failure.
STUB_FAIL = False

app = CropMindApp(
    image_service=StubImageService(outcome=STUB_OUTCOME, fail=STUB_FAIL),
    text_service=StubTextService(outcome=STUB_OUTCOME, fail=STUB_FAIL),
)
app.run()