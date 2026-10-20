"""Time spent planning, kept on the day

Revision ID: 0009
Revises: 0008
"""

import sqlalchemy as sa
from alembic import op

revision = "0009"
down_revision = "0008"


def upgrade() -> None:
    op.add_column("day", sa.Column("planning_started_at", sa.String(40), nullable=True))
    op.add_column(
        "day",
        sa.Column("planning_accumulated_s", sa.Integer, nullable=False, server_default="0"),
    )


def downgrade() -> None:
    with op.batch_alter_table("day") as batch:
        batch.drop_column("planning_accumulated_s")
        batch.drop_column("planning_started_at")
