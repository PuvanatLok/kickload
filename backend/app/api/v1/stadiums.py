from fastapi import APIRouter, Depends, Query
from geoalchemy2.functions import ST_DWithin, ST_MakePoint
from sqlalchemy import cast, select
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2 import Geography

from app.database import get_db
from app.models.stadium import Stadium

router = APIRouter(prefix="/stadiums", tags=["stadiums"])


@router.get("/nearby")
async def find_nearby_stadiums(
    lat: float = Query(..., description="User latitude"),
    lon: float = Query(..., description="User longitude"),
    radius_meters: int = Query(10000, description="Search radius in meters"),
    db: AsyncSession = Depends(get_db),
):
    """
    Finds active stadiums within radius_meters of the given coordinates.

    WHY ST_DWithin NOT ST_Distance:
    ST_Distance calculates distance for every row in the table, then filters.
    ST_DWithin uses the spatial index (GiST) to skip rows outside the radius
    entirely — dramatically faster at scale. Always use ST_DWithin for
    "within X meters" queries.

    WHY METERS NOT KILOMETERS:
    ST_DWithin on Geography columns uses meters as the unit automatically.
    No conversion needed. This is another reason to use Geography over Geometry.
    """
    user_location = cast(
        ST_MakePoint(lon, lat),
        Geography(srid=4326),
    )

    result = await db.execute(
        select(Stadium)
        .where(Stadium.is_active.is_(True))
        .where(ST_DWithin(Stadium.location, user_location, radius_meters))
        .order_by(ST_DWithin(Stadium.location, user_location, radius_meters))
        .limit(20)
    )
    stadiums = result.scalars().all()

    return [
        {
            "id": str(s.id),
            "name": s.name,
            "surface_type": s.surface_type,
            "price_per_hour": float(s.price_per_hour),
            "formats": s.formats,
        }
        for s in stadiums
    ]
