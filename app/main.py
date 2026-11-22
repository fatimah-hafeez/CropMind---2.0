from app.crop_mind_app import CropMindApp
import streamlit as st

from image_module import settings
from image_module.image_classifier import ImageClassifier
from image_module.image_diagnosis_service import ImageDiagnosisService
from results.errors import DiagnosisError
from text_module.text_diagnosis_service import TextDiagnosisService

@st.cache_resource(show_spinner="Loading the photo model...")
def load_image_service():
    """Build the real image service once. Streamlit runs this file again on every click."""
    classifier = ImageClassifier(settings.MODEL_PATH)
    try:
        classifier.load()
    except DiagnosisError:
        pass  # the user sees the plain message when a photo is checked
    return ImageDiagnosisService(classifier)

@st.cache_resource(show_spinner=False)
def load_text_service():
    """Build the text service once. Streamlit runs this file again on every click."""
    return TextDiagnosisService()


app = CropMindApp(
    image_service=load_image_service(),
    text_service=load_text_service(),
)
app.run()