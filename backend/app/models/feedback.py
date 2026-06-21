import uuid
from datetime import datetime

from sqlalchemy import TEXT, VARCHAR, DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Feedback(Base):
    """User feedback on a suggestion — fed back into future suggestion prompts."""

    __tablename__ = "feedback"

    feedback_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    household_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("households.household_id", ondelete="CASCADE", name="fk_feedback_household_id"),
        nullable=False,
    )
    suggestion_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("suggestions.suggestion_id", ondelete="CASCADE", name="fk_feedback_suggestion_id"),
        nullable=False,
    )
    rating: Mapped[str] = mapped_column(VARCHAR(10), nullable=False)  # up / down (or "1".."5")
    comment: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (Index("ix_feedback_household_id", "household_id"),)
