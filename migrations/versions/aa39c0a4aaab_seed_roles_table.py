"""seed roles table

Revision ID: aa39c0a4aaab
Revises: 07e65a5209ca
Create Date: 2026-02-19 10:47:42.439259

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aa39c0a4aaab'
down_revision: Union[str, Sequence[str], None] = '07e65a5209ca'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    roles_table = sa.table(
        'roles',
        sa.column('id', sa.Integer),
        sa.column('name', sa.String)
    )
    op.bulk_insert(roles_table, [
        {'id': 1, 'name': 'admin'},
        {'id': 2, 'name': 'user'}
    ])


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DELETE FROM roles WHERE id IN (1, 2)")
