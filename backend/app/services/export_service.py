import io
import re
import logging
from markdown2 import markdown
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Preformatted
from reportlab.lib import colors
from reportlab.pdfgen import canvas

# ==========================
# Configuration
# ==========================
WATERMARK_TEXT = "~honeypot"

logger = logging.getLogger(__name__)

# ==========================
# ReportLab PDF Utilities
# ==========================

class WatermarkCanvas(canvas.Canvas):
    """Custom canvas class to add watermark to PDF pages."""
    def __init__(self, *args, **kwargs):
        self.add_watermark = kwargs.pop('add_watermark', False)
        canvas.Canvas.__init__(self, *args, **kwargs)
    
    def showPage(self):
        """Override to add watermark before showing page."""
        if self.add_watermark:
            self.saveState()
            self.setFont('Helvetica', 10)
            self.setFillColor(colors.lightgrey)
            # Add watermark at bottom right
            self.drawRightString(
                A4[0] - 20,
                20,
                WATERMARK_TEXT
            )
            self.restoreState()
        canvas.Canvas.showPage(self)


def create_styles():
    """Create custom paragraph styles for PDF."""
    styles = getSampleStyleSheet()
    
    # Title style
    styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=styles['Title'],
        fontSize=28,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))
    
    # Heading 2 style
    styles.add(ParagraphStyle(
        name='CustomHeading2',
        parent=styles['Heading2'],
        fontSize=20,
        textColor=colors.HexColor('#2a2a2a'),
        spaceAfter=10,
        spaceBefore=20,
        fontName='Helvetica-Bold',
        borderWidth=0,
        borderPadding=5,
        borderColor=colors.HexColor('#e0e0e0'),
        borderRadius=0,
    ))
    
    # Heading 3 style
    styles.add(ParagraphStyle(
        name='CustomHeading3',
        parent=styles['Heading3'],
        fontSize=16,
        textColor=colors.HexColor('#3a3a3a'),
        spaceAfter=8,
        spaceBefore=15,
        fontName='Helvetica-Bold'
    ))
    
    # Body text style
    styles.add(ParagraphStyle(
        name='CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        textColor=colors.HexColor('#333333'),
        alignment=TA_JUSTIFY,
        spaceAfter=10,
        fontName='Helvetica'
    ))
    
    # Code style
    styles.add(ParagraphStyle(
        name='CustomCode',
        parent=styles['Code'],
        fontSize=9,
        fontName='Courier',
        textColor=colors.black,
        backColor=colors.HexColor('#f4f4f4'),
        leftIndent=10,
        rightIndent=10,
        spaceAfter=10,
        spaceBefore=10
    ))
    
    return styles


