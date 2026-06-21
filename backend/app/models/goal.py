import uuid

from sqlalchemy import JSON, TEXT, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Goal(Base):
    """The household's single active nutrition goal (one per household in v0)."""

    __tablename__ = "goals"

    goal_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    household_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("households.household_id", ondelete="CASCADE", name="fk_goals_household_id"),
        nullable=False,
        unique=True,
    )
    description: Mapped[str] = mapped_column(TEXT, nullable=False)
    # optional macro targets, e.g. {"protein_g": 120, "fiber_g": 30}
    target: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    household: Mapped["Household"] = relationship("Household", back_populates="goal")  # noqa: F821
