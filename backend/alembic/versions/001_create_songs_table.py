"""Create songs table

Revision ID: 001
Revises:
Create Date: 2025-01-02

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "songs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("artist", sa.String(255), nullable=True),
        sa.Column("lyrics", sa.Text(), nullable=True),
        sa.Column("chordpro", sa.Text(), nullable=True),
        sa.Column("original_key", sa.String(10), nullable=True),
        sa.Column("tempo", sa.Integer(), nullable=True),
        sa.Column("time_signature", sa.String(10), nullable=True),
        sa.Column("mood", sa.String(50), nullable=True),
        sa.Column("themes", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("ccli_number", sa.String(50), nullable=True),
        sa.Column("youtube_url", sa.String(500), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("language", sa.String(10), nullable=False, server_default="en"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_songs_title"), "songs", ["title"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_songs_title"), table_name="songs")
    op.drop_table("songs")
