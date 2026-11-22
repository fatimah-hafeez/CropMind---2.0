"""Tests for the text module. They use fakes: no key and no internet needed."""

import pytest
import requests

from results.assessment_result import (
    OUTCOME_DISEASE_MATCHED,
    OUTCOME_HEALTHY_MATCHED,
    OUTCOME_NO_MATCH,
    SOURCE_AI_WORKFLOW,
)
from results.class_labels import LABELS_BY_CROP
from results.errors import DiagnosisError
from results.text_assessment import TextAssessment
from text_module.text_ai_client import (
    GEMINI_MODEL,
    GROQ_MODEL,
    NO_MATCH_EXPLANATION,
    SERVICE_FAILURE_MESSAGE,
    TEMPERATURE,
    TIMEOUT_SECONDS,
    TextAIClient,
    build_response_schema,
    build_user_message,
)
from text_module.text_diagnosis_service import TextDiagnosisService

GOOD_DISEASE = (
    '{"outcome":"disease_matched","disease":"Wheat_Brown_Rust",'
    '"explanation":"Orange-brown pustules on leaves."}'
)
GOOD_HEALTHY = (
    '{"outcome":"healthy_matched","disease":"Wheat_Healthy",'
    '"explanation":"No symptoms described."}'
)
GOOD_NO_MATCH = '{"outcome":"no_match","disease":"","explanation":"Too vague."}'


@pytest.fixture(autouse=True)
def placeholder_keys(monkeypatch):
    """Fake keys for every test. A real key is never used or needed."""
    monkeypatch.setenv("GROQ_API_KEY", "placeholder-not-a-real-key")
    monkeypatch.setenv("GEMINI_API_KEY", "placeholder-not-a-real-key")


class FakeResponse:
    def __init__(self, data):
        self._data = data

    def raise_for_status(self):
        pass

    def json(self):
        return self._data


def groq_reply(text):
    return FakeResponse({"choices": [{"message": {"content": text}}]})


def gemini_reply(text):
    return FakeResponse({"candidates": [{"content": {"parts": [{"text": text}]}}]})


class FakePost:
    """Stands in for requests.post and records what it receives.

    A provider whose answer is None fails with a timeout.
    """

    def __init__(self, groq=None, gemini=None):
        self.groq = groq
        self.gemini = gemini
        self.calls = []

    def __call__(self, url, headers, json, timeout):
        provider = "groq" if "groq" in url else "gemini"
        self.calls.append(
            {"provider": provider, "url": url, "headers": headers,
             "body": json, "timeout": timeout}
        )
        answer = self.groq if provider == "groq" else self.gemini
        if answer is None:
            raise requests.exceptions.Timeout()
        return answer

    def providers(self):
        return [call["provider"] for call in self.calls]


class FakeClient(TextAIClient):
    """A client that returns a prepared reply or raises a prepared error."""

    def __init__(self, reply=None, error=None):
        super().__init__()
        self.reply = reply
        self.error = error
        self.asked = []

    def ask_ai(self, symptoms, crop):
        self.asked.append((symptoms, crop))
        if self.error:
            raise self.error
        return self.reply


# ---------- TextAIClient: requests and providers ----------

def test_groq_request_uses_plan_settings():
    post = FakePost(groq=groq_reply(GOOD_DISEASE))
    TextAIClient(post=post).ask_groq("orange pustules", "Wheat")
    call = post.calls[0]
    assert call["body"]["model"] == GROQ_MODEL
    assert call["body"]["temperature"] == TEMPERATURE == 0.2
    assert call["timeout"] == TIMEOUT_SECONDS == 30
    assert call["body"]["messages"][0]["role"] == "system"
    assert call["body"]["response_format"]["json_schema"]["strict"] is True
    assert "Authorization" in call["headers"]


def test_groq_answer_does_not_call_gemini():
    post = FakePost(groq=groq_reply(GOOD_DISEASE), gemini=gemini_reply("x"))
    assert TextAIClient(post=post).ask_ai("orange pustules", "Wheat") == GOOD_DISEASE
    assert post.providers() == ["groq"]


def test_gemini_used_when_groq_fails():
    post = FakePost(groq=None, gemini=gemini_reply(GOOD_DISEASE))
    assert TextAIClient(post=post).ask_ai("orange pustules", "Wheat") == GOOD_DISEASE
    assert post.providers() == ["groq", "gemini"]


def test_gemini_request_uses_plan_settings():
    post = FakePost(groq=None, gemini=gemini_reply(GOOD_DISEASE))
    TextAIClient(post=post).ask_ai("orange pustules", "Wheat")
    call = post.calls[1]
    assert GEMINI_MODEL in call["url"]
    assert call["body"]["generationConfig"]["temperature"] == 0.2
    assert call["body"]["generationConfig"]["responseMimeType"] == "application/json"
    assert call["timeout"] == 30
    assert "x-goog-api-key" in call["headers"]


def test_both_providers_fail_raises_plain_error():
    post = FakePost(groq=None, gemini=None)
    with pytest.raises(DiagnosisError) as info:
        TextAIClient(post=post).ask_ai("orange pustules", "Wheat")
    assert str(info.value) == SERVICE_FAILURE_MESSAGE
    assert post.providers() == ["groq", "gemini"]


