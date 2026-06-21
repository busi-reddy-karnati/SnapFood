import uuid

from sqlalchemy import JSON, VARCHAR, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class FoodItem(Base):
    """Catalog/cache of nutrition estimates so we don't re-ask the LLM each time."""

    __tablename__ = "food_items"

    food_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(VARCHAR(200), nullable=False, unique=True)
    category: Mapped[str | None] = mapped_column(VARCHAR(40), nullable=True)
    unit: Mapped[str | None] = mapped_column(VARCHAR(20), nullable=True)
    # {"calories": 130, "protein_g": 2.7, "fiber_g": 0.4, ...} per `unit`
    nutrition: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
