"""Tests for XML sanitization in export_service to prevent ReportLab parse errors."""
import pytest
from app.services.export_service import (
    sanitize_for_xml,
    format_inline_markdown,
    apply_markdown_formatting,
    parse_markdown_to_reportlab,
    create_styles,
)
from reportlab.platypus import Paragraph


class TestSanitizeForXml:
    """Test the sanitize_for_xml helper function."""

    def test_escapes_ampersand(self):
        assert sanitize_for_xml("a & b") == "a &amp; b"

    def test_escapes_less_than(self):
        assert sanitize_for_xml("a < b") == "a &lt; b"

    def test_escapes_greater_than(self):
        assert sanitize_for_xml("a > b") == "a &gt; b"

    def test_escapes_all_special_chars(self):
        assert sanitize_for_xml("a < b & c > d") == "a &lt; b &amp; c &gt; d"

    def test_no_special_chars(self):
        assert sanitize_for_xml("hello world") == "hello world"

    def test_empty_string(self):
        assert sanitize_for_xml("") == ""

    def test_html_tags_escaped(self):
        assert sanitize_for_xml("<b>bold</b>") == "&lt;b&gt;bold&lt;/b&gt;"


class TestFormatInlineMarkdownWithSpecialChars:
    """Test that format_inline_markdown handles special XML characters safely."""

    def test_angle_brackets_in_text(self):
        """Text with < and > should not cause ReportLab parse errors."""
        result = format_inline_markdown("value < 10 and value > 5")
        assert isinstance(result, str)
        assert "&lt;" in result
        assert "&gt;" in result

    def test_html_tags_in_text(self):
        """Literal HTML tags in user content should be escaped."""
        result = format_inline_markdown("Use the <b> tag for bold")
        assert isinstance(result, str)
        # The literal <b> from user content should be escaped
        assert "&lt;b&gt;" in result

    def test_bold_markdown_with_angle_brackets(self):
        """Bold markdown containing angle brackets should produce valid XML."""
        result = format_inline_markdown("**a < b**")
        assert isinstance(result, str)
        # Should have proper <b> tags from markdown AND escaped < inside
        assert "<b>" in result
        assert "&lt;" in result

    def test_result_parseable_by_reportlab(self):
        """The output should be parseable by ReportLab's Paragraph without error."""
        styles = create_styles()
        test_cases = [
            "value < 10",
            "a > b",
            "<html>content</html>",
            "**bold < text**",
            "x < y & z > w",
            "Use <b> tag",
            "",
            "normal text",
        ]
        for text in test_cases:
            result = format_inline_markdown(text)
            if isinstance(result, str) and result.strip():
                # This should NOT raise ValueError
                Paragraph(result, styles["CustomBody"])

    def test_list_item_with_angle_brackets(self):
        """List items with angle brackets should not crash parse_markdown_to_reportlab."""
        styles = create_styles()
        content = "- value < 10\n- value > 5\n- a & b"
        elements, temp_files = parse_markdown_to_reportlab(content, styles)
        assert len(elements) > 0


class TestApplyMarkdownFormatting:
    """Test that markdown formatting still works after XML escaping."""

    def test_bold_still_works(self):
        result = apply_markdown_formatting("**bold**")
        assert "<b>bold</b>" in result

    def test_italic_still_works(self):
        result = apply_markdown_formatting("*italic*")
        assert "<i>italic</i>" in result

    def test_inline_code_still_works(self):
        result = apply_markdown_formatting("`code`")
        assert '<font name="Courier"' in result
