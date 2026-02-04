import google.generativeai as genai
from typing import Optional, List, Dict
from app.config import settings
import os


class GeminiService:
    def __init__(self):
        self.api_key = settings.gemini_api_key
        if self.api_key:
            genai.configure(api_key=self.api_key)
    
    async def generate_text(
        self, 
        prompt: str, 
        model_name: str = "gemini-2.0-flash-exp",
        file_paths: Optional[List[str]] = None,
        chat_history: Optional[List[Dict]] = None
    ) -> str:
        """Generate text using Gemini models."""
        if not self.api_key:
            return "Error: Gemini API key not configured"
        
        try:
            # Map model names
            model_mapping = {
                "gemini-2.5-pro": "gemini-2.0-flash-exp",  # Using available model
                "gemini-2.5-flash": "gemini-2.0-flash-exp",
                "gemini-pro": "gemini-2.0-flash-exp"
            }
            
            actual_model = model_mapping.get(model_name, model_name)
            model = genai.GenerativeModel(actual_model)
            
            # Handle file uploads
            uploaded_files = []
            if file_paths:
                for file_path in file_paths:
                    if os.path.exists(file_path):
                        uploaded_file = genai.upload_file(file_path)
                        uploaded_files.append(uploaded_file)
            
            # Build content
            if uploaded_files:
                content = [prompt] + uploaded_files
            else:
                content = prompt
            
            # Generate response
            if chat_history:
                # Use chat mode
                chat = model.start_chat(history=[])
                response = chat.send_message(content)
            else:
                response = model.generate_content(content)
            
            return response.text
            
        except Exception as e:
            return f"Error generating with Gemini: {str(e)}"
    
    async def generate_notes(
        self, 
        text: str, 
        model_name: str = "gemini-2.0-flash-exp",
        file_paths: Optional[List[str]] = None
    ) -> str:
        """Generate structured study notes."""
        prompt = f"""You are an expert note-taking assistant. Generate comprehensive, well-structured study notes from the following content.

Format your notes in Markdown with:
- Clear headings and subheadings
- Bullet points for key concepts
- Bold for important terms
- Code blocks where applicable
- Organized sections

Content:
{text}

Generate detailed, structured notes:"""
        
        return await self.generate_text(prompt, model_name, file_paths)


# Global instance
gemini_service = GeminiService()
