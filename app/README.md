# CropMind 2.0: application and interface (A5)

This folder holds the Streamlit screen and the controller.

## Run the screen

From the repository root, with the virtual environment active:

    python -m streamlit run app/main.py

Always start it from the repository root. The theme is read from
.streamlit/config.toml in the root, and it is not applied if the app
is started from another folder.

## Run the tests

    python -m pytest tests -v

## Current state

The screen uses placeholder services from app/stubs. They return fixed
answers and never read the photo or the text. In app/main.py, the two
marked lines STUB_OUTCOME and STUB_FAIL change what they return.
These switches are for trying the screen only and must not be committed
with a changed value.

## Connecting the real services

The controller calls predict(image, crop) on the image service and
analyse(symptoms, crop) on the text service. Each returns a result with
source, crop, outcome and disease. The image result also has confidence,
and the text result also has explanation. A failure raises DiagnosisError
with a plain message.

To connect a real service, pass it to CropMindApp in app/main.py in place
of the stub. The controller does not change. When both real services are
connected, delete app/stubs and the two STUB lines in app/main.py.

## Keys

Keys are read from environment variables only. They must never be written
in code, screenshots or the repository.