"""Instances of an Art: a trial or Horizon item whose title names an Art

Revision ID: 0006
Revises: 0005
"""

import sqlalchemy as sa
from alembic import op

revision = "0006"
down_revision = "0005"

_KINDS = {"foundational_art": "foundational", "restorative_art": "restorative"}


def upgrade() -> None:
    for table in ("trial", "horizon_item"):
        op.add_column(table, sa.Column("art_kind", sa.String(20), nullable=True))
        # What came from an Art list already is an instance of that Art.
        for origin, kind in _KINDS.items():
            op.execute(
                sa.text(
                    f"UPDATE {table} SET art_kind = :kind WHERE origin_type = :origin"
                ).bindparams(kind=kind, origin=origin)
            )


def downgrade() -> None:
    for table in ("trial", "horizon_item"):
        with op.batch_alter_table(table) as batch:
            batch.drop_column("art_kind")
