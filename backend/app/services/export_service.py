import io
import re
import logging
from xml.sax.saxutils import escape
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH

# ==========================
# Configuration
# ==========================
WATERMARK_TEXT = "~honeypot"

logger = logging.getLogger(__name__)

# ==========================
# Font Registration
# ==========================
try:
    pdfmetrics.registerFont(
        TTFont("DejaVuSans", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    )
    pdfmetrics.registerFont(
        TTFont("DejaVuSans-Bold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
    )
    FONTS_REGISTERED = True
except Exception as e:
    logger.warning(f"Font load failed: {e}")
    FONTS_REGISTERED = False

# ==========================
# Emoji sanitizer (PDF only)
# ==========================
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F700-\U0001F77F"
    "\U0001F780-\U0001F7FF"
    "\U0001F800-\U0001F8FF"
    "\U0001F900-\U0001F9FF"
    "\U0001FA00-\U0001FAFF"
    "]+",
    flags=re.UNICODE,
)

def strip_emojis(text: str) -> str:
    return EMOJI_PATTERN.sub("", text)

# ==========================
# Watermark (Platypus-safe)
# ==========================
def add_watermark(canvas, doc):
    canvas.saveState()
    font = "DejaVuSans" if FONTS_REGISTERED else "Helvetica"
    canvas.setFont(font, 10)
    canvas.setFillColorRGB(0.6, 0.6, 0.6)
    canvas.drawRightString(
        letter[0] - 0.5 * inch,
        0.5 * inch,
        WATERMARK_TEXT
    )
    canvas.restoreState()

# ==========================
# Export Service
# ==========================
class ExportService:

    @staticmethod
    def export_to_markdown(content: str, title: str) -> io.BytesIO:
        output = io.BytesIO()
        md = f"# {title}\n\n{content}"
        output.write(md.encode("utf-8"))
        output.seek(0)
        return output

    @staticmethod
    def export_to_pdf(content: str, title: str, watermark: bool = True) -> io.BytesIO:
        output = io.BytesIO()

        doc = SimpleDocTemplate(
            output,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72,
        )

        styles = getSampleStyleSheet()
        base_font = "DejaVuSans" if FONTS_REGISTERED else "Helvetica"
        bold_font = "DejaVuSans-Bold" if FONTS_REGISTERED else "Helvetica-Bold"

        title_style = ParagraphStyle(
            "Title",
            parent=styles["Heading1"],
            fontName=bold_font,
            fontSize=24,
            alignment=TA_CENTER,
            spaceAfter=30,
        )

        body_style = ParagraphStyle(
            "Body",
            parent=styles["BodyText"],
            fontName=base_font,
            fontSize=11,
        )

        story = []

        # Title
        story.append(Paragraph(escape(strip_emojis(title)), title_style))
        story.append(Spacer(1, 0.2 * inch))

        # Content
        for line in content.split("\n"):
            if not line.strip():
                continue

            clean = escape(strip_emojis(line))
            story.append(Paragraph(clean, body_style))
            story.append(Spacer(1, 0.1 * inch))

        doc.build(
            story,
            onFirstPage=add_watermark if watermark else None,
            onLaterPages=add_watermark if watermark else None,
        )

        output.seek(0)
        return output

    @staticmethod
    def export_to_docx(content: str, title: str) -> io.BytesIO:
        output = io.BytesIO()
        doc = Document()

        title_para = doc.add_heading(title, level=0)
        title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

        for line in content.split("\n"):
            if not line.strip():
                continue
            doc.add_paragraph(line)

        doc.save(output)
        output.seek(0)
        return output


# Global instance
export_service = ExportService()
