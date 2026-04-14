"""create nodes and tasks

Revision ID: 0001_create_nodes_tasks
Revises: 
Create Date: 2026-04-11 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_create_nodes_tasks"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "nodes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_user_id", sa.Integer(), nullable=True),
        sa.Column("node_name", sa.String(length=100), nullable=False),
        sa.Column("host", sa.String(length=255), nullable=True),
        sa.Column("machine_fingerprint_hash", sa.String(length=128), nullable=False),
        sa.Column("node_group", sa.String(length=50), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="offline"),
        sa.Column("cpu_cores", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("ram_mb", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("gpu_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("gpu_info_json", sa.Text(), nullable=True),
        sa.Column("os_info", sa.String(length=100), nullable=True),
        sa.Column("arch", sa.String(length=50), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("last_seen_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_nodes_id", "nodes", ["id"])
    op.create_index("ix_nodes_owner_user_id", "nodes", ["owner_user_id"])
    op.create_index("ix_nodes_node_name", "nodes", ["node_name"])
    op.create_index("ix_nodes_machine_fingerprint_hash", "nodes", ["machine_fingerprint_hash"], unique=True)
    op.create_index("ix_nodes_node_group", "nodes", ["node_group"])
    op.create_index("ix_nodes_status", "nodes", ["status"])

    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("requester_user_id", sa.Integer(), nullable=True),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("assignment_mode", sa.Text(), nullable=False),
        sa.Column("selected_node_id", sa.Integer(), sa.ForeignKey("nodes.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_tasks_id", "tasks", ["id"])
    op.create_index("ix_tasks_requester_user_id", "tasks", ["requester_user_id"])
    op.create_index("ix_tasks_selected_node_id", "tasks", ["selected_node_id"])

    op.create_table(
        "task_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("task_id", sa.Integer(), sa.ForeignKey("tasks.id"), nullable=False),
        sa.Column("level", sa.Text(), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_task_logs_id", "task_logs", ["id"])
    op.create_index("ix_task_logs_task_id", "task_logs", ["task_id"])


def downgrade() -> None:
    op.drop_index("ix_task_logs_task_id", table_name="task_logs")
    op.drop_index("ix_task_logs_id", table_name="task_logs")
    op.drop_table("task_logs")

    op.drop_index("ix_tasks_selected_node_id", table_name="tasks")
    op.drop_index("ix_tasks_requester_user_id", table_name="tasks")
    op.drop_index("ix_tasks_id", table_name="tasks")
    op.drop_table("tasks")

    op.drop_index("ix_nodes_status", table_name="nodes")
    op.drop_index("ix_nodes_node_group", table_name="nodes")
    op.drop_index("ix_nodes_machine_fingerprint_hash", table_name="nodes")
    op.drop_index("ix_nodes_node_name", table_name="nodes")
    op.drop_index("ix_nodes_owner_user_id", table_name="nodes")
    op.drop_index("ix_nodes_id", table_name="nodes")
    op.drop_table("nodes")
