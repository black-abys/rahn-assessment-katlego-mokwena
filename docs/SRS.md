# FitDesk Enquiry Assistant: Mini SRS

## 1. Business objective
The Hermanus studio owner wants staff to stop typing the same price and Saturday-availability replies by hand, without ever sending a wrong price or a made-up slot. The assistant drafts accurate replies from approved data; a staff member approves each one.

## 2. Stakeholders
- **Studio owner:** owns the price list and availability file; carries the risk of wrong information.
- **Front-desk staff:** run the assistant, approve or reject each draft.
- **Customers:** receive the reply; need correct prices and slots.
- **RAHN developer / mentor:** maintains the code and tests.

## 3. Scope
**In scope:** one customer message at the command line; AI classification into JSON; lookup in a local data file; a drafted reply; a y/n approval step; a local status log.

**Out of scope:** WhatsApp, bookings, payments, calendar or Sheets integration, free-form AI-written replies, multi-message conversations, discounts or negotiation.

## 4. Functional requirements
- **FR-01** Accept a customer message typed at the command line (argument or prompt).
- **FR-02** Send the message to the Gemini API and receive JSON with at least `intent`, `details`, `requires_human_approval`.
- **FR-03** Validate the AI output against a Pydantic model; anything else is rejected.
- **FR-04** Look up prices and Saturday slots in the local data file; the draft contains only facts from that file (the AI never writes the reply text).
- **FR-05** If a requested fact is not in the data, the draft uses exactly: "I'll check with the owner and come back to you."
- **FR-06** If the AI output is invalid, show no draft, skip approval, and record `failed_invalid_ai_output`.
- **FR-07** If the AI service fails or times out, skip approval and record `failed_ai_service`.
- **FR-08** Print the draft and ask "Send? (y/n)". Only `y` records `sent`; `n` or any other answer records `rejected`.
- **FR-09** Record every outcome (including empty input, `invalid_input`) in `status_log.json` with timestamp, message, draft, status and reason.

## 5. Non-functional requirements
- **NFR-01 Security:** the API key lives only in `.env` (git-ignored; `.env.example` committed). The customer message is treated as untrusted data; it can never change prices because replies are built by code, not by the AI.
- **NFR-02 Reliability:** every failure path ends in "not sent". Tests run offline in under 5 seconds with the AI mocked.
- **NFR-03 Cost:** free Gemini tier only; one API call per enquiry; 20-second timeout; tests make zero API calls.

## 6. Data inputs and outputs
- **Inputs:** customer text; `data/fitdesk_data.json` (3 packages, 3 Saturday slots); `GEMINI_API_KEY`.
- **Outputs:** printed draft reply; `status_log.json` entry. No message is actually delivered.

## 7. Approval and failure rules
- Staff say `n` (or give no valid answer after 3 tries): `rejected`, never `sent`.
- Fact missing: the escalation phrase is the draft (or its last line next to known facts); it is `sent` only if staff approve it.
- Invalid JSON/shape or AI failure: no draft shown, no approval asked, status is a `failed_*` value.
- `requires_human_approval` from the AI is recorded but never trusted to skip approval: staff are always asked.

## 8. Acceptance criteria
- **AC-1** Given "12-session pack and Saturday slots", the draft contains R1,680, "09:00: Available", "10:00: Full", "11:00: Available".
- **AC-2** Given a 20-session pack (not in data), the draft equals the escalation phrase and contains no price.
- **AC-3** Given invalid JSON, wrong-shape JSON, or a raised timeout, 0 `sent` records are written and the approval prompt is never shown.
- **AC-4** Given `n`, status is `rejected`; given `y`, status is `sent`.
- **AC-5** `pytest` passes with no API key set.

## 9. Ambiguities and assumptions
| # | What the brief leaves unclear | Question for the owner | Assumption made |
|---|---|---|---|
| 1 | Does the availability file cover one specific Saturday or a repeating one? Does "Full" mean a waiting list exists? | Which date does the file cover, and do you offer a waiting list? | The file is the current week's list; replies state "Full" only and do not mention dates or waiting lists. |
| 2 | What if only part of an enquiry can be answered? | Should staff get the partial answer or nothing? | Show known facts, then the escalation phrase on its own line, and flag it as an escalation. |
| 3 | Are prices VAT-inclusive, and is "5 sessions" valid for a set period? | Do prices include VAT and do packs expire? | Prices are shown as given in rand, with no claims about VAT or expiry. |
| 4 | Who counts as "staff" at the approval step? | Is any staff member allowed to approve? | Whoever is at the keyboard; no staff login in this version. |
