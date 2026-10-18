"""Golden Core: Qi columns on trials, templates, days and the planning draft

Revision ID: 0004
Revises: 0003
"""

import sqlalchemy as sa
from alembic import op

revision = "0004"
down_revision = "0003"

_COLUMNS = {
    "trial": "qi_expected",
    "horizon_item": "qi_expected",
    "art": "qi_expected",
    "day": "qi_start",
    "planning_draft": "qi_start",
}


def upgrade() -> None:
    for table, column in _COLUMNS.items():
        op.add_column(table, sa.Column(column, sa.Integer, nullable=True))


def downgrade() -> None:
    for table, column in _COLUMNS.items():
        with op.batch_alter_table(table) as batch:
            batch.drop_column(column)
