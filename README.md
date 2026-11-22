# CropMind 2.0 - Intelligent Crop Disease Diagnosis System

Software Engineering (CS-4525) mini project, BS AI-3B.

## About

CropMind 2.0 is a Python-based application that gives a preliminary assessment of a crop disease. The user can provide either a photograph of a crop or leaf, or a written description of the symptoms. It covers three crops: wheat, cotton and sugarcane, with nine classes for each crop (eight diseases and one healthy class). Every result is one of three outcomes: disease matched, healthy matched or no match, and each result states which module produced it.

## How it works

- **Photo route.** A MobileNetV2 model trained on 10,500 cleaned images in 27 classes. The app looks only at the nine classes of the selected crop. On unseen test photos it reaches 89.5% accuracy within the selected crop. With the confidence rule (0.80 for a disease, 0.85 for Healthy) it answers 83.6% of photos, and 96.6% of those answers are correct. When it is not sure, the result is no match.
- **Text route.** A language model (Groq gpt-oss-120b, with Gemini as an automatic backup) reads the typed symptoms. The code checks every reply, and anything unusable becomes no match.

## How to run

1. Install Python 3.12 (TensorFlow does not support newer versions yet) and create a clean environment.
2. Install the packages: `pip install -r requirements.txt`
3. Photo route: the trained model file (`stage2_finetune_best_v2.keras`) is not stored in this repository because of its size. Place it in a `models` folder in the project, or set the environment variable `CROPMIND_MODEL_PATH` to its location. Without it, the photo route shows a plain message and the text route still works.
4. Text route: copy `.env.example` to `.env` and write your own `GROQ_API_KEY` and `GEMINI_API_KEY` after the equals signs. The `.env` file is ignored by Git and must never be committed.
5. Start the screen: `python -m streamlit run app/main.py`
6. Run the tests: `python -m pytest tests -q`

## Limits

- It is a first assessment, not a replacement for an expert.
- A photo that is not a crop leaf can still get an answer, because the model has a fixed set of classes.
- Wheat is the weakest crop, because several wheat diseases look alike.
- The datasets and the model file are not included.

## Team

- Fatima Hafeez: group leader; datasets, image module and integration
- Sabeela Anwer: application and interface
- Areeba-tul-Islam: text module