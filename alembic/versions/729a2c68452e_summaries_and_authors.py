"""summaries and authors

Revision ID: 729a2c68452e
Revises: 2077e20427f3
Create Date: 2024-10-06 08:28:56.237683

"""

import uuid
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


from sqlalchemy.dialects.postgresql import UUID

from web_tools.config import get_settings

# revision identifiers, used by Alembic.
revision: str = "729a2c68452e"
down_revision: Union[str, None] = "2077e20427f3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

settings = get_settings()


def upgrade() -> None:
    # ### Create Author table ###
    op.create_table(
        "authors",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            default=uuid.uuid4,
            nullable=False,
        ),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column(
            "created_at", sa.DateTime, server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
        schema=settings.database.schema,
    )

    ### Create Summaries table ###
    op.create_table(
        "summaries",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            default=uuid.uuid4,
            nullable=False,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("short_description", sa.String(500), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, default="draft"),
        sa.Column("is_deleted", sa.Boolean, nullable=False, default=False),
        sa.Column(
            "user_id",
            sa.String(255),
            sa.ForeignKey(f"{settings.database.schema}.User.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at", sa.DateTime, server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
        schema=settings.database.schema,
    )

    # ### Create summary_authors association table ###
    op.create_table(
        "summary_authors",
        sa.Column(
            "summary_id",
            UUID(as_uuid=True),
            sa.ForeignKey(
                f"{settings.database.schema}.summaries.id", ondelete="CASCADE"
            ),
            primary_key=True,
        ),
        sa.Column(
            "author_id",
            UUID(as_uuid=True),
            sa.ForeignKey(f"{settings.database.schema}.authors.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        schema=settings.database.schema,
    )

    op.create_table(
        "sources",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            primary_key=True,
            default=uuid.uuid4,
            nullable=False,
        ),
        sa.Column("url", sa.String(length=2083), nullable=True),
        sa.Column(
            "summary_id",
            UUID(as_uuid=True),
            sa.ForeignKey(
                f"{settings.database.schema}.summaries.id", ondelete="CASCADE"
            ),
            nullable=False,
        ),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
        schema=settings.database.schema,
    )

    # # ### Create Indexes ###
    op.create_index(
        "ix_sources_summary_id",
        "sources",
        ["summary_id"],
        unique=False,
        schema=settings.database.schema,
    )

    # # ### Create Indexes ###
    op.create_index(
        "ix_summaries_title",
        "summaries",
        ["title"],
        unique=False,
        schema=settings.database.schema,
    )
    op.create_index(
        "ix_authors_name",
        "authors",
        ["name"],
        unique=True,
        schema=settings.database.schema,
    )
    op.create_index(
        "ix_summary_authors_author_id",
        "summary_authors",
        ["author_id"],
        unique=False,
        schema=settings.database.schema,
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index(
        "ix_summary_authors_author_id",
        table_name="summary_authors",
        schema=settings.database.schema,
    )
    op.drop_index(
        "ix_authors_name", table_name="authors", schema=settings.database.schema
    )
    op.drop_index(
        "ix_summaries_title", table_name="summaries", schema=settings.database.schema
    )

    # # Drop tables
    op.drop_table("summary_authors", schema=settings.database.schema)
    op.drop_table("summaries", schema=settings.database.schema)
    op.drop_table("authors", schema=settings.database.schema)
    op.drop_table("faq_section", schema=settings.database.schema)
    op.drop_table("User", schema=settings.database.schema)

    op.drop_index(
        "ix_sources_summary_id", table_name="sources", schema=settings.database.schema
    )

    # # Drop Sources table
    op.drop_table("sources", schema=settings.database.schema)
