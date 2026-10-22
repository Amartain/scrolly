"""Tribulation Weathered is shown once per clearing of the scroll

Revision ID: 0012
Revises: 0011
"""

import sqlalchemy as sa
from alembic import op

revision = "0012"
down_revision = "0011"


def upgrade() -> None:
    op.add_column("day", sa.Column("victory_seen_at", sa.String(40), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("day") as batch:
        batch.drop_column("victory_seen_at")
