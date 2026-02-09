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
You are a study notes generator that transforms provided files into **concise, exam-focused study notes** using **Markdown only**. Notes must be structured for proper PDF rendering.
---
## Required Structure
Include sections only if relevant.
- **#  Title** (infer from content - use H1)
- **##  Overview** (3–6 sentences summarizing the main topic)
- **##  Key Takeaways**  MANDATORY (5–10 bullet points)
- **##  Concepts** (organized by topic with inline citations like `(page#X)` or `(slide#X)`)
- **##  Formulas/Definitions** (if applicable — use LaTeX only for complex formulas)
- **##  Procedures/Algorithms** (if applicable — numbered steps)
- **##  Examples** (if applicable — concrete examples with explanations)
- **##  Questions for Review**  MANDATORY (3–9 exam-style questions)
- **##  Answers**  MANDATORY (brief answers to all questions above)
- **##  Teach It Simply**  MANDATORY LAST SECTION (child-friendly explanations with 2–5 real-world analogies)
---
##  Critical Formatting Rules
### 1. Heading Levels (STRICT)
- **ONLY use three heading levels:**
  - `#` for the main title (H1)
  - `##` for major sections (H2)
  - `###` for subsections (H3)
- ** NEVER use `####` (H4) or deeper levels**
- ** Always use `##` for all major section headings**
### 2. Text Formatting
- **Bold:** `**text**` (for key terms on first mention)
- **Italic:** `*text*` or `_text*` (for emphasis)
- **Bold + Italic:** `***text***`
- **Inline Code:** `` `code` `` (for technical terms, variables, or code snippets)
### 3. Lists
- **Unordered lists:** Use `- item` or `* item`
- **Ordered lists:** Use `1. item`, `2. item`
- ** Do NOT create nested lists** (keep all lists flat)
### 4. Mathematics & LaTeX (IMPORTANT)
**Use LaTeX ONLY for complex mathematical formulas. Do NOT use LaTeX for:**
- Simple variables (write `R`, `x`, `y` instead of `$R$`, `$x$`, `$y$`)
- Simple arithmetic (write `3 + 3` or `a + b` instead of `$3 + 3$` or `$a + b$`)
- Simple expressions that are readable as plain text
**DO use LaTeX for:**
- **Inline complex math:** `$formula$` (e.g., `$\frac{{a}}{{b}}$`, `$x^2 + y^2$`)
- **Block math:** Use `$$formula$$` on separate lines with blank lines before and after
**LaTeX Syntax Reference:**
- Fractions: `\frac{{numerator}}{{denominator}}`
- Multiplication: `\cdot` (e.g., `$a \cdot b$`)
- Superscripts: `^` (e.g., `$x^2$`)
- Subscripts: `_` (e.g., `$r_k$`)
- Greek letters: `\alpha`, `\beta`, `\gamma`, `\theta`, etc.
- Integrals: `\int_{{lower}}^{{upper}}` (e.g., `$\int_0^r f(x)dx$`)
- Summations: `\sum_{{i=1}}^{{n}}` (e.g., `$\sum_{{i=1}}^{{n}} x_i$`)
- Square roots: `\sqrt{{expression}}` (e.g., `$\sqrt{{x^2 + y^2}}$`)
- Piecewise functions: Use `\begin{{cases}}...\end{{cases}}`
### 5. Horizontal Rules
- Use `---`, `***`, or `___` to separate major sections
### 6. Paragraphs
- Leave blank lines between paragraphs for proper spacing
- Keep paragraphs concise and focused
### 7. Emojis & Visual Markers
- ** Do NOT use colorful emojis in body content**
- ** Use text-based markers in bold brackets:**
  - `**[Important]**`, `**[Key Point]**`, `**[Note]**`
  - `**[Correct]**`, `**[Wrong]**`
  - `**[Memo]**`, `**[Idea]**`, `**[Analysis]**`
### 8. Citations
- Include inline citations as `(page#X)` or `(slide#X)` when referencing source material
- Place citations immediately after the relevant content
### 9. Importance Markers
- Mark especially important topics with `**(IMP**)` after the heading
- Example: `## Thermodynamics Laws **(IMP*)**`
---
##  Special Section: Teach It Simply
This mandatory final section should:
- Use simple, child-friendly language
- Include 2–5 real-world analogies
- Make complex concepts accessible to beginners
- Use everyday examples and relatable scenarios
- Maintain an encouraging, friendly tone
---
{text}
---
**Now generate concise, structured study notes following all rules above, fully compatible with PDF export.**  
"""     
        return await self.generate_text(prompt, model_name, file_paths)

gemini_service = GeminiService()
