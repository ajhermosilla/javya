"""add index to setlist_songs setlist_id

Revision ID: 01638c370eb0
Revises: 005
Create Date: 2026-01-09 15:57:12.803759

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '01638c370eb0'
down_revision: Union[str, None] = '005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Index may already exist from previous schema setup
    op.create_index(
        'ix_setlist_songs_setlist_id',
        'setlist_songs',
        ['setlist_id'],
        unique=False,
        if_not_exists=True
    )


def downgrade() -> None:
    op.drop_index('ix_setlist_songs_setlist_id', table_name='setlist_songs', if_exists=True)
