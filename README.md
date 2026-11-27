# FitDesk Enquiry Assistant

RAHN January 2027 intern assessment — Katlego Mokwena

**Hours actually spent:** about 2 to 3 hours

A command-line enquiry assistant for a Hermanus fitness studio. Gemini classifies each customer message into validated JSON. Code then writes the reply from a local data file only, so the AI cannot invent a price or a Saturday slot. Staff must type `y` at "Send? (y/n)" before anything is logged as `sent`. Nothing is actually delivered.

**16 automated tests pass without an API key.** A live Gemini call on 27 Nov 2026 confirmed the real path: `gemini-2.5-flash` returned 404 for new keys; `gemini-3.5-flash` and `gemini-3.8-flash` timed out with 504 and failed safe; `gemini-3.5-flash-lite` classified the sample enquiry correctly in about a second. The draft showed R1,680 and the Saturday slots (09:00 available, 10:00 full, 11:00 available). Staff answered `n`; status `rejected`. That model is now the default.

## Setup
1. Install Python 3.10 or newer.
2. Clone this repo and open a terminal in its folder.
3. Create and activate a virtual environment:
   - macOS/Linux: `python3 -m venv .venv && source .venv/bin/activate`
   - Windows: `python -m venv .venv` then `.venv\Scripts\activate`
4. Install packages: `pip install -r requirements.txt`
5. Get a free key at https://aistudio.google.com/
6. Copy `.env.example` to `.env` and paste your key after `GEMINI_API_KEY=`. Never commit `.env`.

## Run
```
python main.py "How much is the 12-session pack and do you have Saturday slots?"
```
Or run `python main.py` and type the message when prompted. Outcomes are appended to `status_log.json` (`sent`, `rejected`, `failed_ai_service`, `failed_invalid_ai_output`, `invalid_input`).

## Test
```
python -m pytest -v
```
No API key needed. Last run: 16 passed.

## How it works
Customer message → Gemini returns JSON (`intent`, `details`, `requires_human_approval`) → Pydantic validation → lookup in `data/fitdesk_data.json` → reply built by code from that data → staff approval → status log.

The AI never writes the reply text. Missing facts produce exactly: "I'll check with the owner and come back to you."

Docs: `docs/SRS.md`, `docs/REGRESSION_TESTS.md`, `docs/RAPLH_LOG.md`.

## AI use
Claude (chat) wrote the code, tests, SRS, regression test document and RAPLH log, and ran the tests in its sandbox. I reviewed and can explain the code. I answered the Working style questions myself, out loud in my own words; an AI assistant then fixed spelling and grammar and smoothed the wording, and I reviewed the final versions. I know the brief asked for these without AI, so I am stating this openly.

## What doesn't work yet
- Live Gemini testing is limited to the one enquiry above. Other wordings are only covered by the mocked tests.
- Only English enquiries and a fixed set of sample packages and times. If the AI misclassifies unusual wording, the draft may escalate or show the wrong (but still data-true) facts, which staff must catch at approval.
- Dates are not modelled: "Saturday" means whatever the data file currently says.
- "Sent" only means recorded; nothing is delivered. Staff identity is not recorded.
- Single enquiry per run; no conversation memory.

## Working style

**1. 22:00, stuck on the same error for three hours**

First, I get up from my chair. After three hours on the same error, I know staring at the screen won't help, so I walk around and think about what's really going wrong underneath, not just the error message in front of me. Once my head is clearer, I use problem-solving and creative-thinking methods to look at the issue from a different angle and question the assumptions I've been making. Then I use AI as a sounding board, asking it for ideas and possible solutions, and I check each suggestion against my own understanding before I apply it. My goal is to come back to the task with a fresh, open mind, use every resource available to me, and keep working steadily until the problem is solved.

**2. Wednesday, teammate silent since Monday, presenting Friday**

With the presentation on Friday, I don't wait any longer. I take responsibility for preparing the full presentation myself, so we're ready no matter what. On the day, I still present it as a team effort and give my teammate credit, because embarrassing him in front of everyone wouldn't help anyone. Afterwards, I speak to him privately. I ask why he hasn't replied since Monday and listen to his reasons, since something serious may have happened. I give him honest feedback and remind him that this is a professional environment where we rely on each other. If his explanation doesn't hold up after a fair conversation, I report the situation to head office so it can be handled properly and doesn't happen again.

**3. Mentor says two days of work is the wrong approach**

It stings to hear that two days of work went in the wrong direction, but I stay calm and open, because my mentor is telling me this to help me grow. I listen carefully to everything they say, and I ask questions until I understand exactly what was wrong with my approach and what a better one looks like. I'd rather learn this now than repeat the mistake later. Then I put the feedback into practice straight away, rework the task properly, and carry the lesson into future projects. My aim is not just to fix what they pointed out but to go beyond it, so that next time they can see how much I've grown.

**4. Monday/Wednesday/Friday sessions, January to March 2027**

The main thing that could get in the way is my studies. Fortunately, I study online, so I don't need to be on campus and I can work from anywhere. My plan is to check my class timetable as soon as it's released and arrange my online classes and study hours around the Monday, Wednesday and Friday sessions. Because my lectures are online, I can often catch up on them at a different time, and I'm comfortable studying at night, so the sessions get my full attention during the day. If an assessment or deadline ever clashes with a session, I'll plan ahead, finish the work early, and let the team know in advance. Monday, Wednesday and Friday are days I can fully commit to.
