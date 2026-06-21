from pydantic import BaseModel

from app.schemas.domain import (
    GoalSchema,
    GroceryItemSchema,
    MemberSchema,
    PantryItemSchema,
    ScheduleSchema,
    SuggestionSchema,
)


class HouseholdResponse(BaseModel):
    household_id: str
    name: str | None = None
    dietary_preferences: dict = {}
    cuisines: list = []
    goal: GoalSchema | None = None
    schedule: ScheduleSchema | None = None
    members: list[MemberSchema] = []


class IntakeResponse(BaseModel):
    intent_id: str
    intent_type: str | None = None
    # the structured actions the model produced
    intents: list[dict] = []
    # human-readable summary of what changed (pantry/grocery/etc.)
    applied: list[str] = []
    message: str


class FeedbackResponse(BaseModel):
    feedback_id: str
    suggestion_id: str
    rating: str


class HistoryResponse(BaseModel):
    suggestions: list[SuggestionSchema] = []


__all__ = [
    "HouseholdResponse",
    "IntakeResponse",
    "FeedbackResponse",
    "HistoryResponse",
    "PantryItemSchema",
    "GroceryItemSchema",
    "SuggestionSchema",
]
