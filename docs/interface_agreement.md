# CropMind 2.0 interface agreement (Version 1)

Status: agreed by Fatima, Sabeela and Areeba on 15 November 2026. Any change needs the agreement of all three members.

## 1. Purpose

This page says how the main screen talks to the two diagnosis services, so that each member can build and test their own part separately. The image service and the text service never call each other. The only link between them is the interface layer (CropMindApp). Both services depend only on the `results` folder.

## 2. The two calls

| Item | Agreement |
| --- | --- |
| Image call | `ImageDiagnosisService.predict(image, crop)` returns an `ImagePrediction`. The name `predict` is final. |
| Text call | `TextDiagnosisService.analyse(symptoms, crop)` returns a `TextAssessment`. |
| image | The upload file object from the Streamlit widget, passed as it is. The image service rewinds it (`seek(0)`) and opens it with Pillow itself. |
| symptoms | The written description as text. The screen has already checked that it is not empty. |
| crop | One of `Cotton`, `SugarCane` or `Wheat`. The image result is one of the nine classes of that crop. The screen shows `SugarCane` as Sugarcane. |

## 3. The result

Both services return a result object with these fields. `ImagePrediction` and `TextAssessment` extend `AssessmentResult`.

| Field | Used by | Meaning |
| --- | --- | --- |
| `source` | Both | Exactly `Image model` or `AI workflow`, kept as two constants in `results/assessment_result.py`. Shown on screen as they are. |
| `crop` | Both | The selected crop (`Cotton`, `SugarCane` or `Wheat`). |
| `outcome` | Both | One of `disease_matched`, `healthy_matched` or `no_match`. |
| `disease` | Both | The exact label from the class list. For `healthy_matched` it is the healthy label, for example `Wheat_Healthy`. For `no_match` it is empty. |
| `confidence` | Image only | A number from 0 to 1: the highest probability the model gave to a class of the selected crop. Always present, also for `no_match`. The screen shows it only for a match. |
| `explanation` | Text only | A short written reason. For `no_match` it says briefly that the description did not clearly fit a listed disease. Text results have no confidence. |

The field is named `disease` everywhere. A `no_match` is a normal result and is never treated as an error. The image service applies the confidence rule itself, so the screen never sees a threshold.

## 4. Errors

- The services raise `DiagnosisError` (in `results/errors.py`) for an unreadable image, a model failure, or a text service failure (both providers failed).
- The message is one or two plain sentences for the user. It contains no code messages, file paths, provider responses or exception text. Technical details go to the terminal log only.
- The screen catches `DiagnosisError` and shows its message in the error area.
- `InputValidator` is the exception: it returns a short plain message when something is wrong and `None` when the input is fine, and the screen shows the message.

## 5. Input checks

- Images: JPEG or PNG, judged by their content and not by the file name, up to 10 MB. A file of exactly 10 MB is accepted.
- Text: not empty and not only spaces.

## 6. Labels and display

- The agreed class list is `docs/class_list.md`. The same labels are in `results/class_labels.py`, which every module imports. Nobody retypes a label.
- Services return exact labels, for example `Wheat_Healthy`.
- The screen (`ResultPresenter`) turns a label into the words the user reads: remove the crop prefix and replace underscores with spaces, and show `SugarCane` as Sugarcane.

## 7. Where things live

| File | Content | Owner |
| --- | --- | --- |
| `results/assessment_result.py` | `AssessmentResult`, the three outcome words, the two source constants | Sabeela |
| `results/errors.py` | `DiagnosisError` | Sabeela |
| `results/image_prediction.py` | `ImagePrediction` | Fatima |
| `results/text_assessment.py` | `TextAssessment` | Areeba |
| `results/class_labels.py` | The 27 labels grouped by crop | Fatima |

Everyone imports from these files, for example `from results.assessment_result import AssessmentResult`.

## 8. Rules for everyone

- The image service and the text service are not linked to each other.
- API keys are read from environment variables only (`GROQ_API_KEY` and `GEMINI_API_KEY`). They are never written in code, screenshots, chat messages or the repository.
- Uploaded images and typed symptoms are not saved after use.
- The screen is started from the repository root with `python -m streamlit run app/main.py`, and the tests are run from the repository root with `python -m pytest`. The test tool is pytest.
- The temporary stubs in `app/stubs` return results of the same shape as above. A real service replaces its stub without any change to the screen.
