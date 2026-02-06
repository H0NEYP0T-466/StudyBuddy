import io
import re
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import markdown


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
        """Export content to PDF with optional watermark."""
        output = io.BytesIO()
        doc = SimpleDocTemplate(output, pagesize=letter)
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor='#333333',
            spaceAfter=30,
            alignment=TA_CENTER
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
                    para = Paragraph(line[2:], styles['Heading1'])
                elif line.startswith('## '):
                    para = Paragraph(line[3:], styles['Heading2'])
                elif line.startswith('### '):
                    para = Paragraph(line[4:], styles['Heading3'])
                else:
                    # Convert markdown to HTML safely
                    # Escape special XML characters first
                    line_safe = escape(line)
                    
                    # Convert **text** to <b>text</b> (greedy match for pairs)
                    line_safe = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', line_safe)
                    # Convert __text__ to <b>text</b>
                    line_safe = re.sub(r'__(.+?)__', r'<b>\1</b>', line_safe)
                    
                    para = Paragraph(line_safe, styles['BodyText'])
                story.append(para)
                story.append(Spacer(1, 0.1 * inch))
        
        # Watermark
        if add_watermark:
            watermark_style = ParagraphStyle(
                'Watermark',
                parent=styles['Normal'],
                fontSize=10,
                textColor='#999999',
                alignment=TA_CENTER
            )
            story.append(Spacer(1, 0.5 * inch))
            story.append(Paragraph("~honeypot", watermark_style))
        
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
