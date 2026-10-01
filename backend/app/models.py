"""
SQLAlchemy database models for the Multi-Agent Lead Generation System.
Designed for Sonar compliance, clean separation of concerns, and full typing.
"""

from datetime import datetime
import uuid
from typing import List, Optional, Any, Dict
from sqlalchemy import (
    String,
    Text,
    Boolean,
    Float,
    DateTime,
    ForeignKey,
    JSON,
    Index,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def generate_uuid() -> str:
    """Generate a standard UUID4 hex string."""
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    """Base declarative class for all models."""
    pass


class Lead(Base):
    """Business Lead entity."""

    __tablename__ = "leads"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    business_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    location: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    social_links: Mapped[List[str]] = mapped_column(JSON, default=list)
    source_urls: Mapped[List[str]] = mapped_column(JSON, default=list)
    place_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, unique=True)

    # Workflow & Review Statuses
    # Statuses: DISCOVERED, ANALYZING, ANALYZED, QUALIFIED, REJECTED,
    # GENERATING_WEBSITE, WEBSITE_READY, GENERATING_PITCH, PITCH_READY, HUMAN_REVIEW, FAILED
    status: Mapped[str] = mapped_column(String(50), default="DISCOVERED", index=True)
    # Review Statuses: PENDING, APPROVED, REJECTED, CONTACTED
    review_status: Mapped[str] = mapped_column(String(50), default="PENDING", index=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    analysis: Mapped[Optional["BusinessAnalysis"]] = relationship(
        "BusinessAnalysis", back_populates="lead", uselist=False, cascade="all, delete-orphan"
    )
    opportunity: Mapped[Optional["Opportunity"]] = relationship(
        "Opportunity", back_populates="lead", uselist=False, cascade="all, delete-orphan"
    )
    prototype: Mapped[Optional["Prototype"]] = relationship(
        "Prototype", back_populates="lead", uselist=False, cascade="all, delete-orphan"
    )
    pitch: Mapped[Optional["Pitch"]] = relationship(
        "Pitch", back_populates="lead", uselist=False, cascade="all, delete-orphan"
    )
    agent_runs: Mapped[List["AgentRun"]] = relationship(
        "AgentRun", back_populates="lead", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_lead_dedup", "business_name", "location", "phone"),
    )


class BusinessAnalysis(Base):
    """Business and digital presence analysis performed by Agent 2."""

    __tablename__ = "business_analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    lead_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    # MISSING, PRESENT, NEEDS_IMPROVEMENT, UNKNOWN
    website_status: Mapped[str] = mapped_column(String(50), nullable=False)
    business_summary: Mapped[str] = mapped_column(Text, nullable=False)
    current_digital_presence: Mapped[str] = mapped_column(Text, nullable=False)
    observations: Mapped[List[str]] = mapped_column(JSON, default=list)
    missing_features: Mapped[List[str]] = mapped_column(JSON, default=list)
    website_opportunity: Mapped[bool] = mapped_column(Boolean, default=False)
    evidence: Mapped[List[str]] = mapped_column(JSON, default=list)
    source_urls: Mapped[List[str]] = mapped_column(JSON, default=list)
    analyzed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    lead: Mapped["Lead"] = relationship("Lead", back_populates="analysis")


class Opportunity(Base):
    """Opportunity validation decision performed by Agent 3."""

    __tablename__ = "opportunities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    lead_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    qualified: Mapped[bool] = mapped_column(Boolean, nullable=False, index=True)
    opportunity_type: Mapped[str] = mapped_column(String(100), default="SINGLE_PAGE_WEBSITE")
    priority: Mapped[str] = mapped_column(String(20), default="MEDIUM")  # HIGH, MEDIUM, LOW
    confidence: Mapped[float] = mapped_column(Float, default=0.5)  # 0.0 to 1.0
    reasoning: Mapped[List[str]] = mapped_column(JSON, default=list)
    evidence: Mapped[List[str]] = mapped_column(JSON, default=list)
    recommended_solution: Mapped[str] = mapped_column(Text, default="")
    risks: Mapped[List[str]] = mapped_column(JSON, default=list)
    validated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    lead: Mapped["Lead"] = relationship("Lead", back_populates="opportunity")


class Prototype(Base):
    """Single-page website prototype generated by Agent 4."""

    __tablename__ = "prototypes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    lead_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    site_title: Mapped[str] = mapped_column(String(255), nullable=False)
    tagline: Mapped[str] = mapped_column(String(255), default="")
    color_scheme: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    hero_section: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    about_section: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    services_section: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    why_us_section: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    gallery_section: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    contact_section: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    cta_section: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    full_config: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    preview_url: Mapped[str] = mapped_column(String(255), default="")
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    lead: Mapped["Lead"] = relationship("Lead", back_populates="prototype")


class Pitch(Base):
    """Personalized sales pitches generated by Agent 5."""

    __tablename__ = "pitches"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    lead_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    short_pitch: Mapped[str] = mapped_column(Text, nullable=False)  # WhatsApp / DM
    email_pitch: Mapped[str] = mapped_column(Text, nullable=False)  # Professional email
    detailed_pitch: Mapped[str] = mapped_column(Text, nullable=False)  # In-depth proposal
    observations_referenced: Mapped[List[str]] = mapped_column(JSON, default=list)
    demo_link: Mapped[str] = mapped_column(String(255), default="")
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    lead: Mapped["Lead"] = relationship("Lead", back_populates="pitch")


class AgentRun(Base):
    """Audit log of individual agent executions."""

    __tablename__ = "agent_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    lead_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("leads.id", ondelete="CASCADE"), nullable=True, index=True
    )
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="RUNNING")  # RUNNING, SUCCESS, FAILED
    input_data: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    output_data: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    lead: Mapped[Optional["Lead"]] = relationship("Lead", back_populates="agent_runs")


class SystemSetting(Base):
    """Dynamic key-value settings storage."""

    __tablename__ = "system_settings"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
