"""
GitHub API client for fetching code and creating pull requests.
"""
from github import Github, GithubException
from github.Repository import Repository
from typing import Optional
import base64

from app.config import settings


class GitHubClient:
    """Client for interacting with GitHub API."""
    
    def __init__(self):
        self.token = settings.github_token
        self.repo_full_name = settings.github_repo_full_name
        self.default_branch = settings.github_default_branch
        self._gh = Github(self.token)
        self._repo: Optional[Repository] = None
    
    @property
    def repo(self) -> Repository:
        """Get the repository object (cached)."""
        if self._repo is None:
            self._repo = self._gh.get_repo(self.repo_full_name)
        return self._repo
    
    def get_file_content(
        self,
        file_path: str,
        ref: Optional[str] = None,
    ) -> tuple[str, str]:
        """
        Fetch file content from GitHub.
        
        Args:
            file_path: Path to file in repository
            ref: Git reference (branch, tag, commit). Defaults to default branch.
            
        Returns:
            Tuple of (content as string, sha of the file)
        """
        ref = ref or self.default_branch
        
        try:
            contents = self.repo.get_contents(file_path, ref=ref)
            
            # Handle case where contents might be a list
            if isinstance(contents, list):
                raise ValueError(f"Path {file_path} is a directory, not a file")
            
            # Decode content
            if contents.encoding == "base64":
                content = base64.b64decode(contents.content).decode("utf-8")
            else:
                content = contents.decoded_content.decode("utf-8")
            
            return content, contents.sha
            
        except GithubException as e:
            raise Exception(f"Failed to fetch file {file_path}: {e}")
    
    def create_branch(self, branch_name: str, from_branch: Optional[str] = None) -> str:
        """
        Create a new branch.
        
        Args:
            branch_name: Name of the new branch
            from_branch: Source branch to branch from. Defaults to default branch.
            
        Returns:
            SHA of the branch head
        """
        from_branch = from_branch or self.default_branch
        
        # Get the source branch reference
        source_ref = self.repo.get_git_ref(f"heads/{from_branch}")
        source_sha = source_ref.object.sha
        
        # Create new branch
        try:
            new_ref = self.repo.create_git_ref(
                ref=f"refs/heads/{branch_name}",
                sha=source_sha,
            )
            return new_ref.object.sha
        except GithubException as e:
            if e.status == 422:  # Branch already exists
                # Get existing branch
                ref = self.repo.get_git_ref(f"heads/{branch_name}")
                return ref.object.sha
            raise
    
    def update_file(
        self,
        file_path: str,
        content: str,
        commit_message: str,
        branch: str,
        sha: Optional[str] = None,
    ) -> str:
        """
        Update a file in the repository.
        
        Args:
            file_path: Path to file in repository
            content: New file content
            commit_message: Commit message
            branch: Branch to commit to
            sha: Current SHA of the file (required for updates)
            
        Returns:
            Commit SHA
        """
        try:
            result = self.repo.update_file(
                path=file_path,
                message=commit_message,
                content=content,
                sha=sha,
                branch=branch,
            )
            return result["commit"].sha
        except GithubException as e:
            raise Exception(f"Failed to update file {file_path}: {e}")
    
    def create_pull_request(
        self,
        title: str,
        body: str,
        head_branch: str,
        base_branch: Optional[str] = None,
    ) -> str:
        """
        Create a pull request.
        
        Args:
            title: PR title
            body: PR description
            head_branch: Source branch (the branch with changes)
            base_branch: Target branch. Defaults to default branch.
            
        Returns:
            URL of the created pull request
        """
        base_branch = base_branch or self.default_branch
        
        try:
            pr = self.repo.create_pull(
                title=title,
                body=body,
                head=head_branch,
                base=base_branch,
            )
            return pr.html_url
        except GithubException as e:
            raise Exception(f"Failed to create pull request: {e}")
    
    def get_pr_status(self, pr_number: int) -> dict:
        """
        Get the status of a pull request.
        
        Args:
            pr_number: Pull request number
            
        Returns:
            Dict with PR status information
        """
        try:
            pr = self.repo.get_pull(pr_number)
            
            # Get commit statuses
            commit = pr.head.sha
            statuses = self.repo.get_commit(commit).get_statuses()
            
            # Get combined status
            combined_status = self.repo.get_commit(commit).get_combined_status()
            
            return {
                "state": pr.state,
                "merged": pr.merged,
                "mergeable": pr.mergeable,
                "ci_state": combined_status.state,  # pending, success, failure
                "statuses": [
                    {
                        "context": s.context,
                        "state": s.state,
                        "description": s.description,
                    }
                    for s in statuses
                ],
            }
        except GithubException as e:
            raise Exception(f"Failed to get PR status: {e}")


# Global client instance
github_client = GitHubClient()
