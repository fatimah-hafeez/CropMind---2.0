"""TextAssessment: the result of the text route. Owner: Areeba."""

from dataclasses import dataclass

from results.assessment_result import AssessmentResult


@dataclass
class TextAssessment(AssessmentResult):
    """AssessmentResult plus a short written explanation. No confidence."""

    explanation: str