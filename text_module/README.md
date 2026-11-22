# text_module

Text diagnosis service and classes. Gives a preliminary assessment of a crop
problem from a written description of symptoms. Crops: Cotton, SugarCane, Wheat.

## How it works

- `TextDiagnosisService.analyse(symptoms, crop)` returns a `TextAssessment`.
- `TextAIClient` sends the symptoms and the selected crop's label list to the AI
  service. Groq (`openai/gpt-oss-120b`) is used first, and Gemini
  (`gemini-3.5-flash-lite`) is used automatically only if Groq fails.
- Temperature is 0.2, the reply format is a strict JSON schema, and the timeout is
  30 seconds.
- Python checks every reply. Broken JSON, a missing field, an unknown outcome, a
  disease that is not on the crop's list, or a disease that does not fit the
  outcome all become `no_match`.
- The labels are imported from `results/class_labels.py`. Nothing is retyped.

## The result

`TextAssessment` has `source` (always `AI workflow`), `crop`, `outcome`
(`disease_matched`, `healthy_matched` or `no_match`), `disease` (the class label,
empty for `no_match`) and `explanation`. Text results have no confidence.

A `no_match` is a normal result. If both providers fail, or the text or crop is
not usable, `DiagnosisError` is raised with a short, plain message.

## Setup

1. Create and activate a virtual environment, then install the packages:
   `pip install requests python-dotenv pytest`
2. Copy `.env.example` to `.env` and write your own keys after the equals signs
   (`GROQ_API_KEY` and `GEMINI_API_KEY`). Never commit `.env` and never share a
   screen that shows it.

## Use

```python
from text_module.text_diagnosis_service import TextDiagnosisService

service = TextDiagnosisService()
result = service.analyse("orange-brown pustules on the leaves", "Wheat")
print(result.outcome, result.disease, result.explanation)
```

## Test

From the repository root: `python -m pytest tests/test_text_module.py -v`

The tests use fakes in place of Groq and Gemini, so no key and no internet are
needed.

## Limits found in live tests

- The text route gives a preliminary assessment. The same description gave
  different rust diseases in different runs, and Wheat has three rusts in its list.
- Answers can vary between runs, even at temperature 0.2.
- Groq returned a rate limit error (429) once, and the Gemini backup answered
  automatically. The cause was not investigated.
- There is no limit on the length of the text. A very long text of about 4,500
  characters was accepted.
- One text that told the AI to ignore its rules was answered with `no_match`. Only
  one such text was tried.
- The Groq free plan allows about 1,000 requests and 200,000 tokens per day. Keep
  live runs small, and check usage before the demonstration.
- Gemini model names change over time. Check that `gemini-3.5-flash-lite` is still
  available before the demonstration.
- Nothing is saved: no symptom text is stored, and no history is kept.