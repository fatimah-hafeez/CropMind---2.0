"""TextDiagnosisService: coordinates the text diagnosis (Step 10)."""

from results.assessment_result import SOURCE_AI_WORKFLOW
from results.class_labels import LABELS_BY_CROP
from results.errors import DiagnosisError
from results.text_assessment import TextAssessment
from text_module.text_ai_client import TextAIClient

# Short, plain messages that are safe to show to the user.
EMPTY_TEXT_MESSAGE = "Please describe the symptoms before asking for an assessment."
UNKNOWN_CROP_MESSAGE = "Please choose Cotton, Sugarcane or Wheat."


class TextDiagnosisService:
    """Receives the symptoms and the crop, and returns a TextAssessment."""

    def __init__(self, client=None):
        # Tests give a fake client, so no key or internet is needed.
        self._client = client or TextAIClient()

    def analyse(self, symptoms, crop):
        """Ask the AI, check its reply, and return a TextAssessment.

        A vague or unusable reply is a normal no_match result.
        A failed service (both providers) raises DiagnosisError.
        """
        # The screen's InputValidator checks this too.
        if not isinstance(symptoms, str) or not symptoms.strip():
            raise DiagnosisError(EMPTY_TEXT_MESSAGE)
        if crop not in LABELS_BY_CROP:
            raise DiagnosisError(UNKNOWN_CROP_MESSAGE)

        reply_text = self._client.ask_ai(symptoms, crop)  # may raise DiagnosisError
        checked = self._client.check_reply(reply_text, crop)

        return TextAssessment(
            source=SOURCE_AI_WORKFLOW,
            crop=crop,
            outcome=checked["outcome"],
            disease=checked["disease"],
            explanation=checked["explanation"],
        )