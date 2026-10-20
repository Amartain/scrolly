"""Timer segments: one continuous run of one discipline on one trial

Revision ID: 0010
Revises: 0009
"""

import sqlalchemy as sa
from alembic import op

revision = "0010"
down_revision = "0009"


def upgrade() -> None:
    op.create_table(
        "timer_segment",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("realm_id", sa.String(36), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=True),
        sa.Column("created_at", sa.String(40), nullable=False),
        sa.Column("updated_at", sa.String(40), nullable=False),
        sa.Column("trial_id", sa.String(36), nullable=False),
        sa.Column("discipline", sa.String(20), nullable=False),
        sa.Column("started_at", sa.String(40), nullable=False),
        sa.Column("ended_at", sa.String(40), nullable=True),
    )
    op.create_index("ix_timer_segment_trial_id", "timer_segment", ["trial_id"])


def downgrade() -> None:
    op.drop_index("ix_timer_segment_trial_id", table_name="timer_segment")
    op.drop_table("timer_segment")
