import httpx
from typing import Optional, List, Dict
from app.config import settings


class LongCatService:
    def __init__(self):
        self.api_key = settings.longcat_api_key
        self.base_url = "https://api.longcat.chat/openai/v1/chat/completions"
    
    async def generate_text(
        self, 
        prompt: str, 
        model_name: str = "longcat-flash-chat",
        chat_history: Optional[List[Dict]] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """Generate text using LongCat models."""
        if not self.api_key:
            return "Error: LongCat API key not configured"
        
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
                    return f"Error: LongCat API returned {response.status_code} - {response.text}"
                    
        except Exception as e:
            return f"Error generating with LongCat: {str(e)}"
    
    async def generate_notes(self, text: str, model_name: str = "longcat-chat") -> str:
        """Generate structured study notes."""
        system_prompt = """You are an expert note-taking assistant. Generate comprehensive, well-structured study notes in Markdown format."""
        
        prompt = f"""Generate detailed, structured study notes from the following content.

Format your notes in Markdown with:
- Clear headings and subheadings
- Bullet points for key concepts
- Bold for important terms
- Code blocks where applicable
- Organized sections

Content:
{text}

Generate notes:"""
        
        return await self.generate_text(prompt, model_name, system_prompt=system_prompt)


# Global instance
longcat_service = LongCatService()
