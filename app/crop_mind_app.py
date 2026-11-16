import traceback

from app.input_validator import InputValidator
from results.errors import DiagnosisError

# The two input modes. The screen and the controller both use these names.
IMAGE_MODE = "Image diagnosis"
TEXT_MODE = "Text diagnosis"

# What the screen shows for each crop, and the spelling the services expect.
CROP_CHOICES = {"Wheat": "Wheat", "Cotton": "Cotton", "Sugarcane": "SugarCane"}

# Shown when something unexpected breaks. It must stay short and plain.
MSG_UNEXPECTED = "Something went wrong. Please try again."


class CropMindApp:
    """The main controller. It connects the screen to the two services."""

    def __init__(self, image_service, text_service, validator=None):
        self.image_service = image_service
        self.text_service = text_service
        self.validator = validator or InputValidator()

    def assess(self, mode, crop_choice, image=None, symptoms=None):
        """Run one assessment.

        Returns (result, error_message). One of the two is always None.
        Only one route runs: the image service or the text service.
        """
        try:
            crop = CROP_CHOICES[crop_choice]

            if mode == IMAGE_MODE:
                message = self.validator.check_image(image)
                if message:
                    return None, message
                return self.image_service.predict(image, crop), None

            if mode == TEXT_MODE:
                message = self.validator.check_text(symptoms)
                if message:
                    return None, message
                return self.text_service.analyse(symptoms, crop), None

            raise ValueError(f"Unknown mode: {mode}")

        except DiagnosisError as error:
            # A service gave a plain message that is safe to show.
            return None, str(error)
        except Exception:
            # Technical details go to the terminal only, never to the screen.
            traceback.print_exc()
            return None, MSG_UNEXPECTED