"""
SQLAlchemy models for the application.
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.database import Base


class IssueStatus(str, enum.Enum):
    """Status of an issue in the fix pipeline."""
    NEW = "NEW"
    FIXING = "FIXING"
    PR_OPEN = "PR_OPEN"
    CI_PASSED = "CI_PASSED"
    CI_FAILED = "CI_FAILED"
    CLOSED = "CLOSED"


class EventType(str, enum.Enum):
    """Types of events that can occur."""
    ISSUE_DETECTED = "ISSUE_DETECTED"
    AI_CALLED = "AI_CALLED"
    PR_CREATED = "PR_CREATED"
    CI_PASSED = "CI_PASSED"
    CI_FAILED = "CI_FAILED"
    STATUS_UPDATED = "STATUS_UPDATED"
    ERROR = "ERROR"


class Issue(Base):
    """SonarQube issue with AI fix status."""
    __tablename__ = "issues"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sonarqube_issue_key = Column(String(255), unique=True, nullable=False, index=True)
    project_key = Column(String(255), nullable=False, index=True)
    rule = Column(String(255), nullable=False)
    severity = Column(String(50), nullable=False)
    component = Column(String(500), nullable=False)  # File path
    line = Column(Integer, nullable=True)
    message = Column(Text, nullable=True)  # Issue description from SonarQube
    status = Column(SQLEnum(IssueStatus), nullable=False, default=IssueStatus.NEW, index=True)
    pr_url = Column(String(500), nullable=True)
    pr_branch = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    events = relationship("Event", back_populates="issue", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Issue(key={self.sonarqube_issue_key}, status={self.status})>"


class Event(Base):
    """Events tracking the lifecycle of an issue."""
    __tablename__ = "events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    issue_id = Column(UUID(as_uuid=True), ForeignKey("issues.id"), nullable=False, index=True)
    event_type = Column(SQLEnum(EventType), nullable=False, index=True)
    message = Column(Text, nullable=False)
    event_metadata = Column(Text, nullable=True)  # JSON string for additional data
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    issue = relationship("Issue", back_populates="events")
    
    def __repr__(self):
        return f"<Event(type={self.event_type}, issue_id={self.issue_id})>"
