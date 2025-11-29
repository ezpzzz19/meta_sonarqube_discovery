"""
FastAPI routes for the API.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID
from typing import Optional
import math

from app.database import get_db
from app.models import Issue, Event, IssueStatus, EventType
from app.schemas import (
    IssueResponse,
    IssueDetail,
    IssueListResponse,
    EventResponse,
    MetricsSummary,
    TriggerFixResponse,
)
from app.fixer_service import fixer_service

router = APIRouter()


@router.get("/issues", response_model=IssueListResponse)
async def list_issues(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    List all issues with optional filters and pagination.
    """
    query = db.query(Issue)
    
    # Apply filters
    if status:
        try:
            status_enum = IssueStatus(status)
            query = query.filter(Issue.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    
    if severity:
        query = query.filter(Issue.severity == severity)
    
    # Get total count
    total = query.count()
    
    # Calculate pagination
    total_pages = math.ceil(total / page_size)
    offset = (page - 1) * page_size
    
    # Fetch issues
    issues = query.order_by(Issue.created_at.desc()).offset(offset).limit(page_size).all()
    
    return IssueListResponse(
        items=[IssueResponse.model_validate(issue) for issue in issues],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/issues/{issue_id}", response_model=IssueDetail)
async def get_issue(
    issue_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get detailed information about a specific issue, including events.
    """
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    return IssueDetail.model_validate(issue)


@router.post("/issues/{issue_id}/trigger-fix", response_model=TriggerFixResponse)
async def trigger_fix(
    issue_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Manually trigger an AI fix for a specific issue.
    """
    # Check if issue exists
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    # Attempt the fix
    result = await fixer_service.attempt_fix(str(issue_id), db)
    
    return TriggerFixResponse(
        success=result.get("success", False),
        message=result.get("message", ""),
        issue_id=issue_id,
    )


@router.get("/events/recent", response_model=list[EventResponse])
async def get_recent_events(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """
    Get recent events across all issues.
    """
    events = (
        db.query(Event)
        .order_by(Event.created_at.desc())
        .limit(limit)
        .all()
    )
    
    return [EventResponse.model_validate(event) for event in events]


@router.get("/metrics/summary", response_model=MetricsSummary)
async def get_metrics_summary(
    db: Session = Depends(get_db),
):
    """
    Get aggregate metrics for the dashboard.
    """
    # Count issues by status
    total_issues = db.query(Issue).count()
    new_issues = db.query(Issue).filter(Issue.status == IssueStatus.NEW).count()
    fixing_issues = db.query(Issue).filter(Issue.status == IssueStatus.FIXING).count()
    pr_open_issues = db.query(Issue).filter(Issue.status == IssueStatus.PR_OPEN).count()
    ci_passed_issues = db.query(Issue).filter(Issue.status == IssueStatus.CI_PASSED).count()
    ci_failed_issues = db.query(Issue).filter(Issue.status == IssueStatus.CI_FAILED).count()
    closed_issues = db.query(Issue).filter(Issue.status == IssueStatus.CLOSED).count()
    
    # Count total PRs created
    total_prs_created = db.query(Issue).filter(Issue.pr_url.isnot(None)).count()
    
    # Calculate success rate (CI passed / total PRs with CI results)
    total_with_ci = ci_passed_issues + ci_failed_issues
    success_rate = (ci_passed_issues / total_with_ci * 100) if total_with_ci > 0 else 0.0
    
    return MetricsSummary(
        total_issues=total_issues,
        new_issues=new_issues,
        fixing_issues=fixing_issues,
        pr_open_issues=pr_open_issues,
        ci_passed_issues=ci_passed_issues,
        ci_failed_issues=ci_failed_issues,
        closed_issues=closed_issues,
        total_prs_created=total_prs_created,
        success_rate=round(success_rate, 2),
    )


@router.post("/sync")
async def sync_issues(
    db: Session = Depends(get_db),
):
    """
    Manually trigger a sync of issues from SonarQube.
    """
    try:
        new_count = await fixer_service.sync_sonarqube_issues(db)
        return {
            "success": True,
            "message": f"Synced {new_count} new issues from SonarQube",
            "new_issues": new_count,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync issues: {str(e)}")
