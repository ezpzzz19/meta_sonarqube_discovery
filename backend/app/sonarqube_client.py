"""
SonarQube API client for fetching issues.
"""
import httpx
from typing import Optional

from app.config import settings


class SonarQubeClient:
    """Client for interacting with SonarQube API."""
    
    def __init__(self):
        self.base_url = settings.sonarqube_url.rstrip("/")
        self.token = settings.sonarqube_token
        self.project_key = settings.sonarqube_project_key
        
    def _get_headers(self) -> dict:
        """Get authentication headers."""
        return {
            "Authorization": f"Bearer {self.token}",
        }
    
    async def get_issues(
        self,
        project_key: Optional[str] = None,
        statuses: Optional[list[str]] = None,
        page: int = 1,
        page_size: int = 100,
    ) -> dict:
        """
        Fetch issues from SonarQube for a given project.
        
        Args:
            project_key: Project key to filter by (defaults to configured project)
            statuses: List of issue statuses to filter by (e.g., ["OPEN", "CONFIRMED"])
            page: Page number (1-indexed)
            page_size: Number of issues per page
            
        Returns:
            Dict with 'issues' list and 'paging' info
        """
        project = project_key or self.project_key
        
        params = {
            "componentKeys": project,
            "p": page,
            "ps": page_size,
        }
        
        if statuses:
            params["statuses"] = ",".join(statuses)
        
        url = f"{self.base_url}/api/issues/search"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=self._get_headers(),
                params=params,
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()
    
    async def get_issue(self, issue_key: str) -> dict:
        """
        Fetch a single issue by its key.
        
        Args:
            issue_key: The SonarQube issue key
            
        Returns:
            Issue data dict
        """
        url = f"{self.base_url}/api/issues/search"
        params = {"issues": issue_key}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=self._get_headers(),
                params=params,
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("issues"):
                return data["issues"][0]
            return {}
    
    def parse_component_path(self, component: str) -> str:
        """
        Parse the component string to extract the file path.
        
        SonarQube component format is typically: projectKey:path/to/file.ext
        
        Args:
            component: Full component string from SonarQube
            
        Returns:
            File path relative to repository root
        """
        if ":" in component:
            parts = component.split(":", 1)
            if len(parts) == 2:
                return parts[1]
        return component


# Global client instance
sonarqube_client = SonarQubeClient()
