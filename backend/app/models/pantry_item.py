import uuid
from datetime import datetime

from sqlalchemy import NUMERIC, VARCHAR, DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PantryItem(Base):
    """What the household currently has on hand. `status` captures "almost over"."""

    __tablename__ = "pantry_items"

    item_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    household_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("households.household_id", ondelete="CASCADE", name="fk_pantry_household_id"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(VARCHAR(200), nullable=False)
    # produce / grain / pulse / oil / dairy / meat / spice / other
    category: Mapped[str | None] = mapped_column(VARCHAR(40), nullable=True)
    quantity: Mapped[float | None] = mapped_column(NUMERIC(10, 2), nullable=True)
    unit: Mapped[str | None] = mapped_column(VARCHAR(20), nullable=True)
    status: Mapped[str] = mapped_column(VARCHAR(10), nullable=False, default="ok")  # ok / low / out
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    __table_args__ = (Index("ix_pantry_items_household_id", "household_id"),)
