"""Settings of the image module. The ONLY place for the thresholds and the model path.

The two thresholds were chosen in A10 (21 November 2026) on the validation
images and the tune half of the out-of-scope set. They are frozen. Do not
change them, and do not copy the numbers into any other file.

T_DISEASE: minimum confidence to accept a disease or pest answer.
T_HEALTHY: minimum confidence to accept a Healthy answer. It is stricter,
           because calling a sick plant healthy is the more harmful mistake.

The confidence is the RAW probability that the 27-class model gives to the
best class of the selected crop. Below the threshold the result is "no match".
"""

import os
from pathlib import Path

T_DISEASE = 0.80
T_HEALTHY = 0.85

# The 24 MB model file is NOT committed to Git. Put it in the "models" folder of
# the repository, or point to it with the CROPMIND_MODEL_PATH environment variable.
MODEL_FILE_NAME = "stage2_finetune_best_v2.keras"
_REPO_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = Path(os.environ.get("CROPMIND_MODEL_PATH", _REPO_ROOT / "models" / MODEL_FILE_NAME))
