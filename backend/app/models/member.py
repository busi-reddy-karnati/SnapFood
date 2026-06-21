import uuid

from sqlalchemy import JSON, INTEGER, TEXT, VARCHAR, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Member(Base):
    """A person in the household — each can carry their own dietary preferences."""

    __tablename__ = "members"

    member_id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    household_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("households.household_id", ondelete="CASCADE", name="fk_members_household_id"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(VARCHAR(120), nullable=False)
    age: Mapped[int | None] = mapped_column(INTEGER, nullable=True)
    dietary_preferences: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    notes: Mapped[str | None] = mapped_column(TEXT, nullable=True)

    household: Mapped["Household"] = relationship("Household", back_populates="members")  # noqa: F821
