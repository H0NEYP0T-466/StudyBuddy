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

Transform provided files into clean, structured study notes using **Markdown only**.

## 🏗️ Structure
Include sections only if relevant from source content, except mandatory sections marked with ⭐:

* # 📑 Title (infer from content)
* ## 🌐 Overview (3-6 sentences)
* ## ⭐ Key Takeaways (5-10 bullets)
* ## 📂 Concepts (organize by topic with inline citations like (page#X))
* ## ➕ Formulas/Definitions (if applicable - use LaTeX format)
* ## ⚙️ Procedures/Algorithms (if applicable - numbered steps)
* ## 💡 Examples (if applicable)
* ## ❓ Questions for Review — ⭐ MANDATORY (3-9 questions)
* ## ✅ Answers — ⭐ MANDATORY (brief answers to all questions)
* ## 🍼 Teach It Simply — ⭐ MANDATORY LAST SECTION (child-friendly explanations with 2-5 real-world analogies)

## 🎯 Rules
* Your **goal is NOT to make the notes long** — focus on delivering *concise, clear study notes only*.
* Discard any unnecessary or irrelevant material from the provided source.
* **Make the notes exam-focused:** after the heading of a topic, if the topic is especially important for exams, add **(IMP*)** right after the heading.
* Use H1/H2/H3 headings only.
* **All headings and bullet points must include relevant emojis**
* Bold key terms on first mention
* Academic tone (except "Teach It Simply" section)
* Include inline source citations: (slide#X) or (page#X)
* No invented facts — use only content from provided files.

## 📐 LaTeX Formatting Rules (CRITICAL for Formulas/Definitions section)
* **ALWAYS use proper LaTeX delimiters with CORRECT formatting:**
  - For **inline math** (within a sentence): Use single dollar signs like `$formula$`
    * Example: "The equation $s = T(r)$ defines the transformation"
  - For **display/block math** (standalone formulas): Use double dollar signs on SEPARATE lines
    * MUST have a blank line before and after the formula

* **Examples of CORRECT LaTeX formatting:**
  - Inline: "The transformation is $s = T(r)$ or function $g(x,y) = T[f(x,y)]$"
  - Display:
    ```
    Logarithmic transformation (slide#5):
    
    $$s = c \\cdot \\log(1+r)$$
    
    Probability function (slide#8):
    
    $$p(r_k) = \\frac{{n_k}}{{MN}}$$
    ```

* **Use proper LaTeX syntax:**
  - Multiplication: `$c \\cdot r$`
  - Fractions: `$\\frac{{a}}{{b}}$`
  - Superscripts: `$r^\\gamma$`
  - Subscripts: `$r_k$`
  - Greek letters: `$\\gamma$, $\\theta$, $\\alpha$`
  - Integrals: `$\\int_0^r f(x)dx$`
  - Summations: `$\\sum_{{i=1}}^{{n}} x_i$`
  - Square roots: `$\\sqrt{{x^2 + y^2}}$`
  - Cases:
    ```
    $$H(x) = \\begin{{cases}}
    1 & \\text{{if }} x > 0 \\\\
    0 & \\text{{if }} x \\le 0
    \\end{{cases}}$$
    ```

---

## 📄 Source Content:

{text}

---

Now generate comprehensive study notes following all the rules above:"""
        
        return await self.generate_text(prompt, model_name, file_paths)

gemini_service = GeminiService()
