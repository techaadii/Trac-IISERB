"""
models.py
=========
SQLAlchemy ORM models.
Each class = one database table.
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean, Column, DateTime, Float,
    ForeignKey, Integer, String, Text, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.app.db.base import Base


def gen_uuid():
    return str(uuid.uuid4())


# ── Users ─────────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id            = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    username      = Column(String(50),  unique=True, nullable=False, index=True)
    email         = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role          = Column(String(20),  nullable=False, default="operator")
    # role: "admin" or "operator"
    is_active     = Column(Boolean, default=True)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    sessions      = relationship("SearchSession",   back_populates="user")
    sightings     = relationship("VehicleSighting", back_populates="confirmed_by_user")
    corrections   = relationship("CorrectionHistory", back_populates="corrected_by_user")
    hmm_feedback  = relationship("HMMFeedback",     back_populates="user")


# ── Search Sessions ───────────────────────────────────────────────────────────

class SearchSession(Base):
    __tablename__ = "search_sessions"

    id            = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    session_id    = Column(String(50),  unique=True, nullable=False, index=True)
    user_id       = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)
    query_type    = Column(String(10),  nullable=False)   # "image" or "text"
    query_text    = Column(Text,        nullable=True)    # only for text queries
    viterbi_path  = Column(JSON,        nullable=True)    # ["ENTRY_CAM", "AB4", ...]
    total_images  = Column(Integer,     default=0)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user          = relationship("User",           back_populates="sessions")
    results       = relationship("SearchResult",   back_populates="session",
                                 cascade="all, delete-orphan")
    corrections   = relationship("CorrectionHistory", back_populates="session")


# ── Search Results ────────────────────────────────────────────────────────────

class SearchResult(Base):
    __tablename__ = "search_results"

    id            = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    session_id    = Column(String(50), ForeignKey("search_sessions.session_id"),
                           nullable=False, index=True)
    camera_id     = Column(String(50),  nullable=False)
    image_path    = Column(Text,        nullable=False)
    similarity    = Column(Float,       nullable=False)
    rank          = Column(Integer,     nullable=False)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    session       = relationship("SearchSession", back_populates="results")


# ── Vehicle Sightings ─────────────────────────────────────────────────────────

class VehicleSighting(Base):
    __tablename__ = "vehicle_sightings"

    id              = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    session_id      = Column(String(50), ForeignKey("search_sessions.session_id"),
                             nullable=True, index=True)
    camera_id       = Column(String(50),  nullable=False)
    image_path      = Column(Text,        nullable=False)
    confirmed_by    = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)
    plate_number    = Column(String(20),  nullable=True)   # optional
    vehicle_type    = Column(String(50),  nullable=True)   # car/bike/truck etc
    notes           = Column(Text,        nullable=True)
    confirmed_at    = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    confirmed_by_user = relationship("User", back_populates="sightings")


# ── Correction History ────────────────────────────────────────────────────────

class CorrectionHistory(Base):
    __tablename__ = "correction_history"

    id                   = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    session_id           = Column(String(50), ForeignKey("search_sessions.session_id"),
                                  nullable=False, index=True)
    camera_id            = Column(String(50),  nullable=False)
    original_image_path  = Column(Text,        nullable=True)
    corrected_image_path = Column(Text,        nullable=False)
    corrected_by         = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)
    # Combined embedding weights used for re-search
    original_weight      = Column(Float, default=0.3)
    corrected_weight     = Column(Float, default=0.7)
    created_at           = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    session              = relationship("SearchSession",  back_populates="corrections")
    corrected_by_user    = relationship("User",           back_populates="corrections")


# ── Camera Events ─────────────────────────────────────────────────────────────

class CameraEvent(Base):
    __tablename__ = "camera_events"

    id          = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    camera_id   = Column(String(50),  nullable=False, index=True)
    event_type  = Column(String(20),  nullable=False)
    # event_type: "online" | "offline" | "alert" | "error"
    message     = Column(Text,        nullable=True)
    timestamp   = Column(DateTime(timezone=True), server_default=func.now())


# ── HMM Feedback ──────────────────────────────────────────────────────────────

class HMMFeedback(Base):
    __tablename__ = "hmm_feedback"

    id          = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    from_cam    = Column(String(50),  nullable=False)
    to_cam      = Column(String(50),  nullable=False)
    confirmed   = Column(Boolean,     nullable=False)
    user_id     = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user        = relationship("User", back_populates="hmm_feedback")