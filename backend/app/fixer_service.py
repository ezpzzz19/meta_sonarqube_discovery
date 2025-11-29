"""
Fixer service orchestrating the AI fix workflow.
"""
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from app.models import Issue, Event, IssueStatus, EventType
from app.sonarqube_client import sonarqube_client
from app.github_client import github_client
from app.ai_client import ai_client
from app.database import get_db_context

logger = logging.getLogger(__name__)


class FixerService:
    """Service for orchestrating AI-powered fixes."""
    
    async def sync_sonarqube_issues(self, db: Session) -> int:
        """
        Fetch issues from SonarQube and sync to database.
        
        Args:
            db: Database session
            
        Returns:
            Number of new issues added
        """
        logger.info("Syncing issues from SonarQube...")
        
        try:
            # Fetch open issues from SonarQube
            response = await sonarqube_client.get_issues(
                statuses=["OPEN", "CONFIRMED", "REOPENED"],
                page_size=500,
            )
            
            issues_data = response.get("issues", [])
            new_count = 0
            
            for issue_data in issues_data:
                issue_key = issue_data.get("key")
                
                # Check if issue already exists
                existing = db.query(Issue).filter(
                    Issue.sonarqube_issue_key == issue_key
                ).first()
                
                if existing:
                    continue
                
                # Parse component to get file path
                component = issue_data.get("component", "")
                file_path = sonarqube_client.parse_component_path(component)
                
                # Create new issue
                issue = Issue(
                    sonarqube_issue_key=issue_key,
                    project_key=issue_data.get("project", ""),
                    rule=issue_data.get("rule", ""),
                    severity=issue_data.get("severity", ""),
                    component=file_path,
                    line=issue_data.get("line"),
                    message=issue_data.get("message", ""),
                    status=IssueStatus.NEW,
                )
                db.add(issue)
                db.flush()  # Get the ID
                
                # Create detection event
                event = Event(
                    issue_id=issue.id,
                    event_type=EventType.ISSUE_DETECTED,
                    message="Issue detected by SonarQube: {}".format(issue_data.get('message', '')),
                )
                db.add(event)
                
                new_count += 1
            
            db.commit()
            logger.info("Synced {} new issues from SonarQube".format(new_count))
            return new_count
            
        except Exception as e:
            logger.error("Error syncing SonarQube issues: {}".format(e))
            db.rollback()
            raise
    
    async def attempt_fix(self, issue_id: str, db: Session) -> dict:
        """
        Attempt to fix an issue using AI.
        
        Args:
            issue_id: UUID of the issue
            db: Database session
            
        Returns:
            Dict with success status and message
        """
        logger.info("Attempting to fix issue {}...".format(issue_id))
        
        try:
            # Get the issue
            issue = db.query(Issue).filter(Issue.id == issue_id).first()
            
            if not issue:
                return {"success": False, "message": "Issue not found"}
            
            if issue.status not in [IssueStatus.NEW]:
                return {
                    "success": False,
                    "message": "Issue already in status {}".format(issue.status),
                }
            
            # Update status to FIXING
            issue.status = IssueStatus.FIXING
            db.add(Event(
                issue_id=issue.id,
                event_type=EventType.STATUS_UPDATED,
                message="Status changed to FIXING",
            ))
            db.commit()
            
            # Step 1: Fetch file content from GitHub
            logger.info("Fetching file content for {}...".format(issue.component))
            try:
                file_content, file_sha = github_client.get_file_content(issue.component)
            except Exception as e:
                error_msg = "Failed to fetch file from GitHub: {}".format(str(e))
                logger.error(error_msg)
                issue.status = IssueStatus.NEW
                db.add(Event(
                    issue_id=issue.id,
                    event_type=EventType.ERROR,
                    message=error_msg,
                ))
                db.commit()
                return {"success": False, "message": error_msg}
            
            # Step 2: Call AI to generate fix
            logger.info("Calling AI to generate fix...")
            db.add(Event(
                issue_id=issue.id,
                event_type=EventType.AI_CALLED,
                message="Requesting AI to generate fix",
            ))
            db.commit()
            
            ai_result = await ai_client.generate_fix(
                issue_description=issue.message or "",
                rule=issue.rule,
                severity=issue.severity,
                file_path=issue.component,
                file_content=file_content,
                line_number=issue.line,
            )
            
            if not ai_result.get("success"):
                error_msg = "AI failed to generate fix: {}".format(ai_result.get('explanation'))
                logger.error(error_msg)
                issue.status = IssueStatus.NEW
                db.add(Event(
                    issue_id=issue.id,
                    event_type=EventType.ERROR,
                    message=error_msg,
                ))
                db.commit()
                return {"success": False, "message": error_msg}
            
            fixed_content = ai_result.get("fixed_content", "")
            explanation = ai_result.get("explanation", "")
            
            # Step 3: Create branch and commit fix
            branch_name = "ai-fix/{}".format(issue.sonarqube_issue_key)
            logger.info("Creating branch {}...".format(branch_name))
            
            try:
                github_client.create_branch(branch_name)
                
                # Update file
                commit_message = "Fix SonarQube issue {}\n\n{}".format(issue.sonarqube_issue_key, explanation)
                github_client.update_file(
                    file_path=issue.component,
                    content=fixed_content,
                    commit_message=commit_message,
                    branch=branch_name,
                    sha=file_sha,
                )
                
            except Exception as e:
                error_msg = "Failed to create branch or commit: {}".format(str(e))
                logger.error(error_msg)
                issue.status = IssueStatus.NEW
                db.add(Event(
                    issue_id=issue.id,
                    event_type=EventType.ERROR,
                    message=error_msg,
                ))
                db.commit()
                return {"success": False, "message": error_msg}
            
            # Step 4: Create pull request
            logger.info("Creating pull request...")
            pr_title = "[AI Fix] {}: {}".format(issue.rule, issue.component)
            pr_body = """## AI-Generated Fix for SonarQube Issue

**Issue Key:** {}
**Rule:** {}
**Severity:** {}
**File:** {}
**Line:** {}

### Issue Description
{}

### AI Explanation
{}

---
*This pull request was automatically generated by the SonarQube Code Janitor.*
""".format(issue.sonarqube_issue_key, issue.rule, issue.severity, issue.component, issue.line or 'N/A', issue.message, explanation)
            
            try:
                pr_url = github_client.create_pull_request(
                    title=pr_title,
                    body=pr_body,
                    head_branch=branch_name,
                )
                
                # Update issue with PR info
                issue.status = IssueStatus.PR_OPEN
                issue.pr_url = pr_url
                issue.pr_branch = branch_name
                
                db.add(Event(
                    issue_id=issue.id,
                    event_type=EventType.PR_CREATED,
                    message="Pull request created: {}".format(pr_url),
                ))
                db.commit()
                
                logger.info("Successfully created PR: {}".format(pr_url))
                return {
                    "success": True,
                    "message": "Fix applied and PR created: {}".format(pr_url),
                    "pr_url": pr_url,
                }
                
            except Exception as e:
                error_msg = "Failed to create pull request: {}".format(str(e))
                logger.error(error_msg)
                issue.status = IssueStatus.NEW
                db.add(Event(
                    issue_id=issue.id,
                    event_type=EventType.ERROR,
                    message=error_msg,
                ))
                db.commit()
                return {"success": False, "message": error_msg}
            
        except Exception as e:
            logger.error("Unexpected error fixing issue: {}".format(e))
            db.rollback()
            return {"success": False, "message": "Unexpected error: {}".format(str(e))}


# Global service instance
fixer_service = FixerService()