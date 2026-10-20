"""Strict HTTP contracts for the local prototype."""

from pydantic import BaseModel, ConfigDict, StrictStr, field_validator


class RecommendationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: StrictStr

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        if not 1 <= len(value) <= 500 or not value.strip():
            raise ValueError("text must contain 1 to 500 characters")
        return value
