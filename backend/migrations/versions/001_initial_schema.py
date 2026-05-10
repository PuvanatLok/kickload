"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-05-11
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ARRAY
import geoalchemy2

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # WHY EXTENSIONS FIRST:
    # PostGIS and uuid-ossp are PostgreSQL extensions that must be enabled
    # before any table uses their types. Creating the geography column or
    # calling gen_random_uuid() without the extension raises an error.
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    op.create_table(
        "players",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("phone", sa.String(20), nullable=False, unique=True),
        sa.Column("display_name", sa.String(100), nullable=False),
        sa.Column("avatar_url", sa.String),
        sa.Column("line_id", sa.String(100), unique=True),
        sa.Column("preferred_positions", ARRAY(sa.String(3))),
        sa.Column("elo_rating", sa.Integer, nullable=False, server_default="1000"),
        sa.Column("games_played", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "stadiums",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("owner_id", UUID(as_uuid=True), sa.ForeignKey("players.id")),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("address", sa.String),
        sa.Column("location", geoalchemy2.Geography(geometry_type="POINT", srid=4326), nullable=False),
        sa.Column("surface_type", sa.String(20)),
        sa.Column("formats", ARRAY(sa.String(10))),
        sa.Column("price_per_hour", sa.Numeric(10, 2), nullable=False),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    # Spatial index — required for ST_DWithin to use the GiST index.
    # Without this, every nearby search is a full table scan.
    op.create_index("idx_stadiums_location", "stadiums", ["location"], postgresql_using="gist")

    op.create_table(
        "matches",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("stadium_id", UUID(as_uuid=True), sa.ForeignKey("stadiums.id")),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("players.id"), nullable=False),
        sa.Column("format", sa.String(10), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duration_hours", sa.Numeric(3, 1), nullable=False, server_default="1.5"),
        sa.Column("field_cost", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("skill_min", sa.Integer, server_default="0"),
        sa.Column("skill_max", sa.Integer, server_default="9999"),
        sa.Column("status", sa.String(20), server_default="open"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("idx_matches_status_starts_at", "matches", ["status", "starts_at"])

    op.create_table(
        "match_teams",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("match_id", UUID(as_uuid=True), sa.ForeignKey("matches.id"), nullable=False),
        sa.Column("label", sa.String(1), nullable=False),
        sa.Column("treasurer_id", UUID(as_uuid=True), sa.ForeignKey("players.id")),
    )

    op.create_table(
        "match_position_slots",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("match_team_id", UUID(as_uuid=True), sa.ForeignKey("match_teams.id"), nullable=False),
        sa.Column("position", sa.String(3), nullable=False),
        sa.Column("filled_by", UUID(as_uuid=True), sa.ForeignKey("players.id")),
    )
    # Index for "find all open slots for a team" — used in join validation
    op.create_index("idx_slots_team_open", "match_position_slots", ["match_team_id", "filled_by"])

    op.create_table(
        "team_payments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("match_team_id", UUID(as_uuid=True), sa.ForeignKey("match_teams.id"), nullable=False),
        sa.Column("total_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("paid_to_stadium", sa.Boolean, server_default="false"),
        sa.Column("paid_at", sa.DateTime(timezone=True)),
        sa.Column("confirmed_by", UUID(as_uuid=True), sa.ForeignKey("players.id")),
    )

    op.create_table(
        "player_payment_shares",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("team_payment_id", UUID(as_uuid=True), sa.ForeignKey("team_payments.id"), nullable=False),
        sa.Column("player_id", UUID(as_uuid=True), sa.ForeignKey("players.id"), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("confirmed_at", sa.DateTime(timezone=True)),
        sa.Column("confirmed_by", UUID(as_uuid=True), sa.ForeignKey("players.id")),
        sa.UniqueConstraint("team_payment_id", "player_id", name="uq_share_per_player"),
    )


def downgrade() -> None:
    # WHY DOWNGRADE EXISTS:
    # Alembic can roll back migrations — useful when a deployment goes wrong
    # and you need to revert the schema to match the previous code version.
    # Always write the downgrade even if you never expect to use it.
    op.drop_table("player_payment_shares")
    op.drop_table("team_payments")
    op.drop_index("idx_slots_team_open", "match_position_slots")
    op.drop_table("match_position_slots")
    op.drop_table("match_teams")
    op.drop_index("idx_matches_status_starts_at", "matches")
    op.drop_table("matches")
    op.drop_index("idx_stadiums_location", "stadiums")
    op.drop_table("stadiums")
    op.drop_table("players")
