import io
import re
import logging
from playwright.async_api import async_playwright
from markdown2 import markdown
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH

# ==========================
# Configuration
# ==========================
WATERMARK_TEXT = "~honeypot"

logger = logging.getLogger(__name__)

# ==========================
# HTML Template for PDF with MathJax support
# ==========================
def create_html_template(title: str, content_html: str) -> str:
    """
    Create HTML template with CSS styling.
    
    Note: Uses Google Fonts CDN for Noto Sans and Noto Emoji fonts.
    For offline environments, fonts will fall back to system defaults.
    To use local fonts, install Noto fonts on the system or bundle them.
    Watermark is handled via Playwright PDF options, not in HTML.
    """
    
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;700&family=Noto+Emoji&display=swap');
            
            body {{
                font-family: 'Noto Sans', 'Noto Emoji', sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }}
            
            h1 {{
                font-size: 28pt;
                font-weight: 700;
                text-align: center;
                margin-bottom: 30px;
                color: #1a1a1a;
            }}
            
            h2 {{
                font-size: 20pt;
                font-weight: 700;
                margin-top: 20px;
                margin-bottom: 10px;
                color: #2a2a2a;
                border-bottom: 2px solid #e0e0e0;
                padding-bottom: 5px;
            }}
            
            h3 {{
                font-size: 16pt;
                font-weight: 700;
                margin-top: 15px;
                margin-bottom: 8px;
                color: #3a3a3a;
            }}
            
            p {{
                margin: 10px 0;
                text-align: justify;
            }}
            
            code {{
                background-color: #f4f4f4;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
                font-size: 9pt;
            }}
            
            pre {{
                background-color: #f4f4f4;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
                border-left: 4px solid #4CAF50;
            }}
            
            pre code {{
                background-color: transparent;
                padding: 0;
            }}
            
            blockquote {{
                border-left: 4px solid #ccc;
                margin-left: 0;
                padding-left: 20px;
                color: #666;
                font-style: italic;
            }}
            
            ul, ol {{
                margin: 10px 0;
                padding-left: 30px;
            }}
            
            li {{
                margin: 5px 0;
            }}
            
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 15px 0;
            }}
            
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}
            
            th {{
                background-color: #f4f4f4;
                font-weight: 700;
            }}
            
            /* LaTeX styling */
            .math {{
                font-family: 'STIX Two Math', serif;
                font-style: italic;
            }}
            
            /* Emoji support */
            .emoji {{
                font-family: 'Noto Emoji', sans-serif;
            }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        {content_html}
    </body>
    </html>
    """
    
    return html_template


def process_latex(text: str) -> str:
    """Convert LaTeX expressions to HTML with basic rendering."""
    # Handle inline LaTeX: $...$
    text = re.sub(
        r'\$([^\$]+)\$',
        r'<span class="math">\1</span>',
        text
    )
    
    # Handle display LaTeX: $$...$$
    text = re.sub(
        r'\$\$([^\$]+)\$\$',
        r'<div class="math" style="text-align: center; margin: 15px 0;">\1</div>',
        text
    )
    
    return text


def markdown_to_html(content: str) -> str:
    """Convert markdown to HTML with LaTeX support."""
    # Process LaTeX first (before markdown conversion)
    content = process_latex(content)
    
    # Convert markdown to HTML
    html_content = markdown(
        content,
        extras=[
            'fenced-code-blocks',
            'tables',
            'break-on-newline',
            'code-friendly',
            'cuddled-lists',
            'header-ids',
            'strike',
            'task_list'
        ]
    )
    
    return html_content


# ==========================
# Export Service
# ==========================
class ExportService:

    @staticmethod
    def export_to_markdown(content: str, title: str) -> io.BytesIO:
        """Export content as markdown file."""
        output = io.BytesIO()
        md = f"# {title}\n\n{content}"
        output.write(md.encode("utf-8"))
        output.seek(0)
        return output

    @staticmethod
    async def export_to_pdf(content: str, title: str, watermark: bool = True) -> io.BytesIO:
        """Export content as PDF with emoji, markdown, and LaTeX support using Playwright."""
        try:
            # Convert markdown content to HTML
            content_html = markdown_to_html(content)
            
            # Create full HTML document (without watermark in HTML)
            html_doc = create_html_template(title, content_html)
            
            # Generate PDF using Playwright (Chromium)
            output = io.BytesIO()
            
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                
                # Set content and wait for fonts to load
                await page.set_content(html_doc, wait_until='load')
                
                # Wait for fonts to be ready
                await page.evaluate('document.fonts.ready')
                
                # Prepare footer template for watermark
                footer_template = '<div style="font-size: 10pt; color: #999; text-align: right; width: 100%; padding-right: 20px;">~honeypot</div>' if watermark else ''
                
                # Generate PDF with proper settings
                pdf_bytes = await page.pdf(
                    format='A4',
                    print_background=True,
                    margin={
                        'top': '20px',
                        'right': '20px',
                        'bottom': '40px' if watermark else '20px',
                        'left': '20px'
                    },
                    display_header_footer=watermark,
                    footer_template=footer_template if watermark else None
                )
                
                await browser.close()
                
                output.write(pdf_bytes)
            
            output.seek(0)
            logger.info(f"PDF generated successfully for '{title}' using Playwright")
            return output
            
        except Exception as e:
            logger.error(f"PDF generation failed: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def export_to_docx(content: str, title: str) -> io.BytesIO:
        """Export content as DOCX file."""
        output = io.BytesIO()
        doc = Document()

        title_para = doc.add_heading(title, level=0)
        title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Simple paragraph splitting - DOCX doesn't need fancy markdown parsing
        for line in content.split("\n"):
            if not line.strip():
                continue
            doc.add_paragraph(line)

        doc.save(output)
        output.seek(0)
        return output


# Global instance
export_service = ExportService()
