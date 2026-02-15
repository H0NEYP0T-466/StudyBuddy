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
    
    async def format_notes(self, gemini_notes: str, model_name: str = "longcat-flash-lite") -> str:
        """Format Gemini-generated notes with strict formatting rules using LongCat."""
        system_prompt = """You are a markdown formatting expert. Your task is to take provided notes and format them correctly according to specific markdown formatting rules.

##  Critical Formatting Rules
### 1. Heading Levels (STRICT)
- **ONLY use three heading levels:**
  - `#` for the main title (H1)
  - `##` for major sections (H2)
  - `###` for subsections (H3)
- **NEVER use `####` (H4) or deeper levels**
- **Always use `##` for all major section headings**

### 2. Text Formatting
- **Bold:** `**text**` (for key terms on first mention)
- **Italic:** `*text*` or `_text_` (for emphasis)
- **Bold + Italic:** `***text***`
- **Inline Code:** `` `code` `` (for technical terms, variables, or code snippets)

### 3. Lists
- **Unordered lists:** Use `- item` or `* item`
- **Ordered lists:** Use `1. item`, `2. item`
- **Do NOT create nested lists** (keep all lists flat)

### 4. Mathematics & LaTeX (IMPORTANT)
**Use LaTeX ONLY for complex mathematical formulas. Do NOT use LaTeX for:**
- Simple variables (write `R`, `x`, `y` instead of `$R$`, `$x$`, `$y$`)
- Simple arithmetic (write `3 + 3` or `a + b` instead of `$3 + 3$` or `$a + b$`)
- Simple expressions that are readable as plain text

**DO use LaTeX for:**
- **Inline complex math:** `$formula$` (e.g., `$\\frac{{a}}{{b}}$`, `$x^2 + y^2$`)
- **Block math:** Use `$$formula$$` on separate lines with blank lines before and after

**LaTeX Syntax Reference:**
- Fractions: `\\frac{{numerator}}{{denominator}}`
- Multiplication: `\\cdot` (e.g., `$a \\cdot b$`)
- Superscripts: `^` (e.g., `$x^2$`)
- Subscripts: `_` (e.g., `$r_k$`)
- Greek letters: `\\alpha`, `\\beta`, `\\gamma`, `\\theta`, etc.
- Integrals: `\\int_{{lower}}^{{upper}}` (e.g., `$\\int_0^r f(x)dx$`)
- Summations: `\\sum_{{i=1}}^{{n}}` (e.g., `$\\sum_{{i=1}}^{{n}} x_i$`)
- Square roots: `\\sqrt{{expression}}` (e.g., `$\\sqrt{{x^2 + y^2}}$`)
- Piecewise functions: Use `\\begin{{cases}}...\\end{{cases}}`

### 5. Horizontal Rules
- Use `---`, `***`, or `___` to separate major sections

### 6. Paragraphs
- Leave blank lines between paragraphs for proper spacing
- Keep paragraphs concise and focused

### 7. Emojis & Visual Markers
- **Do NOT use colorful emojis in body content**
- **Use text-based markers in bold brackets:**
  - `**[Important]**`, `**[Key Point]**`, `**[Note]**`
  - `**[Correct]**`, `**[Wrong]**`
  - `**[Memo]**`, `**[Idea]**`, `**[Analysis]**`

Format the provided notes according to these rules. Keep all the content but ensure it follows the formatting rules strictly."""
        
        prompt = f"""Please format the following notes according to the critical formatting rules provided in the system prompt:

{gemini_notes}

Return the properly formatted notes:"""
        
        return await self.generate_text(prompt, model_name, system_prompt=system_prompt)


# Global instance
longcat_service = LongCatService()
