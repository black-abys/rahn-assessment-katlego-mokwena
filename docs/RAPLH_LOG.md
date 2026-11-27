# RAPLH Log

**Tool used:** Claude (chat), writing code and documents; tests run in Claude's sandbox. All entries below are **genuine records** of what happened in that session. No entries are illustrative. In both iterations the tests passed on the first run, so no fix was needed; I have not invented a failure.

## Entry 1 (genuine): R, A, P and first build
- **Task / expectation:** Build the FitDesk assistant, SRS, tests and docs from the assessment PDFs. Expected the 6 required scenarios to pass with a mocked AI.
- **Prompt summary:** "Build the SRS and the rest", with both PDFs and the invitation email attached.
- **R / A / P done:** Requirements pulled out (CLI, Gemini JSON + Pydantic, local lookup, exact escalation phrase, approval, status log, never "sent" on the four conditions). Risks: AI inventing facts, AI failures, approval bypass. Plan: design so the AI only *classifies* and code writes the reply, which makes the no-invented-data rule structural.
- **Files changed:** `fitdesk/*.py`, `main.py`, `data/fitdesk_data.json`, `tests/test_fitdesk.py`, `requirements.txt`, `.env.example`, `.gitignore`, `docs/SRS.md`.
- **Test run:** `python -m pytest -v` gave **16 passed in 0.17s**.
- **Corrected:** Nothing needed correcting.
- **Decision:** approved.

## Entry 2 (genuine): verification beyond the mocks
- **Task / expectation:** Check what mocks cannot: the real CLI and Gemini SDK path should fail safe, and the SDK should accept the Pydantic schema.
- **Prompt summary:** Run `main.py` with no key, with a fake key, and build the SDK config from `EnquiryAnalysis`.
- **Files changed:** none (read-only checks; the temporary `status_log.json` was deleted afterwards).
- **Tests / results:** No key gave `failed_ai_service` logged. Fake key gave `ConnectError` caught and `failed_ai_service` logged. SDK accepted the schema. At that point, a live call with a real key had not been run (no key or network in the build environment).
- **Live call (27 Nov 2026, my own free key):** `gemini-2.5-flash` returned 404 NOT_FOUND (no longer available to new users). `gemini-3.5-flash` and `gemini-3.8-flash` both failed safe with 504 DEADLINE_EXCEEDED inside the 20s timeout, logged as `failed_ai_service`. `gemini-3.5-flash-lite` returned valid JSON (`package_and_availability`, packages `["12"]`); the draft showed R1,680 and the Saturday slots (09:00 available, 10:00 full, 11:00 available); staff answered `n`, status `rejected`.
- **Corrected:** Default model changed to `gemini-3.5-flash-lite` in `fitdesk/ai.py` and `.env.example`; all 16 tests still pass.
- **Decision:** approved.

## Reflection

**1. How would you stop an AI coding agent from changing unrelated files or exposing your API key?**

Give the agent an explicit list of files per task and review the diff (`git diff --stat`) before accepting anything. Keep the key only in `.env`, which is in `.gitignore`, commit `.env.example`, and check `git status` before every commit. Never paste the key into prompts.

**2. How would you stop the loop if the agent keeps repeating the same failed fix?**

Cap attempts (the playbook says two identical failures). On the second identical failure, stop, read the actual error myself, change the approach (smaller test, different hypothesis), and if still stuck, escalate to a mentor instead of letting the agent retry.
