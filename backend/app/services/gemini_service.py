import os
import google.generativeai as genai_legacy
from app.config import settings

class GeminiService:
    def __init__(self):
        self.api_key = settings.gemini_api_key
        if self.api_key:
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
                        uploaded_file = genai_legacy.upload_file(file_path)
                        contents.append(uploaded_file)
            
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
        prompt = f"""
You are a study notes generator that transforms provided files into **concise short, exam-focused study notes**
## Required Structure
Include sections only if relevant.
- **#  Title** (infer from content - use H1)
- **##  Overview** (1-2 sentences summarizing the main topic)
- **##  Key Takeaways** (5–10 bullet points)
- **##  Concepts** (organized by topic with inline citations like `(page#X)` or `(slide#X)`)
- **##  Formulas/Definitions** (if applicable — use LaTeX only for complex formulas)
- **##  Procedures/Algorithms** (if applicable — numbered steps)
- **##  Examples** (if applicable — concrete examples with explanations)
- **##  Questions for Review**  MANDATORY (3–9 exam-style questions)
- **##  Answers**  MANDATORY (brief answers to all questions above)
- **##  Teach It Simply**  MANDATORY LAST SECTION (child-friendly explanations with 2–5 real-world analogies)
---
### 8. Citations
- Include inline citations as `(page#X)` or `(slide#X)` when referencing source material
- Place citations immediately after the relevant content
### 9. Importance Markers
- Mark especially important topics with `**(IMP**)` after the heading
- Example: `## Thermodynamics Laws **(IMP*)**`
---
{text}
---
**Now generate concise and too the points, structured study notes following all rules above."""     
        return await self.generate_text(prompt, model_name, file_paths)

gemini_service = GeminiService()
