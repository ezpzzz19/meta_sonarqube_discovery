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
        
        return await self._call_and_parse_ai_response(prompt)
    
    async def _call_and_parse_ai_response(self, prompt: str) -> dict:
        """
        Call OpenAI API and parse the response.
        """
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
    
    # ... rest of the class remains the same ...