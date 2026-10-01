"""
Pydantic V2 data schemas for the Multi-Agent Lead Generation System.
Ensures strict typed validation and Sonar-compliant contracts across all agents and APIs.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class LeadBase(BaseModel):
    """Base business lead schema."""
    business_name: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    location: str = Field(..., min_length=1, max_length=255)
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    social_links: List[str] = Field(default_factory=list)
    source_urls: List[str] = Field(default_factory=list)
    place_id: Optional[str] = None


class LeadCreate(LeadBase):
    """Schema for lead creation."""
    status: str = "DISCOVERED"


class LeadUpdate(BaseModel):
    """Schema for updating lead details."""
    business_name: Optional[str] = None
    category: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    notes: Optional[str] = None
    review_status: Optional[str] = None


class ReviewStatusUpdate(BaseModel):
    """Schema for human review action."""
    review_status: str = Field(..., pattern="^(PENDING|APPROVED|REJECTED|CONTACTED)$")
    notes: Optional[str] = None


class BusinessAnalysisResponse(BaseModel):
    """Schema for business & digital presence analysis."""
    id: str
    lead_id: str
    website_status: str
    business_summary: str
    current_digital_presence: str
    observations: List[str] = Field(default_factory=list)
    missing_features: List[str] = Field(default_factory=list)
    website_opportunity: bool = False
    evidence: List[str] = Field(default_factory=list)
    source_urls: List[str] = Field(default_factory=list)
    analyzed_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OpportunityResponse(BaseModel):
    """Schema for opportunity qualification."""
    id: str
    lead_id: str
    qualified: bool
    opportunity_type: str
    priority: str
    confidence: float
    reasoning: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    recommended_solution: str
    risks: List[str] = Field(default_factory=list)
    validated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PrototypeResponse(BaseModel):
    """Schema for single-page website prototype."""
    id: str
    lead_id: str
    site_title: str
    tagline: str
    color_scheme: Dict[str, Any] = Field(default_factory=dict)
    hero_section: Dict[str, Any] = Field(default_factory=dict)
    about_section: Dict[str, Any] = Field(default_factory=dict)
    services_section: Dict[str, Any] = Field(default_factory=dict)
    why_us_section: Dict[str, Any] = Field(default_factory=dict)
    gallery_section: Dict[str, Any] = Field(default_factory=dict)
    contact_section: Dict[str, Any] = Field(default_factory=dict)
    cta_section: Dict[str, Any] = Field(default_factory=dict)
    full_config: Dict[str, Any] = Field(default_factory=dict)
    preview_url: str = ""
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PitchResponse(BaseModel):
    """Schema for personalized sales pitches."""
    id: str
    lead_id: str
    short_pitch: str
    email_pitch: str
    detailed_pitch: str
    observations_referenced: List[str] = Field(default_factory=list)
    demo_link: str = ""
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AgentRunResponse(BaseModel):
    """Schema for agent execution audit log."""
    id: str
    agent_name: str
    lead_id: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_data: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class LeadResponse(LeadBase):
    """Summary schema for a business lead in listings."""
    id: str
    status: str
    review_status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    # Summary fields extracted for table display
    analysis_status: Optional[str] = None
    qualified: Optional[bool] = None
    priority: Optional[str] = None
    confidence: Optional[float] = None
    has_prototype: bool = False
    has_pitch: bool = False

    model_config = ConfigDict(from_attributes=True)


class LeadDetailResponse(LeadResponse):
    """Full detail dossier for a lead, including all related agent outputs."""
    analysis: Optional[BusinessAnalysisResponse] = None
    opportunity: Optional[OpportunityResponse] = None
    prototype: Optional[PrototypeResponse] = None
    pitch: Optional[PitchResponse] = None
    agent_runs: List[AgentRunResponse] = Field(default_factory=list)


class DashboardStats(BaseModel):
    """Key Performance Indicators for the dashboard."""
    total_leads: int = 0
    new_leads: int = 0
    analyzed: int = 0
    qualified: int = 0
    rejected: int = 0
    websites_generated: int = 0
    pitches_ready: int = 0
    approved: int = 0
    contacted: int = 0


class PipelineRunRequest(BaseModel):
    """Request payload to trigger a lead discovery and analysis run."""
    category: str = Field(default="Restaurants", description="Target industry or business type")
    location: str = Field(default="Downtown, CA", description="City, state, or neighborhood")
    max_leads: int = Field(default=5, ge=1, le=20)


class PipelineRunResponse(BaseModel):
    """Response payload for a pipeline execution."""
    status: str
    message: str
    leads_discovered: int
    leads_processed: int
    qualified_count: int
    rejected_count: int
