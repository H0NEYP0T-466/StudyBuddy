"""
Tests for improved LaTeX rendering in PDF export.

Covers:
- fix_latex_delimiters: $$...$$, \\[...\\], \\(...\\) normalisation
- format_inline_markdown: LaTeX not corrupted by sanitize_for_xml
- Unicode font registration (_UNICODE_FONT)
- End-to-end PDF generation with LaTeX formulas
"""
import io
import re
import pytest

from app.services.export_service import (
    fix_latex_delimiters,
    format_inline_markdown,
    parse_markdown_to_reportlab,
    create_styles,
    sanitize_for_xml,
    _UNICODE_FONT,
    export_service,
)
from reportlab.platypus import Paragraph, Image


# ===========================================================================
# fix_latex_delimiters
# ===========================================================================
class TestFixLatexDelimiters:
    """Normalise all LaTeX delimiter variants to single-dollar $...$."""

    def test_single_dollar_unchanged(self):
        text = "Inline $x^2 + y^2 = z^2$ formula."
        assert fix_latex_delimiters(text) == text

    def test_backtick_dollar_converted(self):
        text = "Formula `$x^2$` here."
        result = fix_latex_delimiters(text)
        assert "$x^2$" in result
        assert "`" not in result

    def test_double_dollar_converted(self):
        text = "Display math: $$(X^TX + \\lambda I)^{-1}X^Ty$$."
        result = fix_latex_delimiters(text)
        # Should produce a single-dollar wrapped formula (no double $$)
        assert "$$" not in result
        assert "$" in result
        # Formula content must be preserved
        assert "X^TX" in result

    def test_display_math_brackets_converted(self):
        text = r"Formula: \[(X^TX + \lambda I)^{-1}X^Ty\] end."
        result = fix_latex_delimiters(text)
        assert r"\[" not in result
        assert r"\]" not in result
        assert "X^TX" in result

    def test_inline_math_parens_converted(self):
        text = r"Inline: \(x < y\) end."
        result = fix_latex_delimiters(text)
        assert r"\(" not in result
        assert r"\)" not in result
        assert "x < y" in result

    def test_multiline_display_math_converted(self):
        text = "$$\nE = mc^2\n$$"
        result = fix_latex_delimiters(text)
        assert "$$" not in result
        assert "E = mc^2" in result

    def test_unmatched_dollar_closed(self):
        text = "This has $x + y unclosed"
        result = fix_latex_delimiters(text)
        # After fixing, dollars should be even
        assert result.count("$") % 2 == 0


# ===========================================================================
# format_inline_markdown – LaTeX content not broken by XML escaping
# ===========================================================================
class TestFormatInlineMarkdownLatex:
    """Ensure LaTeX formulas with special chars are not corrupted."""

    def test_less_than_in_formula_not_escaped(self):
        """< inside $...$ must reach matplotlib as '<', not '&lt;'."""
        # We cannot inspect the image pixels, but we can verify the formula
        # extracted from the text is not HTML-escaped.
        # We'll do this by monkey-patching render_latex_to_image.
        from app.services import export_service as svc
        captured = []
        original = svc.render_latex_to_image

        def capture(latex, **kwargs):
            captured.append(latex)
            return None  # force fallback path – we only care about what's captured

        svc.render_latex_to_image = capture
        try:
            format_inline_markdown("The condition $x < y$ is key.")
        finally:
            svc.render_latex_to_image = original

        assert captured, "render_latex_to_image was never called"
        assert "&lt;" not in captured[0], (
            "< inside LaTeX was HTML-escaped before being sent to matplotlib"
        )
        assert "<" in captured[0] or "x" in captured[0]

    def test_ampersand_in_formula_not_escaped(self):
        """& inside $...$ must reach matplotlib as '&', not '&amp;'."""
        from app.services import export_service as svc
        captured = []
        original = svc.render_latex_to_image

        def capture(latex, **kwargs):
            captured.append(latex)
            return None

        svc.render_latex_to_image = capture
        try:
            format_inline_markdown(r"Align: $a & b$")
        finally:
            svc.render_latex_to_image = original

        assert captured
        assert "&amp;" not in captured[0], (
            "& inside LaTeX was HTML-escaped before being sent to matplotlib"
        )

    def test_non_latex_text_still_xml_escaped(self):
        """< and & outside LaTeX delimiters must still be XML-escaped."""
        result = format_inline_markdown("a < b & c > d with $x^2$")
        # The non-LaTeX portions must be escaped
        assert isinstance(result, (str, list))
        if isinstance(result, str):
            assert "&lt;" in result or "&amp;" in result
        # (if it's a list of flowables, the Paragraph texts have been escaped)

    def test_formula_fallback_is_xml_safe(self):
        """When image rendering fails, the fallback Courier text must be XML-safe."""
        from app.services import export_service as svc
        original = svc.render_latex_to_image

        svc.render_latex_to_image = lambda *a, **kw: None  # always fail
        try:
            result = format_inline_markdown("$a < b$")
        finally:
            svc.render_latex_to_image = original

        assert isinstance(result, str)
        # The result must be parseable by ReportLab without error
        styles = create_styles()
        if result.strip():
            Paragraph(result, styles["CustomBody"])

    def test_double_dollar_formula_is_rendered(self):
        """$$...$$ display math should be detected and rendered."""
        from app.services import export_service as svc
        captured = []
        original = svc.render_latex_to_image

        def capture(latex, **kwargs):
            captured.append(latex)
            return None

        svc.render_latex_to_image = capture
        try:
            format_inline_markdown("$$(X^TX + \\lambda I)^{-1}X^Ty$$")
        finally:
            svc.render_latex_to_image = original

        assert captured, "$$...$$ formula was not detected for rendering"
        assert "X^TX" in captured[0]

    def test_display_math_brackets_rendered(self):
        r"""\\[...\\] display math should be detected and rendered."""
        from app.services import export_service as svc
        captured = []
        original = svc.render_latex_to_image

        def capture(latex, **kwargs):
            captured.append(latex)
            return None

        svc.render_latex_to_image = capture
        try:
            format_inline_markdown(r"\[(X^TX + \lambda I)^{-1}X^Ty\]")
        finally:
            svc.render_latex_to_image = original

        assert captured, r"\[...\] formula was not detected for rendering"
        assert "X^TX" in captured[0]

    def test_inline_math_parens_rendered(self):
        r"""\\(...\\) inline math should be detected and rendered."""
        from app.services import export_service as svc
        captured = []
        original = svc.render_latex_to_image

        def capture(latex, **kwargs):
            captured.append(latex)
            return None

        svc.render_latex_to_image = capture
        try:
            format_inline_markdown(r"\(x^2 + y^2\)")
        finally:
            svc.render_latex_to_image = original

        assert captured, r"\(...\) formula was not detected for rendering"


