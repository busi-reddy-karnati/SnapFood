import uuid
from datetime import datetime

from sqlalchemy import JSON, BOOLEAN, VARCHAR, DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Suggestion(Base):
    """A generated suggestion (grocery list / cook-with-pantry / recipe).

    Doubles as the v0 "history" record. `ordered` / `order_ref` are the seam for
    real ordering (DoorDash) in a later phase.
    """

    __tablename__ = "suggestions"

    suggestion_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    household_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("households.household_id", ondelete="CASCADE", name="fk_suggestion_household_id"),
        nullable=False,
    )
    kind: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)  # grocery_list / cook_with_pantry / recipe
    # {"grocery": [...], "recipes": [...], "rationale": "...", "goal_alignment": "..."}
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    ordered: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=False)
    order_ref: Mapped[str | None] = mapped_column(VARCHAR(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (Index("ix_suggestions_household_id", "household_id"),)
