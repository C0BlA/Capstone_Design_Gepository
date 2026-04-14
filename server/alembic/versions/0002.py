"""add users tokens and node owner

Revision ID: 0002
Revises: 0001_create_nodes_tasks
Create Date: 2026-04-14
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "0002"
down_revision = "0001_create_nodes_tasks"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)

    table_names = inspector.get_table_names()

    if "users" not in table_names:
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("username", sa.String(length=50), nullable=False),
            sa.Column("email", sa.String(length=255), nullable=False),
            sa.Column("password_hash", sa.String(length=255), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_users_id", "users", ["id"], unique=False)
        op.create_index("ix_users_username", "users", ["username"], unique=True)
        op.create_index("ix_users_email", "users", ["email"], unique=True)

    if "api_tokens" not in table_names:
        op.create_table(
            "api_tokens",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("token_name", sa.String(length=100), nullable=False),
            sa.Column("token_hash", sa.String(length=255), nullable=False),
            sa.Column("is_revoked", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("expires_at", sa.DateTime(), nullable=True),
            sa.Column("last_used_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        )
        op.create_index("ix_api_tokens_id", "api_tokens", ["id"], unique=False)
        op.create_index("ix_api_tokens_user_id", "api_tokens", ["user_id"], unique=False)
        op.create_index("ix_api_tokens_token_hash", "api_tokens", ["token_hash"], unique=True)

    node_columns = [col["name"] for col in inspector.get_columns("nodes")]
    node_indexes = [idx["name"] for idx in inspector.get_indexes("nodes")]

    if "owner_user_id" not in node_columns:
        op.add_column("nodes", sa.Column("owner_user_id", sa.Integer(), nullable=True))

    if "ix_nodes_owner_user_id" not in node_indexes:
        op.create_index("ix_nodes_owner_user_id", "nodes", ["owner_user_id"], unique=False)

    fk_names = [
        fk["name"]
        for fk in inspector.get_foreign_keys("nodes")
        if fk["name"] is not None
    ]

    if "fk_nodes_owner_user_id_users" not in fk_names:
        op.create_foreign_key(
            "fk_nodes_owner_user_id_users",
            "nodes",
            "users",
            ["owner_user_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)

    fk_names = [
        fk["name"]
        for fk in inspector.get_foreign_keys("nodes")
        if fk["name"] is not None
    ]
    node_indexes = [idx["name"] for idx in inspector.get_indexes("nodes")]
    node_columns = [col["name"] for col in inspector.get_columns("nodes")]
    table_names = inspector.get_table_names()

    if "fk_nodes_owner_user_id_users" in fk_names:
        op.drop_constraint("fk_nodes_owner_user_id_users", "nodes", type_="foreignkey")

    if "ix_nodes_owner_user_id" in node_indexes:
        op.drop_index("ix_nodes_owner_user_id", table_name="nodes")

    if "owner_user_id" in node_columns:
        op.drop_column("nodes", "owner_user_id")

    if "api_tokens" in table_names:
        op.drop_index("ix_api_tokens_token_hash", table_name="api_tokens")
        op.drop_index("ix_api_tokens_user_id", table_name="api_tokens")
        op.drop_index("ix_api_tokens_id", table_name="api_tokens")
        op.drop_table("api_tokens")

    if "users" in table_names:
        op.drop_index("ix_users_email", table_name="users")
        op.drop_index("ix_users_username", table_name="users")
        op.drop_index("ix_users_id", table_name="users")
        op.drop_table("users")