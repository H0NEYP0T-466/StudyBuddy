import io
import re
import logging
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import markdown

# Configuration
WATERMARK_TEXT = "~honeypot"

# Setup logging
logger = logging.getLogger(__name__)

# Register Unicode-compatible fonts for better emoji support
try:
    pdfmetrics.registerFont(TTFont('DejaVuSans', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuSans-Oblique', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf'))
    FONTS_REGISTERED = True
except Exception as e:
    logger.warning(f"Could not register DejaVu fonts: {e}")
    FONTS_REGISTERED = False


class WatermarkCanvas(canvas.Canvas):
    """Custom canvas to add watermark on every page."""
    
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []
        
    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()
        
    def save(self):
        # Add watermark to each page
        num_pages = len(self.pages)
        for page_num, page in enumerate(self.pages, 1):
            self.__dict__.update(page)
            self.add_watermark()
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
        
    def add_watermark(self):
        """Add watermark at bottom right of page."""
        self.saveState()
        # Use registered font if available, otherwise fallback to Helvetica
        watermark_font = 'DejaVuSans' if FONTS_REGISTERED else 'Helvetica'
        self.setFont(watermark_font, 10)
        self.setFillColorRGB(0.6, 0.6, 0.6)  # Gray color
        # Position at bottom right (with some padding)
        self.drawRightString(letter[0] - 0.5*inch, 0.5*inch, WATERMARK_TEXT)
        self.restoreState()


class ExportService:
    
    @staticmethod
    def export_to_markdown(content: str, title: str) -> io.BytesIO:
        """Export content to Markdown file."""
        output = io.BytesIO()
        markdown_content = f"# {title}\n\n{content}"
        output.write(markdown_content.encode('utf-8'))
        output.seek(0)
        return output
    
    @staticmethod
    def export_to_pdf(content: str, title: str, add_watermark: bool = True) -> io.BytesIO:
        """Export content to PDF with watermark on every page and emoji support."""
        output = io.BytesIO()
        
        # Use custom canvas for watermark on every page
        doc = SimpleDocTemplate(
            output, 
            pagesize=letter,
            canvasmaker=WatermarkCanvas if add_watermark else canvas.Canvas
        )
        
        # Styles - Use DejaVu Sans for better Unicode/emoji support
        styles = getSampleStyleSheet()
        
        # Choose font based on availability
        base_font = 'DejaVuSans' if FONTS_REGISTERED else 'Helvetica'
        bold_font = 'DejaVuSans-Bold' if FONTS_REGISTERED else 'Helvetica-Bold'
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontName=base_font,
            fontSize=24,
            textColor='#333333',
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading1_style = ParagraphStyle(
            'CustomHeading1',
            parent=styles['Heading1'],
            fontName=bold_font,
            fontSize=18,
        )
        
        heading2_style = ParagraphStyle(
            'CustomHeading2',
            parent=styles['Heading2'],
            fontName=bold_font,
            fontSize=14,
        )
        
        heading3_style = ParagraphStyle(
            'CustomHeading3',
            parent=styles['Heading3'],
            fontName=bold_font,
            fontSize=12,
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontName=base_font,
            fontSize=11,
        )
        
        # Build document
        story = []
        
        # Title
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 0.2 * inch))
        
        # Content - split by lines and add paragraphs
        lines = content.split('\n')
        for line in lines:
            if line.strip():
                # Simple markdown to HTML conversion for basic formatting
                if line.startswith('# '):
                    line_text = line[2:]
                    line_safe = escape(line_text)
                    para = Paragraph(line_safe, heading1_style)
                elif line.startswith('## '):
                    line_text = line[3:]
                    line_safe = escape(line_text)
                    para = Paragraph(line_safe, heading2_style)
                elif line.startswith('### '):
                    line_text = line[4:]
                    line_safe = escape(line_text)
                    para = Paragraph(line_safe, heading3_style)
                else:
                    # Convert markdown to HTML safely
                    # Escape special XML characters but preserve Unicode characters (including emojis)
                    line_safe = escape(line)
                    
                    # Important: Process bold (**/__) before italic (*/_) to avoid conflicts
                    # Convert **text** to <b>text</b> (non-greedy match for pairs)
                    line_safe = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', line_safe)
                    # Convert __text__ to <b>text</b>
                    line_safe = re.sub(r'__(.+?)__', r'<b>\1</b>', line_safe)
                    # Convert *text* to <i>text</i>
                    line_safe = re.sub(r'\*(.+?)\*', r'<i>\1</i>', line_safe)
                    # Convert _text_ to <i>text</i>
                    line_safe = re.sub(r'_(.+?)_', r'<i>\1</i>', line_safe)
                    
                    # Use UTF-8 encoding to support emojis
                    para = Paragraph(line_safe, body_style)
                story.append(para)
                story.append(Spacer(1, 0.1 * inch))
        
        doc.build(story)
        output.seek(0)
        return output
    
    @staticmethod
    def export_to_docx(content: str, title: str) -> io.BytesIO:
        """Export content to DOCX file."""
        output = io.BytesIO()
        doc = Document()
        
        # Title
        title_para = doc.add_heading(title, level=0)
        title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Content
        lines = content.split('\n')
        for line in lines:
            if line.strip():
                if line.startswith('# '):
                    doc.add_heading(line[2:], level=1)
                elif line.startswith('## '):
                    doc.add_heading(line[3:], level=2)
                elif line.startswith('### '):
                    doc.add_heading(line[4:], level=3)
                else:
                    # Handle bold text (simple implementation)
                    p = doc.add_paragraph()
                    parts = line.split('**')
                    for i, part in enumerate(parts):
                        if i % 2 == 0:
                            p.add_run(part)
                        else:
                            p.add_run(part).bold = True
        
        doc.save(output)
        output.seek(0)
        return output


# Global instance
export_service = ExportService()
