"""The result of the image route: AssessmentResult plus the model confidence.

Same name and fields as the placeholder in app/stubs/stub_results.py, so
only the import lines change when the real service is connected.
"""

from dataclasses import dataclass

from results.assessment_result import AssessmentResult


@dataclass
class ImagePrediction(AssessmentResult):
    """AssessmentResult plus the confidence of the image model, 0 to 1."""

    confidence: float
