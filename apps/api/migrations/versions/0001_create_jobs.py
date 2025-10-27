"""create jobs table

Revision ID: 0001_create_jobs
Revises:
Create Date: 2025-10-26 00:00:00

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0001_create_jobs"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "jobs",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("owner_id", sa.String(), nullable=False),
        sa.Column("team_id", sa.String(), nullable=False),
        sa.Column("priority", sa.String(), nullable=False, server_default="normal"),
        sa.Column("spec", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("state", sa.String(), nullable=False, server_default="QUEUED"),
        sa.Column("queued_at", sa.DateTime(timezone=False), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=False), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=False), nullable=True),
        sa.Column("runner_id", sa.String(), nullable=True),
        sa.Column("exit_code", sa.Integer(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=False),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=False),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_jobs_state", "jobs", ["state"])
    op.create_index("ix_jobs_team_state", "jobs", ["team_id", "state"])
    op.create_index("ix_jobs_queued", "jobs", ["queued_at"])
    op.create_index("ix_jobs_started", "jobs", ["started_at"])


def downgrade() -> None:
    op.drop_index("ix_jobs_started", table_name="jobs")
    op.drop_index("ix_jobs_queued", table_name="jobs")
    op.drop_index("ix_jobs_team_state", table_name="jobs")
    op.drop_index("ix_jobs_state", table_name="jobs")
    op.drop_table("jobs")