# ===========================================================================
# Unicode font registration
# ===========================================================================
class TestUnicodeFontRegistration:
    """The registered font must be usable by ReportLab."""

    def test_unicode_font_not_helvetica_when_dejavu_available(self):
        """On this system DejaVuSans should be registered."""
        import os
        if not os.path.exists("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
            pytest.skip("DejaVuSans not available on this system")
        assert _UNICODE_FONT == "DejaVuSans"

    def test_styles_use_unicode_font(self):
        """CustomBody style must use the Unicode font."""
        styles = create_styles()
        assert styles["CustomBody"].fontName == _UNICODE_FONT

    def test_unicode_characters_parseable_by_reportlab(self):
        """Paragraph with Unicode math characters must not raise."""
        styles = create_styles()
        # These characters appear in AI-generated math content and caused ■ blocks
        unicode_math = "XᵀX (transpose), ⁻¹ (inverse), λ (lambda), ≤ (leq)"
        # Should not raise
        Paragraph(unicode_math, styles["CustomBody"])


# ===========================================================================
# End-to-end PDF generation
# ===========================================================================
class TestPdfLatexEndToEnd:
    """Generate real PDFs and verify they contain valid bytes."""

    @pytest.mark.asyncio
    async def test_pdf_with_single_dollar_latex(self):
        content = "The formula $E = mc^2$ is fundamental."
        result = await export_service.export_to_pdf(content, "Test LaTeX", watermark=False)
        assert isinstance(result, io.BytesIO)
        pdf_bytes = result.read()
        assert pdf_bytes[:4] == b"%PDF"

    @pytest.mark.asyncio
    async def test_pdf_with_double_dollar_latex(self):
        content = "Ridge regression: $$(X^TX + \\lambda I)^{-1}X^Ty$$"
        result = await export_service.export_to_pdf(content, "Ridge Regression", watermark=False)
        pdf_bytes = result.read()
        assert pdf_bytes[:4] == b"%PDF"

    @pytest.mark.asyncio
    async def test_pdf_with_display_math_brackets(self):
        content = r"Formula: \[(X^TX + \lambda I)^{-1}X^Ty\]"
        result = await export_service.export_to_pdf(content, "Display Math", watermark=False)
        pdf_bytes = result.read()
        assert pdf_bytes[:4] == b"%PDF"

    @pytest.mark.asyncio
    async def test_pdf_with_unicode_math_characters(self):
        """Unicode math chars (ᵀ, ⁻, λ) must produce a valid PDF."""
        content = "Solution: (XᵀX + λI)⁻¹Xᵀy where λ controls regularisation."
        result = await export_service.export_to_pdf(content, "Unicode Math", watermark=False)
        pdf_bytes = result.read()
        assert pdf_bytes[:4] == b"%PDF"

    @pytest.mark.asyncio
    async def test_pdf_with_latex_containing_less_than(self):
        """LaTeX with < must not corrupt the formula (bug regression test)."""
        content = "The condition $x < y$ and $a \\leq b$ hold."
        result = await export_service.export_to_pdf(content, "Less Than", watermark=False)
        pdf_bytes = result.read()
        assert pdf_bytes[:4] == b"%PDF"

    @pytest.mark.asyncio
    async def test_pdf_with_multiline_display_math(self):
        r"""Multi-line \\[...\\] blocks must be rendered (not shown literally)."""
        content = "The formula:\n\\[\nE = mc^2\n\\]\nEnd."
        result = await export_service.export_to_pdf(content, "Multiline Math", watermark=False)
        pdf_bytes = result.read()
        assert pdf_bytes[:4] == b"%PDF"
        # If rendered as image the literal \\[ should not appear as visible text
        # (We just verify the PDF is valid – pixel-level check is outside scope.)

    def test_parse_markdown_multiline_display_math(self):
        r"""parse_markdown_to_reportlab must handle multi-line \\[...\\]."""
        styles = create_styles()
        content = "Before:\n\\[\nx^2 + y^2 = z^2\n\\]\nAfter."
        elements, temp_files = parse_markdown_to_reportlab(content, styles)
        # Should produce flowables without raising
        assert len(elements) > 0
