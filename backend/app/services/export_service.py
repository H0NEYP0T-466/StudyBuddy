import io
import re
import logging
import tempfile
import os
from pathlib import Path
from markdown2 import markdown
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Preformatted, Image
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from matplotlib import mathtext

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


def render_latex_to_image(latex_text: str, inline: bool = True) -> str:
    """
    Render LaTeX formula to a PNG image and return the file path.
    
    Args:
        latex_text: The LaTeX formula (without $ delimiters)
        inline: Whether this is inline math (True) or display math (False)
    
    Returns:
        Path to the generated PNG image file
    """
    try:
        # Create a temporary file for the image
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        temp_file.close()
        
        # Configure matplotlib for LaTeX rendering
        fig = plt.figure(figsize=(0.01, 0.01))
        fig.patch.set_facecolor('none')
        fig.patch.set_alpha(0)
        
        # Render the LaTeX formula
        # Use mathtext parser for better compatibility
        text = f'${latex_text}$'
        
        # Calculate the size needed for the text
        renderer = fig.canvas.get_renderer()
        t = fig.text(0, 0, text, fontsize=12 if inline else 14, color='black')
        bbox = t.get_window_extent(renderer=renderer)
        
        # Close the figure and create a new one with proper size
        plt.close(fig)
        
        # Convert bbox dimensions from pixels to inches (assuming 100 dpi)
        width_inches = bbox.width / 100.0
        height_inches = bbox.height / 100.0
        
        # Add some padding
        width_inches += 0.1
        height_inches += 0.1
        
        # Create figure with proper size
        fig = plt.figure(figsize=(width_inches, height_inches))
        fig.patch.set_facecolor('white')
        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis('off')
        
        # Render the text centered
        ax.text(0.5, 0.5, text, 
                fontsize=12 if inline else 14, 
                color='black',
                ha='center', 
                va='center',
                transform=ax.transAxes)
        
        # Save the figure
        plt.savefig(temp_file.name, 
                   format='png', 
                   dpi=150, 
                   bbox_inches='tight',
                   pad_inches=0.05,
                   facecolor='white',
                   edgecolor='none')
        plt.close(fig)
        
        logger.debug(f"Rendered LaTeX to image: {temp_file.name}")
        return temp_file.name
        
    except Exception as e:
        logger.error(f"Failed to render LaTeX '{latex_text}': {str(e)}")
        # Return None to indicate failure
        return None


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
    Supports headings, paragraphs, bold, italic, code blocks, lists, and LaTeX formulas.
    LaTeX formulas are rendered as images and placed inline.
    """
    elements = []
    lines = content.split('\n')
    i = 0
    in_code_block = False
    code_lines = []
    in_list = False
    list_items = []
    temp_image_files = []  # Track temporary image files for cleanup
    
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
            processed_elements = format_inline_markdown(text, styles, temp_image_files)
            if isinstance(processed_elements, list):
                elements.extend(processed_elements)
            else:
                elements.append(Paragraph(processed_elements, styles['CustomTitle']))
            elements.append(Spacer(1, 0.3*inch))
        elif line.startswith('## '):
            if in_list:
                elements.extend(list_items)
                list_items = []
                in_list = False
            text = line[3:].strip()
            processed_elements = format_inline_markdown(text, styles, temp_image_files)
            if isinstance(processed_elements, list):
                elements.extend(processed_elements)
            else:
                elements.append(Paragraph(processed_elements, styles['CustomHeading2']))
            elements.append(Spacer(1, 0.2*inch))
        elif line.startswith('### '):
            if in_list:
                elements.extend(list_items)
                list_items = []
                in_list = False
            text = line[4:].strip()
            processed_elements = format_inline_markdown(text, styles, temp_image_files)
            if isinstance(processed_elements, list):
                elements.extend(processed_elements)
            else:
                elements.append(Paragraph(processed_elements, styles['CustomHeading3']))
            elements.append(Spacer(1, 0.15*inch))
        # Handle lists
        elif line.strip().startswith('- ') or line.strip().startswith('* '):
            text = line.strip()[2:].strip()
            processed_elements = format_inline_markdown(text, styles, temp_image_files)
            if isinstance(processed_elements, list):
                # If there are images, add them with proper bullet handling
                first_text_added = False
                for elem in processed_elements:
                    if isinstance(elem, Image):
                        list_items.append(elem)
                    elif isinstance(elem, Paragraph):
                        # Add bullet to the first text paragraph only
                        if not first_text_added:
                            # Extract text and prepend bullet
                            elem_text = elem.text if hasattr(elem, 'text') else str(elem)
                            list_items.append(Paragraph(f"• {elem_text}", elem.style))
                            first_text_added = True
                        else:
                            list_items.append(elem)
            else:
                list_items.append(Paragraph(f"• {processed_elements}", styles['CustomBody']))
            in_list = True
        elif re.match(r'^\d+\.\s', line.strip()):
            # Numbered list (supports any number)
            match = re.match(r'^(\d+)\.\s+(.+)', line.strip())
            if match:
                num, text = match.groups()
                processed_elements = format_inline_markdown(text, styles, temp_image_files)
                if isinstance(processed_elements, list):
                    # If there are images, add them with proper numbering handling
                    first_text_added = False
                    for elem in processed_elements:
                        if isinstance(elem, Image):
                            list_items.append(elem)
                        elif isinstance(elem, Paragraph):
                            # Add number to the first text paragraph only
                            if not first_text_added:
                                # Extract text and prepend number
                                elem_text = elem.text if hasattr(elem, 'text') else str(elem)
                                list_items.append(Paragraph(f"{num}. {elem_text}", elem.style))
                                first_text_added = True
                            else:
                                list_items.append(elem)
                else:
                    list_items.append(Paragraph(f"{num}. {processed_elements}", styles['CustomBody']))
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
            processed_elements = format_inline_markdown(line, styles, temp_image_files)
            if isinstance(processed_elements, list):
                # Mix of text and images - add them all
                elements.extend(processed_elements)
            elif processed_elements and processed_elements.strip():
                elements.append(Paragraph(processed_elements, styles['CustomBody']))
        
        i += 1
    
    # Add any remaining list items
    if in_list:
        elements.extend(list_items)
    
    return elements, temp_image_files


def format_inline_markdown(text: str, styles=None, temp_image_files=None) -> str:
    """
    Format inline markdown elements like bold, italic, code, and LaTeX.
    Converts to ReportLab XML markup.
    LaTeX formulas are converted to images and inserted at the correct position.
    
    Args:
        text: The text to format
        styles: ReportLab styles (optional, needed for complex formatting)
        temp_image_files: List to track temporary image files for cleanup
    
    Returns:
        Either a string with XML markup, or a list of flowables if images are present
    
    Note: ReportLab's Paragraph class handles XML-like markup, so we don't
    escape angle brackets for bold/italic tags that we intentionally add.
    """
    if temp_image_files is None:
        temp_image_files = []
    
    # First, escape only ampersands in user content (< and > are OK for our XML tags)
    text = text.replace('&', '&amp;')
    
    # Check if text contains LaTeX formulas
    latex_pattern = r'\$([^$]+?)\$'
    has_latex = re.search(latex_pattern, text)
    
    if has_latex:
        # Split text by LaTeX formulas and create a mix of text and images
        parts = []
        last_end = 0
        
        for match in re.finditer(latex_pattern, text):
            # Add text before the formula
            before_text = text[last_end:match.start()]
            if before_text:
                # Apply markdown formatting to the text part
                formatted_text = apply_markdown_formatting(before_text)
                parts.append(('text', formatted_text))
            
            # Render LaTeX formula as image
            latex_formula = match.group(1)
            image_path = render_latex_to_image(latex_formula, inline=True)
            
            if image_path:
                temp_image_files.append(image_path)
                # Store both image path and formula for fallback
                parts.append(('image', image_path, latex_formula))
            else:
                # Fallback to italic if image rendering fails
                parts.append(('text', f'<i>{latex_formula}</i>'))
            
            last_end = match.end()
        
        # Add remaining text
        if last_end < len(text):
            remaining_text = text[last_end:]
            formatted_text = apply_markdown_formatting(remaining_text)
            parts.append(('text', formatted_text))
        
        # If we have images, we need to return a list of flowables
        if any(p[0] == 'image' for p in parts):
            if styles is None:
                # Can't create flowables without styles, return text only with formulas in italic
                result = []
                for p in parts:
                    if p[0] == 'text':
                        result.append(p[1])
                    else:  # image
                        # Use the formula text (p[2]) for fallback
                        result.append(f'<i>{p[2]}</i>')
                return ''.join(result)
            
            flowables = []
            for p in parts:
                part_type = p[0]
                if part_type == 'text':
                    part_value = p[1]
                    if part_value.strip():
                        flowables.append(Paragraph(part_value, styles['CustomBody']))
                elif part_type == 'image':
                    part_value = p[1]  # image path
                    try:
                        # Create inline image with appropriate size
                        img = Image(part_value)
                        # Scale image to fit inline (roughly text height)
                        img.drawHeight = 0.2 * inch
                        img.drawWidth = img.drawHeight * (img.imageWidth / float(img.imageHeight))
                        flowables.append(img)
                        logger.debug(f"Added image flowable: {part_value}")
                    except Exception as e:
                        logger.error(f"Failed to create image from {part_value}: {str(e)}")
            
            return flowables if flowables else ''
        else:
            # No images, just return formatted text
            return ''.join(p[1] for p in parts)
    else:
        # No LaTeX formulas, just apply markdown formatting
        return apply_markdown_formatting(text)


def apply_markdown_formatting(text: str) -> str:
    """
    Apply markdown formatting (bold, italic, code) to text.
    This is separated from format_inline_markdown to handle LaTeX formulas properly.
    """
    # Handle bold + italic first (before individual patterns)
    # ***text*** or ___text___
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<b><i>\1</i></b>', text)
    text = re.sub(r'___(.+?)___', r'<b><i>\1</i></b>', text)
    
    # Handle bold **text** (use ** for bold, not __ to avoid conflicts with Python identifiers)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    
    # Handle italic *text* (be careful not to match mid-word asterisks)
    text = re.sub(r'(?<!\w)\*([^*]+?)\*(?!\w)', r'<i>\1</i>', text)
    
    # Handle italic _text_ (be careful with underscores in identifiers like __init__)
    # Only match single underscores that are not adjacent to other underscores
    text = re.sub(r'(?<![_a-zA-Z0-9])_([^_]+?)_(?![_a-zA-Z0-9])', r'<i>\1</i>', text)
    
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
        Export content as PDF with markdown and LaTeX support using ReportLab.
        LaTeX formulas are rendered as images using matplotlib.
        
        Note: ReportLab has limited emoji support. Complex emojis may not render correctly.
        """
        temp_image_files = []
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
            content_elements, temp_image_files = parse_markdown_to_reportlab(content, styles)
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
            logger.info(f"PDF generated successfully for '{title}' using ReportLab with LaTeX support")
            return output
            
        except Exception as e:
            logger.error(f"PDF generation failed: {str(e)}", exc_info=True)
            raise
        finally:
            # Clean up temporary image files
            for temp_file in temp_image_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                        logger.debug(f"Cleaned up temporary LaTeX image: {temp_file}")
                except Exception as e:
                    logger.warning(f"Failed to clean up temporary file {temp_file}: {str(e)}")

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
