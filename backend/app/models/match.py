import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    stadium_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("stadiums.id"))
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("players.id"), nullable=False)
    format: Mapped[str] = mapped_column(String(10), nullable=False)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_hours: Mapped[float] = mapped_column(Numeric(3, 1), nullable=False, default=1.5)
    field_cost: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    skill_min: Mapped[int] = mapped_column(Integer, default=0)
    skill_max: Mapped[int] = mapped_column(Integer, default=9999)
    status: Mapped[str] = mapped_column(String(20), default="open")
    # Status values: open | full | in_progress | completed | cancelled
    # WHY NOT AN ENUM TYPE: string columns are easier to add new values to
    # without a database migration. Use CHECK constraint for validation.
    # FUTURE: add CHECK constraint or PostgreSQL ENUM for stricter enforcement.
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    teams: Mapped[list["MatchTeam"]] = relationship(back_populates="match", cascade="all, delete-orphan")


class MatchTeam(Base):
    __tablename__ = "match_teams"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("matches.id"), nullable=False)
    label: Mapped[str] = mapped_column(String(1), nullable=False)
    treasurer_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("players.id"))

    match: Mapped["Match"] = relationship(back_populates="teams")
    position_slots: Mapped[list["MatchPositionSlot"]] = relationship(back_populates="team", cascade="all, delete-orphan")


class MatchPositionSlot(Base):
    __tablename__ = "match_position_slots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_team_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("match_teams.id"), nullable=False)
    position: Mapped[str] = mapped_column(String(3), nullable=False)
    filled_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("players.id"))
    # filled_by = None means the slot is open.
    # This is the core of position conflict prevention — a player can only
    # join a slot that exists and is unfilled (filled_by IS NULL).

    team: Mapped["MatchTeam"] = relationship(back_populates="position_slots")
