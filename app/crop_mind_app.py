import traceback

import streamlit as st

from app.input_validator import InputValidator
from app.result_presenter import ResultPresenter
from results.errors import DiagnosisError

# The two input modes. The screen and the controller both use these names.
IMAGE_MODE = "Image diagnosis"
TEXT_MODE = "Text diagnosis"

# What the screen shows for each crop, and the spelling the services expect.
CROP_CHOICES = {"Wheat": "Wheat", "Cotton": "Cotton", "Sugarcane": "SugarCane"}

# Shown when something unexpected breaks. It must stay short and plain.
MSG_UNEXPECTED = "Something went wrong. Please try again."

# Texts on the screen. Change the wording here and nowhere else.
FORMATS_NOTE = "Supported formats: JPEG and PNG, up to 10 MB."
STATUS_READY = "Choose a crop, add your photo or description, and press Submit."
STATUS_DONE = "The assessment is complete."
STATUS_FAILED = "The assessment could not be completed."

# Progress messages while an assessment is running.
STATUS_CHECKING_IMAGE = "Checking your photo."
STATUS_ANALYSING_IMAGE = "Analysing your photo. Please wait."
STATUS_CHECKING_TEXT = "Checking your description."
STATUS_ANALYSING_TEXT = "Analysing your description. Please wait."


class CropMindApp:
    """The main controller. It connects the screen to the two services."""

    def __init__(self, image_service, text_service, validator=None, presenter=None):
        self.image_service = image_service
        self.text_service = text_service
        self.validator = validator or InputValidator()
        self.presenter = presenter or ResultPresenter()

    def assess(self, mode, crop_choice, image=None, symptoms=None, report=None):
        """Run one assessment.

        Returns (result, error_message). One of the two is always None.
        Only one route runs: the image service or the text service.
        report is an optional function that receives each progress message.
        """
        report = report or (lambda message: None)
        try:
            crop = CROP_CHOICES[crop_choice]

            if mode == IMAGE_MODE:
                report(STATUS_CHECKING_IMAGE)
                message = self.validator.check_image(image)
                if message:
                    return None, message
                report(STATUS_ANALYSING_IMAGE)
                return self.image_service.predict(image, crop), None

            if mode == TEXT_MODE:
                report(STATUS_CHECKING_TEXT)
                message = self.validator.check_text(symptoms)
                if message:
                    return None, message
                report(STATUS_ANALYSING_TEXT)
                return self.text_service.analyse(symptoms, crop), None

            raise ValueError(f"Unknown mode: {mode}")

        except DiagnosisError as error:
            # A service gave a plain message that is safe to show.
            return None, str(error)
        except Exception:
            # Technical details go to the terminal only, never to the screen.
            traceback.print_exc()
            return None, MSG_UNEXPECTED

    def run(self):
        """Draw the screen and react to the buttons. Streamlit calls this on every redraw."""
        st.set_page_config(page_title="CropMind 2.0", layout="centered")

        state = st.session_state
        for name, start in (("run_id", 0), ("result", None), ("error", None)):
            if name not in state:
                state[name] = start
        key = state["run_id"]  # a new number gives fresh, empty widgets

        st.title("CropMind 2.0")
        st.write("Preliminary assessment of crop disease for wheat, cotton and sugarcane.")

        # Elements 1 and 2: input mode and crop
        mode = st.radio(
            "Input mode",
            [IMAGE_MODE, TEXT_MODE],
            horizontal=True,
            key=f"mode_{key}",
            on_change=self._clear_outcome,
        )
        crop_choice = st.selectbox(
            "Crop",
            list(CROP_CHOICES),
            key=f"crop_{key}",
            on_change=self._clear_outcome,
        )

        # Elements 3 and 4: input area and supported formats note
        image = None
        symptoms = None
        if mode == IMAGE_MODE:
            image = st.file_uploader(
                "Photo of the crop or leaf",
                key=f"image_{key}",
                on_change=self._clear_outcome,
            )
            st.caption(FORMATS_NOTE)
        else:
            symptoms = st.text_area(
                "Describe the symptoms you see",
                height=150,
                key=f"symptoms_{key}",
                on_change=self._clear_outcome,
            )

        # Element 5: submit button. The click is handled below the status area.
        submitted = st.button("Submit")

        # Element 6: status area
        st.subheader("Status")
        status_area = st.empty()

        if submitted:
            result, error = self.assess(
                mode,
                crop_choice,
                image=image,
                symptoms=symptoms,
                report=status_area.write,
            )
            state["result"] = result
            state["error"] = error

        if state["error"]:
            status_area.write(STATUS_FAILED)
        elif state["result"] is not None:
            status_area.write(STATUS_DONE)
        else:
            status_area.write(STATUS_READY)

        # Element 7: result area
        if state["result"] is not None:
            st.subheader("Result")
            self.presenter.show_result(state["result"])

        # Element 8: error message area
        if state["error"]:
            self.presenter.show_error(state["error"])

        # Element 9: start a new assessment
        if st.button("Start new assessment"):
            state["run_id"] += 1
            state["result"] = None
            state["error"] = None
            st.rerun()

    def _clear_outcome(self):
        """Forget the last result when the mode, crop, photo or description changes."""
        st.session_state["result"] = None
        st.session_state["error"] = None