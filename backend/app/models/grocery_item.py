import uuid
from datetime import datetime

from sqlalchemy import NUMERIC, VARCHAR, DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class GroceryItem(Base):
    """The editable grocery list. Users add/remove; suggestions can populate it."""

    __tablename__ = "grocery_items"

    item_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    household_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("households.household_id", ondelete="CASCADE", name="fk_grocery_household_id"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(VARCHAR(200), nullable=False)
    category: Mapped[str | None] = mapped_column(VARCHAR(40), nullable=True)
    quantity: Mapped[float | None] = mapped_column(NUMERIC(10, 2), nullable=True)
    unit: Mapped[str | None] = mapped_column(VARCHAR(20), nullable=True)
    source: Mapped[str] = mapped_column(VARCHAR(12), nullable=False, default="manual")  # manual / suggested
    from_suggestion_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    status: Mapped[str] = mapped_column(VARCHAR(12), nullable=False, default="active")  # active / removed / purchased
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (Index("ix_grocery_items_household_id", "household_id"),)
