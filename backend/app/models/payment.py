import uuid
from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, Numeric, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TeamPayment(Base):
    __tablename__ = "team_payments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_team_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("match_teams.id"), nullable=False)
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    paid_to_stadium: Mapped[bool] = mapped_column(Boolean, default=False)
    paid_at: Mapped[datetime | None] = mapped_column()
    confirmed_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("players.id"))

    shares: Mapped[list["PlayerPaymentShare"]] = relationship(back_populates="team_payment", cascade="all, delete-orphan")


class PlayerPaymentShare(Base):
    __tablename__ = "player_payment_shares"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    team_payment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("team_payments.id"), nullable=False)
    player_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("players.id"), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    confirmed_at: Mapped[datetime | None] = mapped_column()
    confirmed_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("players.id"))

    team_payment: Mapped["TeamPayment"] = relationship(back_populates="shares")

    __table_args__ = (
        UniqueConstraint("team_payment_id", "player_id", name="uq_share_per_player"),
        # WHY UNIQUE CONSTRAINT AT DB LEVEL NOT JUST APP LEVEL:
        # Application-level duplicate checks have a race condition — two requests
        # arriving simultaneously both pass the check and both insert.
        # A DB unique constraint is atomic — only one succeeds, the other gets
        # a clear IntegrityError. Always enforce uniqueness at the DB layer.
    )
