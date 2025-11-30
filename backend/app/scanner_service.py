"""
Scanner service for running SonarQube analysis on repositories.
"""
import subprocess
import logging
from typing import Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)


class ScannerService:
    """Service to run SonarQube scanner on repositories."""
    
    @staticmethod
    def scan_repository(repo_owner: str = None, repo_name: str = None) -> Dict[str, Any]:
        """
        Run SonarQube scanner on a repository.
        
        Args:
            repo_owner: GitHub repository owner (uses config if not provided)
            repo_name: GitHub repository name (uses config if not provided)
        
        Returns:
            Dict with success status and message
            
        Note:
            - For configured repo: Full access (scan + create PRs)
            - For external repos: Read-only mode (scan only, no PR creation)
        """
        # Use configured values if not provided
        owner = repo_owner or settings.github_repo_owner
        name = repo_name or settings.github_repo_name
        
        # Check if this is an external repo (not the configured one)
        is_external_repo = (
            repo_owner is not None and 
            repo_name is not None and 
            (owner != settings.github_repo_owner or name != settings.github_repo_name)
        )
        
        try:
            logger.info(f"Starting SonarQube scan for {owner}/{name}")
            
            # Generate a project key for custom repos
            project_key = settings.sonarqube_project_key
            if repo_owner and repo_name:
                project_key = f"{owner}-{name}".replace("/", "-").replace("_", "-")
            
            # Run the scan script
            result = subprocess.run(
                ["/app/scan_repo.sh"],
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
                env={
                    "GITHUB_TOKEN": settings.github_token,
                    "GITHUB_REPO_OWNER": owner,
                    "GITHUB_REPO_NAME": name,
                    "GITHUB_DEFAULT_BRANCH": settings.github_default_branch,
                    "SONARQUBE_URL": settings.sonarqube_url,
                    "SONARQUBE_TOKEN": settings.sonarqube_token,
                    "SONARQUBE_PROJECT_KEY": project_key,
                    "PATH": subprocess.os.environ.get("PATH", ""),
                }
            )
            
            if result.returncode == 0:
                logger.info("SonarQube scan completed successfully")
                message = f"Repository {owner}/{name} scanned successfully"
                if repo_owner and repo_name:
                    message += f"\nProject key: {project_key}"
                
                if is_external_repo:
                    message += "\n\n⚠️ Note: This is an external repository. You can view issues but cannot create PRs (no write access)."
                
                return {
                    "success": True,
                    "message": message,
                    "output": result.stdout,
                    "project_url": f"{settings.sonarqube_url}/dashboard?id={project_key}",
                    "is_external": is_external_repo
                }
            else:
                logger.error(f"SonarQube scan failed: {result.stderr}")
                return {
                    "success": False,
                    "message": "Scan failed",
                    "error": result.stderr,
                    "output": result.stdout
                }
                
        except subprocess.TimeoutExpired:
            logger.error("SonarQube scan timed out")
            return {
                "success": False,
                "message": "Scan timed out after 10 minutes"
            }
        except Exception as e:
            logger.error(f"Error running SonarQube scan: {str(e)}")
            return {
                "success": False,
                "message": f"Error running scan: {str(e)}"
            }


scanner_service = ScannerService()
