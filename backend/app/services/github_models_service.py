import httpx
from typing import Optional, List, Dict
from app.config import settings


class GitHubModelsService:
    def __init__(self):
        self.api_key = settings.github_token
        self.base_url = "https://models.inference.ai.azure.com/chat/completions"
    
    async def generate_text(
        self, 
        prompt: str, 
        model_name: str = "gpt-4o-mini",
        chat_history: Optional[List[Dict]] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate text using GitHub Models."""
        if not self.api_key:
            return "Error: GitHub token not configured"
        
        try:
            # Prepare messages
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            if chat_history:
                messages.extend(chat_history)
            
            messages.append({"role": "user", "content": prompt})
            
            # Make API call
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model_name,
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 4000
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    return f"Error: GitHub Models API returned {response.status_code} - {response.text}"
                    
        except Exception as e:
            return f"Error generating with GitHub Models: {str(e)}"


# Global instance
github_models_service = GitHubModelsService()
