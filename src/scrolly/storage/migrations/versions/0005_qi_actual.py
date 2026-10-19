"""The Qi a trial really cost, recorded when it is conquered

Revision ID: 0005
Revises: 0004
"""

import sqlalchemy as sa
from alembic import op

revision = "0005"
down_revision = "0004"


def upgrade() -> None:
    op.add_column("trial", sa.Column("qi_actual", sa.Integer, nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("trial") as batch:
        batch.drop_column("qi_actual")
