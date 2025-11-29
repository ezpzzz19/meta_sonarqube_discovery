"""
AI client for generating code fixes using OpenAI API.
"""
from openai import AsyncOpenAI
from typing import Optional

from app.config import settings


class AIClient:
    """Client for interacting with OpenAI API to generate code fixes."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
    
    async def generate_fix(
        self,
        issue_description: str,
        rule: str,
        severity: str,
        file_path: str,
        file_content: str,
        line_number: Optional[int] = None,
    ) -> dict:
        """
        Generate a code fix for a SonarQube issue.
        
        Args:
            issue_description: Description of the issue from SonarQube
            rule: SonarQube rule that was violated
            severity: Issue severity
            file_path: Path to the file with the issue
            file_content: Current content of the file
            line_number: Line number where the issue occurs (if available)
            
        Returns:
            Dict with:
                - fixed_content: The complete fixed file content
                - explanation: Explanation of what was changed and why
                - success: Boolean indicating if fix was generated
        """
        # Build the prompt
        prompt = self._build_prompt(
            issue_description=issue_description,
            rule=rule,
            severity=severity,
            file_path=file_path,
            file_content=file_content,
            line_number=line_number,
        )
        
        try:
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert software engineer specializing in code quality and security. "
                            "Your task is to fix code issues identified by SonarQube. "
                            "Provide the complete fixed file content and a clear explanation of your changes."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=0.3,  # Lower temperature for more deterministic fixes
            )
            
            # Parse the response
            content = response.choices[0].message.content
            
            if not content:
                return {
                    "success": False,
                    "fixed_content": "",
                    "explanation": "AI returned empty response",
                }
            
            # Split the response into fixed content and explanation
            # Expected format: ```language\n<code>\n```\n\nExplanation: <text>
            fixed_content, explanation = self._parse_ai_response(content, file_content)
            
            return {
                "success": True,
                "fixed_content": fixed_content,
                "explanation": explanation,
            }
            
        except Exception as e:
            return {
                "success": False,
                "fixed_content": "",
                "explanation": f"Error calling AI: {str(e)}",
            }
    
    def _build_prompt(
        self,
        issue_description: str,
        rule: str,
        severity: str,
        file_path: str,
        file_content: str,
        line_number: Optional[int] = None,
    ) -> str:
        """Build the prompt for the AI model."""
        line_info = f" at line {line_number}" if line_number else ""
        
        prompt = f"""I need you to fix a code quality issue detected by SonarQube.

**Issue Details:**
- File: {file_path}
- Rule: {rule}
- Severity: {severity}
- Location: {line_info or "Unknown line"}
- Description: {issue_description}

**Current File Content:**
```
{file_content}
```

**Instructions:**
1. Analyze the issue and understand what needs to be fixed.
2. Provide the COMPLETE fixed file content (not just a diff).
3. Ensure the fix addresses the SonarQube rule violation.
4. Maintain the original code style and formatting.
5. Do not add or remove functionality unrelated to the fix.

**Output Format:**
First, provide the complete fixed file content in a code block.
Then, on a new line, provide a brief explanation starting with "Explanation: " describing what you changed and why.

Example:
```python
# Fixed code here
```

Explanation: Changed X to Y because Z violates the SonarQube rule ABC.
"""
        return prompt
    
    def _parse_ai_response(self, response: str, original_content: str) -> tuple[str, str]:
        """
        Parse the AI response to extract fixed content and explanation.
        
        Args:
            response: Raw AI response
            original_content: Original file content (fallback)
            
        Returns:
            Tuple of (fixed_content, explanation)
        """
        # Try to extract code block
        fixed_content = original_content  # Fallback to original
        explanation = "AI provided a fix."
        
        # Look for code blocks
        if "```" in response:
            parts = response.split("```")
            if len(parts) >= 3:
                # Extract code (skip language identifier on first line if present)
                code_block = parts[1]
                lines = code_block.split("\n")
                if lines[0].strip() and not lines[0].strip().startswith(("#", "//")):
                    # First line might be language identifier, skip it
                    if lines[0].strip() in ["python", "java", "javascript", "typescript", "go", "cpp", "c"]:
                        code_block = "\n".join(lines[1:])
                fixed_content = code_block.strip()
                
                # Extract explanation
                remaining = parts[2] if len(parts) > 2 else ""
                if "Explanation:" in remaining:
                    explanation = remaining.split("Explanation:", 1)[1].strip()
                elif remaining.strip():
                    explanation = remaining.strip()
        
        return fixed_content, explanation


# Global client instance
ai_client = AIClient()
