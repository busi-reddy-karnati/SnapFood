from pydantic import BaseModel, Field

from app.config import settings


# --- Household / members / goal / schedule ----------------------------- #
class HouseholdUpdateRequest(BaseModel):
    name: str | None = Field(default=None, max_length=120)
    dietary_preferences: dict | None = None
    cuisines: list | None = None


class MemberCreateRequest(BaseModel):
    name: str = Field(max_length=120)
    age: int | None = Field(default=None, ge=0, le=130)
    dietary_preferences: dict = {}
    notes: str | None = Field(default=None, max_length=1000)


class MemberUpdateRequest(BaseModel):
    name: str | None = Field(default=None, max_length=120)
    age: int | None = Field(default=None, ge=0, le=130)
    dietary_preferences: dict | None = None
    notes: str | None = Field(default=None, max_length=1000)


class GoalUpdateRequest(BaseModel):
    description: str = Field(max_length=500)
    target: dict = {}


class ScheduleUpdateRequest(BaseModel):
    meals: list = []


# --- Pantry ------------------------------------------------------------ #
class PantryItemCreateRequest(BaseModel):
    name: str = Field(max_length=200)
    category: str | None = Field(default=None, max_length=40)
    quantity: float | None = Field(default=None, ge=0)
    unit: str | None = Field(default=None, max_length=20)
    status: str = Field(default="ok", pattern="^(ok|low|out)$")


class PantryItemUpdateRequest(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    category: str | None = Field(default=None, max_length=40)
    quantity: float | None = Field(default=None, ge=0)
    unit: str | None = Field(default=None, max_length=20)
    status: str | None = Field(default=None, pattern="^(ok|low|out)$")


# --- Grocery ----------------------------------------------------------- #
class GroceryItemCreateRequest(BaseModel):
    name: str = Field(max_length=200)
    category: str | None = Field(default=None, max_length=40)
    quantity: float | None = Field(default=None, ge=0)
    unit: str | None = Field(default=None, max_length=20)


class GroceryItemUpdateRequest(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    category: str | None = Field(default=None, max_length=40)
    quantity: float | None = Field(default=None, ge=0)
    unit: str | None = Field(default=None, max_length=20)
    status: str | None = Field(default=None, pattern="^(active|removed|purchased)$")


# --- Intake (multimodal) ----------------------------------------------- #
class IntakeRequest(BaseModel):
    """Text and/or a base64 image. At least one must be provided."""

    text: str | None = Field(default=None, max_length=settings.MAX_INTAKE_CHARS)
    image_base64: str | None = None
    image_mime: str | None = Field(default=None, max_length=60)


# --- Suggestions / feedback -------------------------------------------- #
class SuggestionGenerateRequest(BaseModel):
    # which kinds to generate; default both
    kinds: list[str] = ["grocery_list", "cook_with_pantry"]


class FeedbackRequest(BaseModel):
    suggestion_id: str = Field(max_length=36)
    rating: str = Field(pattern="^(up|down|[1-5])$")
    comment: str | None = Field(default=None, max_length=1000)
