"""Manual check of the real image service on real photos (not a unit test).

Usage, from the repository folder:
    python scripts\\check_image_service.py MODEL.keras VAL_FOLDER

VAL_FOLDER holds the 27 class folders of the VALIDATION split
(Datasets\\Split\\val). The test set is not used here.
Uses the frozen thresholds of image_module/settings.py.
"""

import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image  # noqa: E402

from image_module import settings  # noqa: E402
from image_module.image_classifier import ImageClassifier  # noqa: E402
from image_module.image_diagnosis_service import ImageDiagnosisService  # noqa: E402
from results.assessment_result import OUTCOME_NO_MATCH  # noqa: E402
from results.class_labels import ALL_LABELS, CROPS  # noqa: E402
from results.errors import DiagnosisError  # noqa: E402

PER_CLASS = 3

model_path, val_dir = sys.argv[1], sys.argv[2]
service = ImageDiagnosisService(ImageClassifier(model_path))
print(f"Thresholds: disease {settings.T_DISEASE}, healthy {settings.T_HEALTHY}")

# 1. A few validation photos per class, through the real rule
answered = correct = no_match = 0
for label in ALL_LABELS:
    crop = next(c for c in CROPS if label.startswith(c + "_"))
    folder = os.path.join(val_dir, label)
    files = sorted(os.listdir(folder))[:PER_CLASS]
    row = []
    for name in files:
        result = service.predict(os.path.join(folder, name), crop)
        if result.outcome == OUTCOME_NO_MATCH:
            no_match += 1
            row.append(f"no match ({result.confidence:.2f})")
        else:
            answered += 1
            correct += result.disease == label
            row.append(("right" if result.disease == label else f"WRONG: {result.disease}") + f" ({result.confidence:.2f})")
    print(f"{label:30s} " + ", ".join(row))
total = answered + no_match
print(f"\n{total} photos: {answered} answered, {no_match} no match, {correct} right among the answered")

# 2. The same photo as a path, as bytes, as an upload and as a PIL image
folder = os.path.join(val_dir, "Wheat_Healthy")
sample = os.path.join(folder, sorted(os.listdir(folder))[0])
with open(sample, "rb") as f:
    raw = f.read()
print("\nSame photo, four input types (the first three must be identical):")
print("  path   ", service.predict(sample, "Wheat"))
print("  bytes  ", service.predict(raw, "Wheat"))
print("  upload ", service.predict(io.BytesIO(raw), "Wheat"))
with Image.open(sample) as pil_image:
    print("  PIL    ", service.predict(pil_image, "Wheat"), "(may differ in the last digits)")

# 3. A photo of the wrong crop must give no match
cotton_folder = os.path.join(val_dir, "Cotton_Alternaria_Leaf_Spot")
cotton = os.path.join(cotton_folder, sorted(os.listdir(cotton_folder))[0])
print("\nCotton photo with Cotton selected: ", service.predict(cotton, "Cotton").outcome)
print("Cotton photo with Wheat selected:  ", service.predict(cotton, "Wheat").outcome, "(expected no_match)")

# 4. Errors
try:
    service.predict(b"this is not an image", "Wheat")
    print("\nBroken photo: NO ERROR (this is wrong)")
except DiagnosisError as error:
    print("\nBroken photo gives DiagnosisError:", error)
try:
    service.predict(sample, "Rice")
    print("Unknown crop: NO ERROR (this is wrong)")
except ValueError as error:
    print("Unknown crop gives ValueError:", error)
try:
    ImageDiagnosisService(ImageClassifier("no_such_model.keras")).predict(sample, "Wheat")
    print("Missing model: NO ERROR (this is wrong)")
except DiagnosisError as error:
    print("Missing model gives DiagnosisError:", error)
