import uuid

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Schedule(Base):
    """The household's eating schedule (one row per household)."""

    __tablename__ = "schedules"

    schedule_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    household_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("households.household_id", ondelete="CASCADE", name="fk_schedules_household_id"),
        nullable=False,
        unique=True,
    )
    # list of meal slots, e.g.
    # [{"label": "Breakfast", "time_of_day": "08:00", "days_of_week": ["Mon", ...]}]
    meals: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    household: Mapped["Household"] = relationship("Household", back_populates="schedule")  # noqa: F821
