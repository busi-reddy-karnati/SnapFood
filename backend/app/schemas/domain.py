"""Read-side schemas that map directly from ORM rows (from_attributes)."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MemberSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    member_id: str
    name: str
    age: int | None = None
    dietary_preferences: dict = {}
    notes: str | None = None


class GoalSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    goal_id: str
    description: str
    target: dict = {}


class ScheduleSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    schedule_id: str
    meals: list = []


class PantryItemSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    item_id: str
    name: str
    category: str | None = None
    quantity: float | None = None
    unit: str | None = None
    status: str
    updated_at: datetime | None = None


class GroceryItemSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    item_id: str
    name: str
    category: str | None = None
    quantity: float | None = None
    unit: str | None = None
    source: str
    status: str
    created_at: datetime | None = None


class SuggestionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    suggestion_id: str
    kind: str
    payload: dict = {}
    ordered: bool = False
    created_at: datetime | None = None
