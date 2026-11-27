"""Pydantic models for the structured JSON Gemini must return."""
from typing import Literal

from pydantic import BaseModel, Field


class Details(BaseModel):
    packages: list[str] = Field(
        description="Packages the customer asked about, as the session count "
        "(e.g. '12') or 'single'. Empty list if none or 'all packages'."
    )
    saturday_times: list[str] = Field(
        description="Saturday times the customer asked about, 24h HH:MM "
        "(e.g. '09:00'). Empty list if none or 'any slot'."
    )
    other_topics: list[str] = Field(
        description="Anything else the customer asked about that is NOT a "
        "package price or Saturday availability (e.g. 'discounts', 'bookings')."
    )


class EnquiryAnalysis(BaseModel):
    """The structured JSON the AI must return. Anything else is rejected."""

    intent: Literal[
        "package_price",
        "saturday_availability",
        "package_and_availability",
        "other",
    ]
    details: Details
    requires_human_approval: bool
