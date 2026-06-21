import uuid
from datetime import datetime

from sqlalchemy import JSON, VARCHAR, DateTime, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Household(Base):
    """One household per device in v0 (get-or-created by device_uuid)."""

    __tablename__ = "households"

    household_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    device_uuid: Mapped[str] = mapped_column(String(36), nullable=False, unique=True)
    name: Mapped[str | None] = mapped_column(VARCHAR(120), nullable=True)
    # {"diet": "vegetarian", "allergies": [...], "dislikes": [...]}
    dietary_preferences: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    cuisines: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    members: Mapped[list["Member"]] = relationship(  # noqa: F821
        "Member", back_populates="household", cascade="all, delete-orphan"
    )
    goal: Mapped["Goal | None"] = relationship(  # noqa: F821
        "Goal", back_populates="household", uselist=False, cascade="all, delete-orphan"
    )
    schedule: Mapped["Schedule | None"] = relationship(  # noqa: F821
        "Schedule", back_populates="household", uselist=False, cascade="all, delete-orphan"
    )

    __table_args__ = (Index("ix_households_device_uuid", "device_uuid"),)
