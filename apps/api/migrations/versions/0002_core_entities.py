"""core entities

Revision ID: 0002_core_entities
Revises: 0001_create_jobs
Create Date: 2025-10-26 00:30:00

"""

import sqlalchemy as sa
from alembic import op

revision = "0002_core_entities"
down_revision = "0001_create_jobs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "teams",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False, unique=True),
        sa.Column("tier", sa.String(), nullable=False, server_default="standard"),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("email", sa.String(), nullable=False, unique=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("team_id", sa.String(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
    )

    op.create_table(
        "runners",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("host", sa.String(), nullable=False),
        sa.Column("arch", sa.String(), nullable=False),
        sa.Column("gpu_class", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="idle"),
        sa.Column("last_seen", sa.DateTime(), nullable=True),
        sa.Column("team_id", sa.String(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_runners_status", "runners", ["status"])
    op.create_index("ix_runners_last_seen", "runners", ["last_seen"])

    op.create_table(
        "runner_metrics",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column(
            "runner_id", sa.String(), sa.ForeignKey("runners.id"), nullable=False
        ),
        sa.Column("cpu_usage", sa.Float(), nullable=False),
        sa.Column("gpu_usage", sa.Float(), nullable=False),
        sa.Column("mem_gb", sa.Float(), nullable=False),
        sa.Column("thermal_state", sa.String(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(), nullable=False),
    )
    op.create_index(
        "ix_runner_metrics_runner_time", "runner_metrics", ["runner_id", "recorded_at"]
    )


def downgrade() -> None:
    op.drop_index("ix_runner_metrics_runner_time", table_name="runner_metrics")
    op.drop_table("runner_metrics")
    op.drop_index("ix_runners_last_seen", table_name="runners")
    op.drop_index("ix_runners_status", table_name="runners")
    op.drop_table("runners")
    op.drop_table("users")
    op.drop_table("teams")
