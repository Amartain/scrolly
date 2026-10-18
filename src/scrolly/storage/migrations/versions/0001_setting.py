"""setting table

Revision ID: 0001
Revises:
"""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None


def upgrade() -> None:
    op.create_table(
        "setting",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("realm_id", sa.String(36), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=True),
        sa.Column("key", sa.String(100), nullable=False),
        sa.Column("value_json", sa.Text, nullable=False),
        sa.Column("created_at", sa.String(40), nullable=False),
        sa.Column("updated_at", sa.String(40), nullable=False),
        sa.UniqueConstraint("realm_id", "key"),
    )


def downgrade() -> None:
    op.drop_table("setting")
