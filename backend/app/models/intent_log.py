import uuid
from datetime import datetime

from sqlalchemy import JSON, BOOLEAN, TEXT, VARCHAR, DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class IntentLog(Base):
    """Every user input is stored here — the "store every detail" record.

    One raw input can produce several structured actions; `payload` holds the
    full parsed list. `intent_type` is the primary classification for filtering.
    """

    __tablename__ = "intent_logs"

    intent_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    household_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("households.household_id", ondelete="CASCADE", name="fk_intent_household_id"),
        nullable=False,
    )
    source: Mapped[str] = mapped_column(VARCHAR(10), nullable=False)  # voice / text / image
    raw_text: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    has_image: Mapped[bool] = mapped_column(BOOLEAN, nullable=False, default=False)
    # meal_preference / pantry_update / grocery_add / schedule_change /
    # goal_change / dietary_change / eat_out_note / unknown
    intent_type: Mapped[str | None] = mapped_column(VARCHAR(30), nullable=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (Index("ix_intent_logs_household_id", "household_id"),)
