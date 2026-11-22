# CropMind 2.0: application and interface (A5)

This folder holds the Streamlit screen and the controller.

## Run the screen

Use Python 3.12 with the packages in requirements.txt, because TensorFlow
(used by the image model) does not support newer Python versions yet.

From the repository root, with the virtual environment active:

    python -m streamlit run app/main.py

Always start it from the repository root. The theme is read from
.streamlit/config.toml in the root, and it is not applied if the app
is started from another folder.

## What the two routes need

Image route: the model file stage2_finetune_best_v2.keras in the models folder
(see image_module/settings.py). The file is not in Git. Without it the screen
shows "The photo check is not available right now. Please try again later."

Text route: GROQ_API_KEY and GEMINI_API_KEY in a local .env file (copy
.env.example and add your own keys). Never commit .env. Without keys the
screen shows "The AI service could not give an assessment right now. Please
try again later."

Keys are read from environment variables only. They must never be written
in code, screenshots or the repository.

## Run the tests

    python -m pytest tests -v

The tests need no model, no key and no internet. They do not load
TensorFlow, so they also run in a newer Python than 3.12.

## How the screen connects to the services

The controller calls predict(image, crop) on the image service and
analyse(symptoms, crop) on the text service. Each returns a result with
source, crop, outcome and disease. The image result also has confidence,
and the text result also has explanation. A failure raises DiagnosisError
with a plain message.

app/main.py builds CropMindApp with ImageDiagnosisService and
TextDiagnosisService. The controller does not change when a service changes.

## Placeholder services

app/stubs holds placeholder services and result classes. app/main.py does
not use them. Four test files still import them, so they stay until those
tests are moved.s