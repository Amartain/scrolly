"""Bamboo Scraps: the loose thoughts jotted during one visit to Seclusion

Revision ID: 0011
Revises: 0010
"""

import sqlalchemy as sa
from alembic import op

revision = "0011"
down_revision = "0010"


def upgrade() -> None:
    op.create_table(
        "bamboo_scrap",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("realm_id", sa.String(36), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=True),
        sa.Column("created_at", sa.String(40), nullable=False),
        sa.Column("updated_at", sa.String(40), nullable=False),
        sa.Column("opened_at", sa.String(40), nullable=False),
        sa.Column("saved_at", sa.String(40), nullable=False),
        sa.Column("closed_at", sa.String(40), nullable=True),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("trial_ids", sa.Text, nullable=False),
    )
    op.create_index("ix_bamboo_scrap_opened_at", "bamboo_scrap", ["opened_at"])


def downgrade() -> None:
    op.drop_index("ix_bamboo_scrap_opened_at", table_name="bamboo_scrap")
    op.drop_table("bamboo_scrap")
