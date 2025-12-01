"""
Pydantic schemas for request/response models.
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional

from app.models import IssueStatus, EventType


# Issue schemas

class IssueBase(BaseModel):
    """Base issue schema."""
    sonarqube_issue_key: str
    project_key: str
    rule: str
    severity: str
    component: str
    line: Optional[int] = None
    message: Optional[str] = None


class IssueCreate(IssueBase):
    """Schema for creating a new issue."""
    pass


class IssueUpdate(BaseModel):
    """Schema for updating an issue."""
    status: Optional[IssueStatus] = None
    pr_url: Optional[str] = None
    pr_branch: Optional[str] = None


class IssueResponse(IssueBase):
    """Schema for issue response."""
    id: UUID
    status: IssueStatus
    pr_url: Optional[str] = None
    pr_branch: Optional[str] = None
    pr_merged: int = 0
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class IssueDetail(IssueResponse):
    """Detailed issue response with events."""
    events: list["EventResponse"] = []
    
    model_config = ConfigDict(from_attributes=True)


# Event schemas

class EventBase(BaseModel):
    """Base event schema."""
    event_type: EventType
    message: str
    event_metadata: Optional[str] = None


class EventCreate(EventBase):
    """Schema for creating a new event."""
    issue_id: UUID


class EventResponse(EventBase):
    """Schema for event response."""
    id: UUID
    issue_id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# API response schemas

class PaginatedResponse(BaseModel):
    """Generic paginated response."""
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int


class IssueListResponse(BaseModel):
    """Response for issue list endpoint."""
    items: list[IssueResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class MetricsSummary(BaseModel):
    """Summary metrics for the dashboard."""
    total_issues: int
    new_issues: int
    fixing_issues: int
    pr_open_issues: int
    ci_passed_issues: int
    ci_failed_issues: int
    closed_issues: int
    total_prs_created: int
    merged_prs: int
    rejected_prs: int
    success_rate: float = Field(description="Percentage of PRs that were merged")


class TriggerFixResponse(BaseModel):
    """Response for triggering a fix."""
    success: bool
    message: str
    issue_id: UUID


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime


# Update forward references
IssueDetail.model_rebuild()