def parse_markdown_to_reportlab(content: str, styles) -> list:
    """
    Parse markdown content and convert to ReportLab flowables.
    Supports headings, paragraphs, bold, italic, code blocks, and lists.
    """
    elements = []
    lines = content.split('\n')
    i = 0
    in_code_block = False
    code_lines = []
    in_list = False
    list_items = []
    
    while i < len(lines):
        line = lines[i]
        
        # Handle code blocks
        if line.strip().startswith('```'):
            if in_code_block:
                # End of code block
                code_text = '\n'.join(code_lines)
                elements.append(Preformatted(code_text, styles['CustomCode']))
                elements.append(Spacer(1, 0.2*inch))
                code_lines = []
                in_code_block = False
            else:
                # Start of code block
                in_code_block = True
            i += 1
            continue
        
        if in_code_block:
            code_lines.append(line)
            i += 1
            continue
        
        # Handle headings
        if line.startswith('# '):
            if in_list:
                elements.extend(list_items)
                list_items = []
                in_list = False
            text = line[2:].strip()
            elements.append(Paragraph(text, styles['CustomTitle']))
            elements.append(Spacer(1, 0.3*inch))
        elif line.startswith('## '):
            if in_list:
                elements.extend(list_items)
                list_items = []
                in_list = False
            text = line[3:].strip()
            elements.append(Paragraph(text, styles['CustomHeading2']))
            elements.append(Spacer(1, 0.2*inch))
        elif line.startswith('### '):
            if in_list:
                elements.extend(list_items)
                list_items = []
                in_list = False
            text = line[4:].strip()
            elements.append(Paragraph(text, styles['CustomHeading3']))
            elements.append(Spacer(1, 0.15*inch))
        # Handle lists
        elif line.strip().startswith('- ') or line.strip().startswith('* '):
            text = line.strip()[2:].strip()
            text = format_inline_markdown(text)
            list_items.append(Paragraph(f"• {text}", styles['CustomBody']))
            in_list = True
        elif line.strip().startswith(('1. ', '2. ', '3. ', '4. ', '5. ', '6. ', '7. ', '8. ', '9. ')):
            # Numbered list
            match = re.match(r'^(\d+)\.\s+(.+)', line.strip())
            if match:
                num, text = match.groups()
                text = format_inline_markdown(text)
                list_items.append(Paragraph(f"{num}. {text}", styles['CustomBody']))
                in_list = True
        # Handle horizontal rules
        elif line.strip() in ['---', '***', '___']:
            if in_list:
                elements.extend(list_items)
                list_items = []
                in_list = False
            elements.append(Spacer(1, 0.2*inch))
        # Handle empty lines
        elif not line.strip():
            if in_list:
                elements.extend(list_items)
                elements.append(Spacer(1, 0.1*inch))
                list_items = []
                in_list = False
            elif elements:  # Don't add spacer at the beginning
                elements.append(Spacer(1, 0.1*inch))
        # Handle regular paragraphs
        else:
            if in_list:
                elements.extend(list_items)
                list_items = []
                in_list = False
            text = format_inline_markdown(line)
            if text.strip():
                elements.append(Paragraph(text, styles['CustomBody']))
        
        i += 1
    
    # Add any remaining list items
    if in_list:
        elements.extend(list_items)
    
    return elements


def format_inline_markdown(text: str) -> str:
    """
    Format inline markdown elements like bold, italic, code, and LaTeX.
    Converts to ReportLab XML markup.
    """
    # Escape XML special characters first
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    # Handle LaTeX inline math $...$
    text = re.sub(r'\$([^\$]+)\$', r'<i>\1</i>', text)
    
    # Handle bold + italic ***text*** or ___text___
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<b><i>\1</i></b>', text)
    text = re.sub(r'___(.+?)___', r'<b><i>\1</i></b>', text)
    
    # Handle bold **text** or __text__
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)
    
    # Handle italic *text* or _text_
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    text = re.sub(r'_(.+?)_', r'<i>\1</i>', text)
    
    # Handle inline code `code`
    text = re.sub(r'`([^`]+)`', r'<font name="Courier" color="#333333">\1</font>', text)
    
    return text


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
        """
        Export content as PDF with markdown and basic LaTeX support using ReportLab.
        
        Note: ReportLab has limited emoji support. Complex emojis may not render correctly.
        """
        try:
            output = io.BytesIO()
            
            # Create custom canvas with watermark support
            doc = SimpleDocTemplate(
                output,
                pagesize=A4,
                rightMargin=20,
                leftMargin=20,
                topMargin=20,
                bottomMargin=40 if watermark else 20,
                title=title
            )
            
            # Get custom styles
            styles = create_styles()
            
            # Build story (content elements)
            story = []
            
            # Add title
            story.append(Paragraph(title, styles['CustomTitle']))
            story.append(Spacer(1, 0.3*inch))
            
            # Parse markdown content and add to story
            content_elements = parse_markdown_to_reportlab(content, styles)
            story.extend(content_elements)
            
            # Build PDF with custom canvas for watermark
            if watermark:
                doc.build(
                    story,
                    canvasmaker=lambda *args, **kwargs: WatermarkCanvas(
                        *args, add_watermark=True, **kwargs
                    )
                )
            else:
                doc.build(story)
            
            output.seek(0)
            logger.info(f"PDF generated successfully for '{title}' using ReportLab")
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
