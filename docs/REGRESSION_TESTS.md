# Regression Tests

All automated tests live in `tests/test_fitdesk.py` and mock the Gemini response (no API key, no network).

**Command:** `python -m pytest -v`

**Last full run:** 16 passed in 0.07s (Python 3.13.5, pytest 9.2.0).

| Test ID | Requirement | Input / precondition | Steps | Expected result | Actual result | Pass/Fail |
|---|---|---|---|---|---|---|
| TC-01 | FR-01, FR-02, FR-04, AC-1 | Mock AI returns `package_and_availability`, packages `["12"]` | Run `process_enquiry`, staff answer `y` | Draft has R1,680 and all three Saturday slots (10:00 Full); no escalation phrase; one prompt shown | As expected | Pass |
| TC-02 | FR-05, AC-2 | Mock AI returns `package_price`, packages `["20"]` | Run with answer `n` | Draft equals exactly "I'll check with the owner and come back to you."; no price; `needs_escalation` true | As expected | Pass |
| TC-03 | FR-03, FR-06, AC-3 | Mock AI returns `"this is not json"`, `"{}"`, or an unknown intent | Run for each; also run with an input function that fails if called | Status `failed_invalid_ai_output`; no `sent` record; approval never asked | As expected (4 cases) | Pass |
| TC-04 | FR-07, AC-3 | Mock AI raises `AIServiceError`, `TimeoutError`, `RuntimeError` | Run for each; approval input fails if called | Status `failed_ai_service` written to log; approval never asked | As expected (3 cases) | Pass |
| TC-05 | FR-08, AC-4 | Valid AI output for the 5-session pack | Staff answer `n` | Status `rejected`; no `sent` record in log | As expected | Pass |
| TC-06 | FR-08, AC-4 | Valid AI output for the 5-session pack | Staff answer `y` | Status `sent`; draft contains R800; one log record | As expected | Pass |
| TC-07 | FR-05, FR-08 | AI returns `other` with topic "discount" | Run with `n`, then with `y` | `n`: `rejected`. `y`: `sent` with `needs_escalation` true | As expected | Pass |
| TC-08 | FR-08 | Valid AI output | Staff type `maybe` three times | Status `rejected`; prompt shown 3 times | As expected | Pass |
| TC-09 | FR-04, FR-05 | AI asks for Saturday 10:00 and 14:00 | Run with `n` | Draft shows "10:00: Full", ends with escalation phrase, never mentions 14:00 | As expected | Pass |
| TC-10 | FR-09 | Message is only spaces | Run | Status `invalid_input`; AI never called | As expected | Pass |
| TC-11 (manual) | FR-07, NFR-02 | No `GEMINI_API_KEY` set | `python main.py "How much is the 12-session pack and do you have Saturday slots?"` | "Nothing was sent" message; log entry `failed_ai_service` | As expected | Pass |
| TC-12 (manual) | FR-07 | `GEMINI_API_KEY=fake`, no network in the test environment | `python main.py "hello"` | Real SDK path raises; logged as `failed_ai_service` | `ConnectError` caught; `failed_ai_service` logged | Pass |

**Live call (manual, 27 Nov 2026):** later run with a real free key, as recorded in RAPLH log entry 2. `gemini-2.5-flash` returned 404 (no longer available to new keys). `gemini-3.5-flash` and `gemini-3.8-flash` timed out with 504 and failed safe (`failed_ai_service`). `gemini-3.5-flash-lite` classified the sample enquiry correctly in about a second; the draft showed R1,680 and the Saturday slots (09:00 available, 10:00 full, 11:00 available); staff answered `n`, status `rejected`.