def test_missing_groq_key_falls_back_to_gemini(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    post = FakePost(gemini=gemini_reply(GOOD_DISEASE))
    assert TextAIClient(post=post).ask_ai("orange pustules", "Wheat") == GOOD_DISEASE
    assert post.providers() == ["gemini"]


def test_missing_both_keys_raises_plain_error(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    post = FakePost()
    with pytest.raises(DiagnosisError) as info:
        TextAIClient(post=post).ask_ai("orange pustules", "Wheat")
    assert str(info.value) == SERVICE_FAILURE_MESSAGE
    assert post.calls == []


# ---------- Prompt pieces: only the selected crop's labels ----------

def test_schema_only_allows_labels_of_selected_crop():
    allowed = build_response_schema("Wheat")["properties"]["disease"]["enum"]
    assert set(allowed) == set(LABELS_BY_CROP["Wheat"]) | {""}
    assert "Cotton_Curl_Virus" not in allowed


def test_message_lists_only_selected_crop_labels():
    message = build_user_message("orange pustules", "Wheat")
    assert all(label in message for label in LABELS_BY_CROP["Wheat"])
    assert not any(label in message for label in LABELS_BY_CROP["Cotton"])


# ---------- TextAIClient: reply validation ----------

@pytest.mark.parametrize(
    "reply, outcome, disease",
    [
        (GOOD_DISEASE, OUTCOME_DISEASE_MATCHED, "Wheat_Brown_Rust"),
        (GOOD_HEALTHY, OUTCOME_HEALTHY_MATCHED, "Wheat_Healthy"),
        (GOOD_NO_MATCH, OUTCOME_NO_MATCH, ""),
    ],
    ids=["disease", "healthy", "no match"],
)
def test_good_replies_are_kept(reply, outcome, disease):
    result = TextAIClient().check_reply(reply, "Wheat")
    assert result["outcome"] == outcome
    assert result["disease"] == disease


NO_MATCH_CASES = [
    ("broken JSON", '{"outcome": "disease_matched", '),
    ("not an object", "[1, 2]"),
    ("nothing at all", None),
    ("disease of another crop",
     '{"outcome":"disease_matched","disease":"Cotton_Curl_Virus","explanation":"x"}'),
    ("made-up disease",
     '{"outcome":"disease_matched","disease":"Wheat_Purple_Spot","explanation":"x"}'),
    ("missing field",
     '{"outcome":"disease_matched","disease":"Wheat_Brown_Rust"}'),
    ("unknown outcome",
     '{"outcome":"maybe","disease":"Wheat_Brown_Rust","explanation":"x"}'),
    ("disease_matched with healthy label",
     '{"outcome":"disease_matched","disease":"Wheat_Healthy","explanation":"x"}'),
    ("healthy_matched with a disease",
     '{"outcome":"healthy_matched","disease":"Wheat_Brown_Rust","explanation":"x"}'),
    ("no_match with a disease",
     '{"outcome":"no_match","disease":"Wheat_Brown_Rust","explanation":"x"}'),
    ("empty explanation",
     '{"outcome":"disease_matched","disease":"Wheat_Brown_Rust","explanation":"  "}'),
]


@pytest.mark.parametrize(
    "reply", [case[1] for case in NO_MATCH_CASES],
    ids=[case[0] for case in NO_MATCH_CASES],
)
def test_unusable_reply_becomes_no_match(reply):
    result = TextAIClient().check_reply(reply, "Wheat")
    assert result["outcome"] == OUTCOME_NO_MATCH
    assert result["disease"] == ""
    assert result["explanation"] == NO_MATCH_EXPLANATION


# ---------- TextDiagnosisService ----------

def test_service_returns_disease_match():
    result = TextDiagnosisService(FakeClient(GOOD_DISEASE)).analyse(
        "orange pustules", "Wheat")
    assert isinstance(result, TextAssessment)
    assert result.source == SOURCE_AI_WORKFLOW
    assert result.crop == "Wheat"
    assert result.outcome == OUTCOME_DISEASE_MATCHED
    assert result.disease == "Wheat_Brown_Rust"
    assert result.explanation
    assert not hasattr(result, "confidence")


def test_service_returns_healthy_match():
    result = TextDiagnosisService(FakeClient(GOOD_HEALTHY)).analyse(
        "green and strong", "Wheat")
    assert result.outcome == OUTCOME_HEALTHY_MATCHED
    assert result.disease == "Wheat_Healthy"


def test_service_turns_unusable_reply_into_no_match():
    result = TextDiagnosisService(FakeClient("not json")).analyse(
        "the crop looks bad", "Wheat")
    assert result.outcome == OUTCOME_NO_MATCH
    assert result.disease == ""
    assert result.explanation == NO_MATCH_EXPLANATION


def test_service_failure_is_an_error_not_a_no_match():
    client = FakeClient(error=DiagnosisError(SERVICE_FAILURE_MESSAGE))
    with pytest.raises(DiagnosisError):
        TextDiagnosisService(client).analyse("orange pustules", "Wheat")


@pytest.mark.parametrize("symptoms", ["", "   ", None])
def test_empty_text_is_an_error_and_the_ai_is_not_asked(symptoms):
    client = FakeClient(GOOD_DISEASE)
    with pytest.raises(DiagnosisError):
        TextDiagnosisService(client).analyse(symptoms, "Wheat")
    assert client.asked == []


def test_unknown_crop_is_an_error():
    with pytest.raises(DiagnosisError):
        TextDiagnosisService(FakeClient(GOOD_DISEASE)).analyse("x", "Rice")