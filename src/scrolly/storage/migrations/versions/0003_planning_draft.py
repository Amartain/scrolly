"""planning_draft table

Revision ID: 0003
Revises: 0002
"""

import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0002"


def upgrade() -> None:
    op.create_table(
        "planning_draft",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("realm_id", sa.String(36), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=True),
        sa.Column("created_at", sa.String(40), nullable=False),
        sa.Column("updated_at", sa.String(40), nullable=False),
        sa.Column("logical_day", sa.String(10), nullable=False),
        sa.Column("phase", sa.String(20), nullable=False),
        sa.Column("text", sa.Text, nullable=False),
        sa.UniqueConstraint("realm_id"),
    )


def downgrade() -> None:
    op.drop_table("planning_draft")
