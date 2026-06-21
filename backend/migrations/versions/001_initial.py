"""Initial schema: create all SnapFood tables

Revision ID: 001
Revises:
Create Date: 2026-06-21 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "households",
        sa.Column("household_id", sa.String(36), primary_key=True),
        sa.Column("device_uuid", sa.String(36), nullable=False, unique=True),
        sa.Column("name", sa.VARCHAR(120), nullable=True),
        sa.Column("dietary_preferences", sa.JSON(), nullable=False),
        sa.Column("cuisines", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index("ix_households_device_uuid", "households", ["device_uuid"])

    op.create_table(
        "members",
        sa.Column("member_id", sa.String(36), primary_key=True),
        sa.Column(
            "household_id",
            sa.String(36),
            sa.ForeignKey("households.household_id", ondelete="CASCADE", name="fk_members_household_id"),
            nullable=False,
        ),
        sa.Column("name", sa.VARCHAR(120), nullable=False),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("dietary_preferences", sa.JSON(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
    )

    op.create_table(
        "goals",
        sa.Column("goal_id", sa.String(36), primary_key=True),
        sa.Column(
            "household_id",
            sa.String(36),
            sa.ForeignKey("households.household_id", ondelete="CASCADE", name="fk_goals_household_id"),
            nullable=False,
            unique=True,
        ),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("target", sa.JSON(), nullable=False),
    )

    op.create_table(
        "schedules",
        sa.Column("schedule_id", sa.String(36), primary_key=True),
        sa.Column(
            "household_id",
            sa.String(36),
            sa.ForeignKey("households.household_id", ondelete="CASCADE", name="fk_schedules_household_id"),
            nullable=False,
            unique=True,
        ),
        sa.Column("meals", sa.JSON(), nullable=False),
    )

    op.create_table(
        "pantry_items",
        sa.Column("item_id", sa.String(36), primary_key=True),
        sa.Column(
            "household_id",
            sa.String(36),
            sa.ForeignKey("households.household_id", ondelete="CASCADE", name="fk_pantry_household_id"),
            nullable=False,
        ),
        sa.Column("name", sa.VARCHAR(200), nullable=False),
        sa.Column("category", sa.VARCHAR(40), nullable=True),
        sa.Column("quantity", sa.Numeric(10, 2), nullable=True),
        sa.Column("unit", sa.VARCHAR(20), nullable=True),
        sa.Column("status", sa.VARCHAR(10), nullable=False, server_default="ok"),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_pantry_items_household_id", "pantry_items", ["household_id"])

    op.create_table(
        "grocery_items",
        sa.Column("item_id", sa.String(36), primary_key=True),
        sa.Column(
            "household_id",
            sa.String(36),
            sa.ForeignKey("households.household_id", ondelete="CASCADE", name="fk_grocery_household_id"),
            nullable=False,
        ),
        sa.Column("name", sa.VARCHAR(200), nullable=False),
        sa.Column("category", sa.VARCHAR(40), nullable=True),
        sa.Column("quantity", sa.Numeric(10, 2), nullable=True),
        sa.Column("unit", sa.VARCHAR(20), nullable=True),
        sa.Column("source", sa.VARCHAR(12), nullable=False, server_default="manual"),
        sa.Column("from_suggestion_id", sa.String(36), nullable=True),
        sa.Column("status", sa.VARCHAR(12), nullable=False, server_default="active"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_grocery_items_household_id", "grocery_items", ["household_id"])

    op.create_table(
        "food_items",
        sa.Column("food_id", sa.String(36), primary_key=True),
        sa.Column("name", sa.VARCHAR(200), nullable=False, unique=True),
        sa.Column("category", sa.VARCHAR(40), nullable=True),
        sa.Column("unit", sa.VARCHAR(20), nullable=True),
        sa.Column("nutrition", sa.JSON(), nullable=False),
    )

    op.create_table(
        "intent_logs",
        sa.Column("intent_id", sa.String(36), primary_key=True),
        sa.Column(
            "household_id",
            sa.String(36),
            sa.ForeignKey("households.household_id", ondelete="CASCADE", name="fk_intent_household_id"),
            nullable=False,
        ),
        sa.Column("source", sa.VARCHAR(10), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.Column("has_image", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("intent_type", sa.VARCHAR(30), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_intent_logs_household_id", "intent_logs", ["household_id"])

    op.create_table(
        "suggestions",
        sa.Column("suggestion_id", sa.String(36), primary_key=True),
        sa.Column(
            "household_id",
            sa.String(36),
            sa.ForeignKey("households.household_id", ondelete="CASCADE", name="fk_suggestion_household_id"),
            nullable=False,
        ),
        sa.Column("kind", sa.VARCHAR(20), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("ordered", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("order_ref", sa.VARCHAR(120), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_suggestions_household_id", "suggestions", ["household_id"])

    op.create_table(
        "feedback",
        sa.Column("feedback_id", sa.String(36), primary_key=True),
        sa.Column(
            "household_id",
            sa.String(36),
            sa.ForeignKey("households.household_id", ondelete="CASCADE", name="fk_feedback_household_id"),
            nullable=False,
        ),
        sa.Column(
            "suggestion_id",
            sa.String(36),
            sa.ForeignKey("suggestions.suggestion_id", ondelete="CASCADE", name="fk_feedback_suggestion_id"),
            nullable=False,
        ),
        sa.Column("rating", sa.VARCHAR(10), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_feedback_household_id", "feedback", ["household_id"])


def downgrade() -> None:
    op.drop_table("feedback")
    op.drop_table("suggestions")
    op.drop_table("intent_logs")
    op.drop_table("food_items")
    op.drop_table("grocery_items")
    op.drop_table("pantry_items")
    op.drop_table("schedules")
    op.drop_table("goals")
    op.drop_table("members")
    op.drop_index("ix_households_device_uuid", table_name="households")
    op.drop_table("households")
