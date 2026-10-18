"""trial, horizon_item, art and day tables

Revision ID: 0002
Revises: 0001
"""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"


def _audit() -> list[sa.Column]:  # type: ignore[type-arg]
    return [
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("realm_id", sa.String(36), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=True),
        sa.Column("created_at", sa.String(40), nullable=False),
        sa.Column("updated_at", sa.String(40), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "trial",
        *_audit(),
        sa.Column("logical_day", sa.String(10), nullable=False),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("state", sa.String(20), nullable=False),
        sa.Column("is_mandate", sa.Boolean, nullable=False),
        sa.Column("origin_type", sa.String(20), nullable=False),
        sa.Column("origin_id", sa.String(36), nullable=True),
        sa.Column("position", sa.Integer, nullable=False),
        sa.Column("essence_expected_min", sa.Integer, nullable=True),
        sa.Column("essence_actual_min", sa.Integer, nullable=True),
        sa.Column("completed_at", sa.String(40), nullable=True),
        sa.Column("note", sa.Text, nullable=False),
        sa.Column("timer_started_at", sa.String(40), nullable=True),
        sa.Column("timer_paused_at", sa.String(40), nullable=True),
        sa.Column("timer_accumulated_s", sa.Integer, nullable=False),
    )
    op.create_index("ix_trial_logical_day", "trial", ["logical_day"])
    op.create_index("ix_trial_state", "trial", ["state"])
    op.create_table(
        "horizon_item",
        *_audit(),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("is_mandate", sa.Boolean, nullable=False),
        sa.Column("essence_expected_min", sa.Integer, nullable=True),
        sa.Column("note", sa.Text, nullable=False),
        sa.Column("position", sa.Integer, nullable=False),
        sa.Column("origin_type", sa.String(20), nullable=False),
        sa.Column("origin_id", sa.String(36), nullable=True),
    )
    op.create_table(
        "art",
        *_audit(),
        sa.Column("kind", sa.String(20), nullable=False),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("essence_expected_min", sa.Integer, nullable=True),
        sa.Column("note", sa.Text, nullable=False),
        sa.Column("position", sa.Integer, nullable=False),
    )
    op.create_table(
        "day",
        *_audit(),
        sa.Column("logical_day", sa.String(10), nullable=False),
        sa.Column("first_sealed_at", sa.String(40), nullable=True),
        sa.Column("rolled_over_at", sa.String(40), nullable=True),
        sa.Column("dusk_override", sa.String(20), nullable=True),
        sa.Column("advisor_silenced", sa.Boolean, nullable=False),
        sa.UniqueConstraint("realm_id", "logical_day"),
    )


def downgrade() -> None:
    op.drop_table("day")
    op.drop_table("art")
    op.drop_table("horizon_item")
    op.drop_index("ix_trial_state", "trial")
    op.drop_index("ix_trial_logical_day", "trial")
    op.drop_table("trial")
