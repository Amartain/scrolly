"""The sunset poem is shown once a day

Revision ID: 0008
Revises: 0007
"""

import sqlalchemy as sa
from alembic import op

revision = "0008"
down_revision = "0007"


def upgrade() -> None:
    op.add_column("day", sa.Column("poem_shown_at", sa.String(40), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("day") as batch:
        batch.drop_column("poem_shown_at")
