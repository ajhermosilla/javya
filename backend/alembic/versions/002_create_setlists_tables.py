"""Create setlists and setlist_songs tables

Revision ID: 002
Revises: 001
Create Date: 2026-01-03

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create setlists table
    op.create_table(
        "setlists",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("service_date", sa.Date(), nullable=True),
        sa.Column("event_type", sa.String(50), nullable=True),
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
    op.create_index(op.f("ix_setlists_name"), "setlists", ["name"], unique=False)
    op.create_index(
        op.f("ix_setlists_service_date"), "setlists", ["service_date"], unique=False
    )

    # Create setlist_songs join table
    op.create_table(
        "setlist_songs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("setlist_id", sa.UUID(), nullable=False),
        sa.Column("song_id", sa.UUID(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["setlist_id"], ["setlists.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["song_id"], ["songs.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_setlist_songs_setlist_id"),
        "setlist_songs",
        ["setlist_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_setlist_songs_position"),
        "setlist_songs",
        ["setlist_id", "position"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_setlist_songs_position"), table_name="setlist_songs")
    op.drop_index(op.f("ix_setlist_songs_setlist_id"), table_name="setlist_songs")
    op.drop_table("setlist_songs")
    op.drop_index(op.f("ix_setlists_service_date"), table_name="setlists")
    op.drop_index(op.f("ix_setlists_name"), table_name="setlists")
    op.drop_table("setlists")
