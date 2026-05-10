import uuid
from datetime import datetime, time

from geoalchemy2 import Geography
from sqlalchemy import ARRAY, Boolean, ForeignKey, Integer, Numeric, String, Time, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Stadium(Base):
    __tablename__ = "stadiums"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("players.id"))
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    address: Mapped[str | None] = mapped_column(String)
    location = mapped_column(
        Geography(geometry_type="POINT", srid=4326),
        nullable=False
    )
    # WHY GEOGRAPHY NOT GEOMETRY:
    # Geography uses lat/lon on a sphere (WGS84 — same as GPS).
    # ST_DWithin on geography measures real-world meters.
    # Geometry uses a flat plane — distances are in projection units,
    # inaccurate for large areas. Always use Geography for "find nearby X" queries.
    # SRID 4326 = the standard GPS coordinate system.
    surface_type: Mapped[str | None] = mapped_column(String(20))
    formats: Mapped[list[str] | None] = mapped_column(ARRAY(String(10)))
    price_per_hour: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class StadiumTimeSlot(Base):
    __tablename__ = "stadium_time_slots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    stadium_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("stadiums.id"), nullable=False)
    day_of_week: Mapped[int] = mapped_column(Integer)
    open_time: Mapped[time] = mapped_column(Time, nullable=False)
    close_time: Mapped[time] = mapped_column(Time, nullable=False)
