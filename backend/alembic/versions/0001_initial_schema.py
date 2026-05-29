"""initial schema

Revision ID: e5d477318cf1
Revises:
Create Date: 2026-05-29
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "e5d477318cf1"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- Tipos ENUM ---------------------------------------------------------
    journey_stage_enum = postgresql.ENUM(
        "onboarding", "learning", "practicing", "graduating", "graduated",
        name="journey_stage_enum",
    )
    module_type_enum = postgresql.ENUM(
        "simulator", "guide", "safety", "procedure",
        name="module_type_enum",
    )
    content_area_enum = postgresql.ENUM(
        "comunicacion", "banca", "seguridad", "gobierno", "mi_telefono",
        name="content_area_enum",
    )
    trigger_type_enum = postgresql.ENUM(
        "lesson_count", "area_first", "area_complete", "assessment_complete",
        name="trigger_type_enum",
    )
    request_status_enum = postgresql.ENUM(
        "received", "in_development", "available",
        name="request_status_enum",
    )

    for enum_type in (
        journey_stage_enum, module_type_enum, content_area_enum,
        trigger_type_enum, request_status_enum,
    ):
        enum_type.create(op.get_bind(), checkfirst=True)

    # --- users --------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("phone_number", sa.String(20), nullable=False, unique=True),
        sa.Column("full_name", sa.String(255)),
        sa.Column("age", sa.SmallInteger()),
        sa.Column("city", sa.String(100)),
        sa.Column("avatar_url", sa.String(500)),
        sa.Column("phone_verified", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "journey_stage",
            sa.Enum("onboarding", "learning", "practicing", "graduating", "graduated",
                    name="journey_stage_enum"),
            nullable=False,
            server_default="onboarding",
        ),
        sa.Column("competency_map", postgresql.JSON(), nullable=False, server_default="{}"),
        sa.Column("preferred_lesson_duration", sa.SmallInteger(), nullable=False, server_default="8"),
        sa.Column("reminders_enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("reminder_hour", sa.SmallInteger(), nullable=False, server_default="10"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # --- sms_verifications --------------------------------------------------
    op.create_table(
        "sms_verifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("phone_number", sa.String(20), nullable=False),
        sa.Column("code", sa.String(6), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # --- refresh_tokens -----------------------------------------------------
    op.create_table(
        "refresh_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id", postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column("token_hash", sa.String(255), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # --- simulator_catalog --------------------------------------------------
    op.create_table(
        "simulator_catalog",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("slug", sa.String(50), nullable=False, unique=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column(
            "module_type",
            sa.Enum("simulator", "guide", "safety", "procedure", name="module_type_enum"),
            nullable=False,
        ),
        sa.Column(
            "content_area",
            sa.Enum("comunicacion", "banca", "seguridad", "gobierno", "mi_telefono",
                    name="content_area_enum"),
            nullable=False,
        ),
        sa.Column("icon", sa.String(50)),
        sa.Column("difficulty", sa.SmallInteger(), nullable=False, server_default="1"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("config", postgresql.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # --- lessons ------------------------------------------------------------
    op.create_table(
        "lessons",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column(
            "content_area",
            sa.Enum("comunicacion", "banca", "seguridad", "gobierno", "mi_telefono",
                    name="content_area_enum"),
            nullable=False,
        ),
        sa.Column(
            "module_type",
            sa.Enum("simulator", "guide", "safety", "procedure", name="module_type_enum"),
            nullable=False,
        ),
        sa.Column("duration_minutes", sa.SmallInteger(), nullable=False, server_default="8"),
        sa.Column("thumbnail_url", sa.String(500)),
        sa.Column("description", sa.Text()),
        sa.Column(
            "simulator_id", postgresql.UUID(as_uuid=True),
            sa.ForeignKey("simulator_catalog.id", ondelete="SET NULL"), nullable=True,
        ),
        sa.Column(
            "prerequisite_id", postgresql.UUID(as_uuid=True),
            sa.ForeignKey("lessons.id", ondelete="SET NULL"), nullable=True,
        ),
        sa.Column("order_index", sa.SmallInteger(), nullable=False, server_default="0"),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("has_exportable_summary", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # --- user_progress ------------------------------------------------------
    op.create_table(
        "user_progress",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id", postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column(
            "lesson_id", postgresql.UUID(as_uuid=True),
            sa.ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column("completion_pct", sa.SmallInteger(), nullable=False, server_default="0"),
        sa.Column("completed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("last_watched_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "lesson_id", name="uq_user_progress_user_lesson"),
    )

    # --- simulator_sessions -------------------------------------------------
    op.create_table(
        "simulator_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id", postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column(
            "simulator_id", postgresql.UUID(as_uuid=True),
            sa.ForeignKey("simulator_catalog.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True)),
        sa.Column("steps_completed", sa.SmallInteger(), nullable=False, server_default="0"),
        sa.Column("completed", sa.Boolean(), nullable=False, server_default="false"),
    )

    # --- user_activity ------------------------------------------------------
    op.create_table(
        "user_activity",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id", postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True,
        ),
        sa.Column("first_visit_date", sa.Date(), nullable=False),
        sa.Column("last_visit_date", sa.Date(), nullable=False),
        sa.Column("total_active_days", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # --- achievements -------------------------------------------------------
    op.create_table(
        "achievements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("key", sa.String(50), nullable=False, unique=True),
        sa.Column(
            "trigger_type",
            sa.Enum("lesson_count", "area_first", "area_complete", "assessment_complete",
                    name="trigger_type_enum"),
            nullable=False,
        ),
        sa.Column("content_area", sa.String(50)),
        sa.Column("threshold", sa.SmallInteger(), nullable=False, server_default="1"),
    )

    # --- user_achievements --------------------------------------------------
    op.create_table(
        "user_achievements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id", postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column(
            "achievement_id", postgresql.UUID(as_uuid=True),
            sa.ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column("earned_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "achievement_id", name="uq_user_achievement"),
    )

    # --- assessment_responses -----------------------------------------------
    op.create_table(
        "assessment_responses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id", postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column("question_key", sa.String(50), nullable=False),
        sa.Column("answer_value", sa.SmallInteger(), nullable=False),
        sa.Column("answered_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "question_key", name="uq_assessment_user_question"),
    )

    # --- learning_requests --------------------------------------------------
    op.create_table(
        "learning_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id", postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category", sa.String(100)),
        sa.Column("votes", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "status",
            sa.Enum("received", "in_development", "available", name="request_status_enum"),
            nullable=False,
            server_default="received",
        ),
        sa.Column(
            "fulfilled_by_lesson_id", postgresql.UUID(as_uuid=True),
            sa.ForeignKey("lessons.id", ondelete="SET NULL"), nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # --- request_votes ------------------------------------------------------
    op.create_table(
        "request_votes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "request_id", postgresql.UUID(as_uuid=True),
            sa.ForeignKey("learning_requests.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column(
            "user_id", postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column("voted_at", sa.DateTime(timezone=True), nullable=False),
    )

    # --- exported_summaries -------------------------------------------------
    op.create_table(
        "exported_summaries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id", postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column(
            "lesson_id", postgresql.UUID(as_uuid=True),
            sa.ForeignKey("lessons.id", ondelete="SET NULL"), nullable=True,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("file_url", sa.String(500), nullable=False),
        sa.Column("summary_type", sa.String(50), nullable=False, server_default="lesson"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    # --- Índices de rendimiento ---------------------------------------------
    op.create_index("ix_user_progress_user", "user_progress", ["user_id"])
    op.create_index("ix_simulator_sessions_user", "simulator_sessions", ["user_id"])
    op.create_index("ix_learning_requests_status", "learning_requests", ["status"])
    op.create_index("ix_request_votes_request", "request_votes", ["request_id"])
    op.create_index("ix_sms_verifications_phone", "sms_verifications", ["phone_number"])


def downgrade() -> None:
    op.drop_table("exported_summaries")
    op.drop_table("request_votes")
    op.drop_table("learning_requests")
    op.drop_table("assessment_responses")
    op.drop_table("user_achievements")
    op.drop_table("achievements")
    op.drop_table("user_activity")
    op.drop_table("simulator_sessions")
    op.drop_table("user_progress")
    op.drop_table("lessons")
    op.drop_table("simulator_catalog")
    op.drop_table("refresh_tokens")
    op.drop_table("sms_verifications")
    op.drop_table("users")

    for name in (
        "request_status_enum", "trigger_type_enum",
        "content_area_enum", "module_type_enum", "journey_stage_enum",
    ):
        postgresql.ENUM(name=name).drop(op.get_bind(), checkfirst=True)
