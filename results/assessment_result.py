from dataclasses import dataclass

# The two places a result can come from. Every result states its source.
SOURCE_IMAGE_MODEL = "Image model"
SOURCE_AI_WORKFLOW = "AI workflow"

# The three possible outcomes of an assessment.
OUTCOME_DISEASE_MATCHED = "disease_matched"
OUTCOME_HEALTHY_MATCHED = "healthy_matched"
OUTCOME_NO_MATCH = "no_match"


@dataclass
class AssessmentResult:
    """The fields that every result carries, whichever route produced it.

    source:  SOURCE_IMAGE_MODEL or SOURCE_AI_WORKFLOW
    crop:    "Cotton", "SugarCane" or "Wheat"
    outcome: one of the three OUTCOME_ constants
    disease: the class label for a disease match or a healthy match,
             and an empty string for no_match
    """

    source: str
    crop: str
    outcome: str
    disease: str