"""Regression tests. The Gemini call is mocked: no API key, no network."""
import json
import os

import pytest

from fitdesk.ai import AIServiceError
from fitdesk.app import process_enquiry
from fitdesk.replies import ESCALATION, normalise_package, normalise_time

DATA = os.path.join(os.path.dirname(__file__), "..", "data", "fitdesk_data.json")


def ai_json(intent, packages=(), times=(), other=()):
    return json.dumps({
        "intent": intent,
        "details": {"packages": list(packages), "saturday_times": list(times),
                    "other_topics": list(other)},
        "requires_human_approval": True,
    })


def run(tmp_path, ai, answer="y", message="test message"):
    log = tmp_path / "status_log.json"
    prompts = []

    def fake_input(prompt):
        prompts.append(prompt)
        return answer

    out = []
    entry = process_enquiry(message, data_path=DATA, log_path=str(log), call_ai=ai,
                            input_fn=fake_input, print_fn=out.append)
    records = json.loads(log.read_text())
    return entry, records, prompts, "\n".join(out)


def no_input_allowed(prompt):
    raise AssertionError("staff must not be asked to approve when the AI step failed")


# TC-01 / FR-01..FR-04: normal enquiry answered from data
def test_tc01_normal_enquiry(tmp_path):
    ai = lambda m: ai_json("package_and_availability", ["12"], [])
    entry, records, prompts, out = run(tmp_path, ai, answer="y")
    assert "R1,680" in entry["draft"]
    assert "Saturday 09:00: Available" in entry["draft"]
    assert "Saturday 10:00: Full" in entry["draft"]
    assert ESCALATION not in entry["draft"]
    assert prompts == ["Send? (y/n) "]


# TC-02 / FR-05: fact not in data -> exact escalation phrase, no invented price
def test_tc02_missing_fact_uses_escalation(tmp_path):
    ai = lambda m: ai_json("package_price", ["20"])
    entry, records, prompts, out = run(tmp_path, ai, answer="n")
    assert entry["draft"] == ESCALATION
    assert "R" not in entry["draft"].replace("Right", "")  # no price at all
    assert entry["needs_escalation"] is True


# TC-03 / FR-06: invalid JSON, and valid JSON with the wrong shape
@pytest.mark.parametrize("bad", ["this is not json", "{}", '{"intent": "refund", "details": {}}'])
def test_tc03_invalid_ai_output(tmp_path, bad):
    entry, records, _, _ = run(tmp_path, lambda m: bad)
    assert entry["status"] == "failed_invalid_ai_output"
    assert all(r["status"] != "sent" for r in records)


def test_tc03b_invalid_output_never_asks_approval(tmp_path):
    log = tmp_path / "log.json"
    entry = process_enquiry("hi", data_path=DATA, log_path=str(log),
                            call_ai=lambda m: "garbage", input_fn=no_input_allowed,
                            print_fn=lambda *_: None)
    assert entry["status"] == "failed_invalid_ai_output"


# TC-04 / FR-07: AI service failure or timeout
@pytest.mark.parametrize("exc", [AIServiceError("down"), TimeoutError("timed out"), RuntimeError("boom")])
def test_tc04_ai_service_failure(tmp_path, exc):
    def ai(m):
        raise exc
    log = tmp_path / "log.json"
    entry = process_enquiry("hi", data_path=DATA, log_path=str(log), call_ai=ai,
                            input_fn=no_input_allowed, print_fn=lambda *_: None)
    assert entry["status"] == "failed_ai_service"
    assert json.loads(log.read_text())[0]["status"] == "failed_ai_service"


# TC-05 / FR-08: staff say n -> never "sent"
def test_tc05_staff_rejects(tmp_path):
    entry, records, _, _ = run(tmp_path, lambda m: ai_json("package_price", ["5"]), answer="n")
    assert entry["status"] == "rejected"
    assert all(r["status"] != "sent" for r in records)


# TC-06 / FR-08: staff say y -> "sent"
def test_tc06_staff_approves(tmp_path):
    entry, records, _, _ = run(tmp_path, lambda m: ai_json("package_price", ["5"]), answer="y")
    assert entry["status"] == "sent"
    assert "R800" in entry["draft"]
    assert len(records) == 1


# TC-07 / FR-08: escalation message is only "sent" if staff approve it
def test_tc07_escalation_needs_approval(tmp_path):
    ai = lambda m: ai_json("other", other=["discount"])
    entry, _, _, _ = run(tmp_path, ai, answer="n")
    assert entry["status"] == "rejected"
    entry, _, _, _ = run(tmp_path, ai, answer="y")
    assert entry["status"] == "sent" and entry["needs_escalation"] is True


# TC-08 / FR-08: invalid approval answers fail safe
def test_tc08_invalid_approval_answers_not_sent(tmp_path):
    entry, _, prompts, _ = run(tmp_path, lambda m: ai_json("package_price", ["5"]), answer="maybe")
    assert entry["status"] == "rejected"
    assert len(prompts) == 3


# TC-09 / FR-04: partial answer keeps known facts and escalates the rest
def test_tc09_partial_facts(tmp_path):
    ai = lambda m: ai_json("saturday_availability", times=["10:00", "14:00"])
    entry, _, _, _ = run(tmp_path, ai, answer="n")
    assert "Saturday 10:00: Full" in entry["draft"]
    assert entry["draft"].endswith(ESCALATION)
    assert "14:00" not in entry["draft"]


# TC-10 / FR-09: empty message
def test_tc10_empty_message(tmp_path):
    log = tmp_path / "log.json"
    entry = process_enquiry("   ", data_path=DATA, log_path=str(log),
                            call_ai=lambda m: pytest.fail("AI must not be called"),
                            input_fn=no_input_allowed, print_fn=lambda *_: None)
    assert entry["status"] == "invalid_input"


def test_normalisers():
    assert normalise_time("9am") == "09:00"
    assert normalise_time("11:00") == "11:00"
    assert normalise_time("tomorrow") is None
    assert normalise_package("12-session pack") == "12"
    assert normalise_package("1 session") == "single"
