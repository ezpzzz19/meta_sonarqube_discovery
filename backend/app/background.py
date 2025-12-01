"""
Background polling service for automatically syncing and fixing issues.
"""
import asyncio
import logging

from app.config import settings
from app.fixer_service import fixer_service
from app.database import get_db_context
from app.models import Issue, IssueStatus

logger = logging.getLogger(__name__)

async def sync_issues():
    with get_db_context() as db:
        new_count = await fixer_service.sync_sonarqube_issues(db)
        logger.info(f"Synced {new_count} new issues")

async def fix_issues():
    with get_db_context() as db:
        new_issues = db.query(Issue).filter(
            Issue.status == IssueStatus.NEW
        ).limit(10).all()  # Limit to 10 at a time to avoid overwhelming

        logger.info(f"Found {len(new_issues)} NEW issues to fix")

        for issue in new_issues:
            logger.info(f"Auto-fixing issue {issue.sonarqube_issue_key}...")
            try:
                result = await fixer_service.attempt_fix(str(issue.id), db)
                if result.get("success"):
                    logger.info(f"Successfully fixed issue {issue.sonarqube_issue_key}")
                else:
                    logger.warning(f"Failed to fix issue {issue.sonarqube_issue_key}: {result.get('message')}")
            except Exception as e:
                logger.error(f"Error fixing issue {issue.sonarqube_issue_key}: {e}")

            # Small delay between fixes to avoid rate limiting
            await asyncio.sleep(5)

async def update_pr_statuses():
    with get_db_context() as db:
        updated_count = await fixer_service.update_pr_merge_status(db)
        logger.info(f"Updated {updated_count} PR merge statuses")

async def start_background_poller():
    """
    Background task that periodically:
    1. Syncs issues from SonarQube
    2. Checks PR merge status for open PRs
    3. Attempts to fix NEW issues if auto_fix is enabled
    """
    logger.info("Background poller started")

    while True:
        try:
            logger.info("Running background sync...")

            # Sync issues from SonarQube
            await sync_issues()

            # Check PR merge status
            await update_pr_statuses()

            # If auto-fix is enabled, attempt to fix NEW issues
            if settings.auto_fix:
                await fix_issues()

        except Exception as e:
            logger.error(f"Error in background poller: {e}")

        # Wait before next poll
        logger.info(f"Sleeping for {settings.poll_interval_seconds} seconds...")
        await asyncio.sleep(settings.poll_interval_seconds)