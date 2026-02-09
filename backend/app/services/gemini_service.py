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
        prompt = f"""# 📘 Study Notes Generator

Transform the provided files into **concise, exam-focused study notes** using **Markdown only**. Notes must be structured for proper PDF rendering.
---
## 🏗️ Structure
Include sections only if relevant, except mandatory sections marked with ⭐:
- # 📑 Title (infer from content)
- ## 🌐 Overview (3–6 sentences)
- ## ⭐ Key Takeaways (5–10 bullets)
- ## 📂 Concepts (organized by topic with inline citations like (page#X))
- ## ➕ Formulas/Definitions (if applicable — use **LaTeX formatting rules**)
- ## ⚙️ Procedures/Algorithms (if applicable — numbered steps)
- ## 💡 Examples (if applicable)
- ## ❓ Questions for Review — ⭐ MANDATORY (3–9 questions)
- ## ✅ Answers — ⭐ MANDATORY (brief answers to all questions)
- ## 🍼 Teach It Simply — ⭐ MANDATORY LAST SECTION (child-friendly explanations with 2–5 real-world analogies)
---
## 🎯 Rules for PDF Notes
1. **Headings:** Use only H1/H2/H3 (`#`, `##`, `###`).  
   - H1: 28pt, center-aligned, bold  
   - H2: 20pt, bold, bottom border  
   - H3: 16pt, bold
2. **Text Formatting:**  
   - Bold: `**text**`  
   - Italic: `*text*` or `_text_`  
   - Bold + Italic: `***text***`  
   - Inline Code: `` `code` `` (Courier font)
3. **Lists:**  
   - Unordered: `- item` or `* item`  
   - Ordered: `1. item`, `2. item`  
   - ❌ **No nested lists**
4. **Mathematics:**  
   - Inline math: `$formula$`  
   - Block math: `$$formula$$` on separate lines with blank lines before & after  
   - Correct LaTeX syntax required (multiplication `\\cdot`, fractions `\\frac{{a}}{{b}}`, superscripts `^`, subscripts `_`, Greek letters, integrals, summations, square roots, cases)
5. **Horizontal Rules:** Use `---`, `***`, or `___`
6. **Paragraphs:**  
   - Justified alignment  
   - Leave blank lines between paragraphs
7. **Emojis:**  
   - ❌ Do not use colorful emojis  
   - ✅ Use text-based alternatives in bold brackets:  
     - **[Important]**, **[Key Point]**, **[Note]**, **[Correct]**, **[Wrong]**, **[Memo]**, **[Idea]**, **[Analysis]**
8. **Content Rules:**  
   - Bold key terms on first mention  
   - Academic tone (except "Teach It Simply")  
   - Include inline citations `(slide#X)` or `(page#X)`  
   - Focus on clarity and conciseness, discard irrelevant content  
   - Mark especially important topics with **(IMP*)** after the heading
---
## 📐 LaTeX Formatting Rules (Formulas/Definitions Section)
- Inline math: `$s = T(r)$`  
- Multiplication: `$c \cdot r$`  
- Fractions: `$\\frac{{a}}{{b}}$`  
- Superscripts: `$r^\\gamma$`  
- Subscripts: `$r_k$`  
- Greek letters: `$\\gamma$, `$\\theta$`  
- Integrals: `$\\int_0^r f(x)dx$`  
- Summations: `$\\sum_{{i=1}}^{{n}} x_i$`  
- Square roots: `$\\sqrt{{x^2 + y^2}}$`  
{text}
---
Now generate **concise, structured study notes** following all rules above, fully compatible with PDF export."""
        
        return await self.generate_text(prompt, model_name, file_paths)

gemini_service = GeminiService()
