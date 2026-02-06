import os
import google.generativeai as genai_legacy
from app.config import settings

class GeminiService:
    def __init__(self):
        self.api_key = settings.gemini_api_key
        if self.api_key:
            # Configure legacy API for file uploads and generation
            genai_legacy.configure(api_key=self.api_key)
        else:
            self.api_key = None

    async def generate_text(
        self, 
        prompt: str, 
        model_name: str = "gemini-2.5-flash",
        file_paths: list = None
    ) -> str:
        if not self.api_key:
            return "Error: Gemini API key not configured"
        
        try:
            contents = [prompt]
            
            if file_paths:
                for file_path in file_paths:
                    if os.path.exists(file_path):
                        # Upload file using the legacy API
                        uploaded_file = genai_legacy.upload_file(file_path)
                        contents.append(uploaded_file)
            
            # Use legacy API for generation
            model = genai_legacy.GenerativeModel(model_name)
            response = await model.generate_content_async(contents)
            
            if response and response.text:
                return response.text
            return "AI returned an empty response."

        except Exception as e:
            print(f"Gemini Service Error: {str(e)}")
            return f"Error generating with Gemini: {str(e)}"

    async def generate_notes(
        self, 
        text: str, 
        model_name: str = "gemini-2.5-flash",
        file_paths: list = None
    ) -> str:
        """Generate structured study notes in Markdown format."""
        prompt = f"""Generate detailed, structured study notes from the following content.

Format your notes in Markdown with:
- Clear headings and subheadings (use # for H1, ## for H2, ### for H3)
- Bullet points for key concepts
- Bold (**text**) for important terms
- Code blocks (```language```) where applicable
- Organized sections
- LaTeX for mathematical expressions (use $ for inline and $$ for block equations)

Content:
{text}

Generate notes:"""
        
        return await self.generate_text(prompt, model_name, file_paths)

gemini_service = GeminiService()