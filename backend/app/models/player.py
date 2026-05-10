import uuid
from datetime import datetime

from sqlalchemy import ARRAY, DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Player(Base):
    __tablename__ = "players"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String)
    line_id: Mapped[str | None] = mapped_column(String(100), unique=True)
    preferred_positions: Mapped[list[str] | None] = mapped_column(ARRAY(String(3)))
    # ARRAY(String) is a native PostgreSQL array — no join table needed for
    # a simple list of strings. Use a join table only if positions become
    # their own entity with extra attributes.
    elo_rating: Mapped[int] = mapped_column(Integer, nullable=False, default=1000)
    games_played: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
