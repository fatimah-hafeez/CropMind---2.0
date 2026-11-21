from app.crop_mind_app import CropMindApp
import streamlit as st

from image_module import settings
from image_module.image_classifier import ImageClassifier
from image_module.image_diagnosis_service import ImageDiagnosisService
from results.errors import DiagnosisError
from app.stubs.stub_text_service import StubTextService

# TEMPORARY. For trying the screen with the stubs only.
# Remove these two lines and the stubs when the real services arrive.
# STUB_OUTCOME is one of: "disease_matched", "healthy_matched", "no_match".
STUB_OUTCOME = "disease_matched"
# Set to True to simulate a service failure.
STUB_FAIL = False

@st.cache_resource(show_spinner="Loading the photo model...")
def load_image_service():
    """Build the real image service once. Streamlit runs this file again on every click."""
    classifier = ImageClassifier(settings.MODEL_PATH)
    try:
        classifier.load()
    except DiagnosisError:
        pass  # the user sees the plain message when a photo is checked
    return ImageDiagnosisService(classifier)

app = CropMindApp(
    image_service=load_image_service(),
    text_service=StubTextService(outcome=STUB_OUTCOME, fail=STUB_FAIL),
)
app.run()