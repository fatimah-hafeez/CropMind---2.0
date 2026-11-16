import streamlit as st

from results.assessment_result import OUTCOME_DISEASE_MATCHED, OUTCOME_HEALTHY_MATCHED

# What the farmer reads. Change the wording here and nowhere else.
TEXT_HEALTHY = "Healthy"
TEXT_NO_MATCH = "No match. The assessment did not clearly fit any listed disease for this crop."

# How a crop is written on the screen. The services use the key on the left.
DISPLAY_CROPS = {"Cotton": "Cotton", "SugarCane": "Sugarcane", "Wheat": "Wheat"}


class ResultPresenter:
    """Shows a result or an error message in a clear form."""

    def display_crop(self, crop):
        return DISPLAY_CROPS.get(crop, crop)

    def display_disease(self, label, crop):
        """Wheat_Brown_Rust becomes Brown Rust."""
        prefix = f"{crop}_"
        if label.startswith(prefix):
            label = label[len(prefix):]
        return label.replace("_", " ")

    def result_lines(self, result):
        """The lines to show, as (name, text) pairs. No drawing happens here."""
        lines = [
            ("Source", result.source),
            ("Crop", self.display_crop(result.crop)),
        ]

        if result.outcome == OUTCOME_DISEASE_MATCHED:
            lines.append(("Outcome", self.display_disease(result.disease, result.crop)))
        elif result.outcome == OUTCOME_HEALTHY_MATCHED:
            lines.append(("Outcome", TEXT_HEALTHY))
        else:
            lines.append(("Outcome", TEXT_NO_MATCH))

        # Only image results carry a confidence, and a no match never shows it.
        confidence = getattr(result, "confidence", None)
        if confidence is not None and result.outcome != "no_match":
            lines.append(("Confidence", f"{confidence:.0%}"))

        # Only text results carry an explanation.
        explanation = getattr(result, "explanation", None)
        if explanation:
            lines.append(("Explanation", explanation))

        return lines

    def show_result(self, result):
        for name, text in self.result_lines(result):
            st.write(f"{name}: {text}")

    def show_error(self, message):
        st.error(message)