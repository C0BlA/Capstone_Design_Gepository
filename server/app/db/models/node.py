from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Node(Base):
    __tablename__ = "nodes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    owner_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    node_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    host: Mapped[str | None] = mapped_column(String(255), nullable=True)

    machine_fingerprint_hash: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    node_group: Mapped[str | None] = mapped_column(String(100), nullable=True)

    status: Mapped[str] = mapped_column(
        String(20),
        default="offline",
        nullable=False,
        index=True,
    )

    cpu_cores: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ram_mb: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    gpu_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    gpu_info_json: Mapped[list | None] = mapped_column(JSON, nullable=True)

    os_info: Mapped[str | None] = mapped_column(String(100), nullable=True)
    arch: Mapped[str | None] = mapped_column(String(50), nullable=True)

    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    owner: Mapped["User | None"] = relationship(
        "User",
        back_populates="nodes",
    )