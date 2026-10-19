"""Time worked travels with a trial to the Horizon and back

Revision ID: 0007
Revises: 0006
"""

import sqlalchemy as sa
from alembic import op

revision = "0007"
down_revision = "0006"


def upgrade() -> None:
    op.add_column(
        "horizon_item", sa.Column("worked_s", sa.Integer, nullable=False, server_default="0")
    )


def downgrade() -> None:
    with op.batch_alter_table("horizon_item") as batch:
        batch.drop_column("worked_s")
