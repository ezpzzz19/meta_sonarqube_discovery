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
        prompt = self._build_prompt(
            issue_description=issue_description,
            rule=rule,
            severity=severity,
            file_path=file_path,
            file_content=file_content,
            line_number=line_number,
        )
        
        try:
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
                temperature=0.3,
            )
            
            content = response.choices[0].message.content
            
            if not content:
                return {
                    "success": False,
                    "fixed_content": "",
                    "explanation": "AI returned empty response",
                }
            
            fixed_content = self._extract_fixed_content(content, file_content)
            explanation = self._extract_explanation(content)
            
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
    
    # ... other methods ...

    def _extract_fixed_content(self, response: str, original_content: str) -> str:
        fixed_content = original_content  # Fallback to original
        if "