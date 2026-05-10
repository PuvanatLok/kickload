import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.events.publisher import publish_event
from app.models.match import Match, MatchPositionSlot, MatchTeam
from app.models.player import Player

router = APIRouter(prefix="/matches", tags=["matches"])


class PositionSlotInput(BaseModel):
    position: str
    count: int


class MatchCreateRequest(BaseModel):
    stadium_id: uuid.UUID | None = None
    format: str
    starts_at: datetime
    duration_hours: float = 1.5
    field_cost: float = 0
    skill_min: int = 0
    skill_max: int = 9999
    team_a_slots: list[PositionSlotInput]
    team_b_slots: list[PositionSlotInput]


class JoinMatchRequest(BaseModel):
    slot_id: uuid.UUID
    player_id: uuid.UUID


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_match(body: MatchCreateRequest, db: AsyncSession = Depends(get_db)):
    match = Match(
        stadium_id=body.stadium_id,
        created_by=uuid.uuid4(),  # replace with real auth user id
        format=body.format,
        starts_at=body.starts_at,
        duration_hours=body.duration_hours,
        field_cost=body.field_cost,
        skill_min=body.skill_min,
        skill_max=body.skill_max,
    )
    db.add(match)
    await db.flush()
    # WHY FLUSH NOT COMMIT HERE:
    # flush() sends the INSERT to the DB and gets the generated ID back,
    # but keeps the transaction open. This lets us use match.id to create
    # the related teams and slots in the same transaction. If anything fails,
    # the whole transaction rolls back — no orphaned match with no teams.

    for label, slots in [("A", body.team_a_slots), ("B", body.team_b_slots)]:
        team = MatchTeam(match_id=match.id, label=label)
        db.add(team)
        await db.flush()

        for slot_input in slots:
            for _ in range(slot_input.count):
                db.add(MatchPositionSlot(match_team_id=team.id, position=slot_input.position))

    await publish_event(
        event_type="match_created",
        payload={
            "match_id": str(match.id),
            "format": match.format,
            "starts_at": match.starts_at.isoformat(),
            "field_cost": float(match.field_cost),
        },
    )

    return {"match_id": str(match.id)}


@router.post("/{match_id}/join")
async def join_match(
    match_id: uuid.UUID,
    body: JoinMatchRequest,
    db: AsyncSession = Depends(get_db),
):
    # Verify the slot exists, belongs to this match, and is open
    slot = await db.get(MatchPositionSlot, body.slot_id)
    if not slot:
        raise HTTPException(status_code=404, detail="Position slot not found")
    if slot.filled_by is not None:
        raise HTTPException(status_code=409, detail="Position slot already filled")
    # 409 Conflict is the correct HTTP status for "resource state prevents this action".
    # 400 Bad Request is for malformed input, not state conflicts.

    # Verify player ELO is within match skill range
    player = await db.get(Player, body.player_id)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")

    team = await db.get(MatchTeam, slot.match_team_id)
    match = await db.get(Match, team.match_id)

    if not (match.skill_min <= player.elo_rating <= match.skill_max):
        raise HTTPException(
            status_code=403,
            detail=f"Player ELO {player.elo_rating} is outside match range "
                   f"{match.skill_min}–{match.skill_max}",
        )

    slot.filled_by = body.player_id

    await publish_event(
        event_type="player_joined",
        payload={
            "match_id": str(match_id),
            "player_id": str(body.player_id),
            "position": slot.position,
            "slot_id": str(body.slot_id),
        },
        user_id=str(body.player_id),
    )

    # Check if match is now full and update status
    result = await db.execute(
        select(MatchPositionSlot).where(
            MatchPositionSlot.match_team_id == slot.match_team_id,
            MatchPositionSlot.filled_by.is_(None),
        )
    )
    open_slots = result.scalars().all()
    if not open_slots:
        match.status = "full"
        await publish_event("match_filled", {"match_id": str(match_id)})

    return {"joined": True, "position": slot.position}
