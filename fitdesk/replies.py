"""Fact lookup and reply drafting. Pure code, no AI: every price and slot in a
draft comes from the data file, so the reply cannot contain invented facts."""
import json
import re
from dataclasses import dataclass

from .models import EnquiryAnalysis

ESCALATION = "I'll check with the owner and come back to you."

_TIME_RE = re.compile(r"^\s*(\d{1,2})(?:[:h.](\d{2}))?\s*(am|pm)?\s*$", re.I)


@dataclass
class Draft:
    text: str
    needs_escalation: bool


def load_data(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def normalise_time(raw: str) -> str | None:
    m = _TIME_RE.match(raw or "")
    if not m:
        return None
    hour, minute, ampm = int(m.group(1)), int(m.group(2) or 0), (m.group(3) or "").lower()
    if ampm == "pm" and hour < 12:
        hour += 12
    if ampm == "am" and hour == 12:
        hour = 0
    if hour > 23 or minute > 59:
        return None
    return f"{hour:02d}:{minute:02d}"


def normalise_package(raw: str) -> str:
    s = (raw or "").strip().lower()
    if "single" in s:
        return "single"
    m = re.search(r"\d+", s)
    if m:
        return "single" if int(m.group(0)) == 1 else str(int(m.group(0)))
    return s


def draft_reply(analysis: EnquiryAnalysis, data: dict) -> Draft:
    packages = data["packages"]
    slots = data["saturday_slots"]
    asked_pkgs = analysis.details.packages
    asked_times = analysis.details.saturday_times

    wants_price = analysis.intent in ("package_price", "package_and_availability") or bool(asked_pkgs)
    wants_slots = analysis.intent in ("saturday_availability", "package_and_availability") or bool(asked_times)

    lines: list[str] = []
    missing = bool(analysis.details.other_topics) or analysis.intent == "other" and not (asked_pkgs or asked_times)

    if wants_price:
        keys = [normalise_package(p) for p in asked_pkgs] or list(packages)
        for key in dict.fromkeys(keys):  # de-duplicate, keep order
            if key in packages:
                p = packages[key]
                lines.append(f"- {p['label']}: R{p['price_zar']:,}")
            else:
                missing = True

    if wants_slots:
        times = [normalise_time(t) for t in asked_times]
        if not asked_times:
            times = list(slots)
        for t in dict.fromkeys(times):
            if t in slots:
                lines.append(f"- Saturday {t}: {slots[t]}")
            else:
                missing = True

    if not lines:
        return Draft(ESCALATION, True)

    text = "Hi! Here is what I can confirm from our current price list and availability:\n"
    text += "\n".join(lines)
    if missing:
        text += "\n" + ESCALATION
    return Draft(text, missing)
