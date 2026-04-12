from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Node(Base):
    __tablename__ = "nodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    owner_user_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    node_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    host: Mapped[str | None] = mapped_column(String(255), nullable=True)
    machine_fingerprint_hash: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    node_group: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="offline", index=True)
    cpu_cores: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    ram_mb: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    gpu_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    gpu_info_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    os_info: Mapped[str | None] = mapped_column(String(100), nullable=True)
    arch: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
