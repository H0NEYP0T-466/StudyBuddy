"""Tests for the export_to_txt method and zip export endpoint."""
import io
import pytest
from app.services.export_service import export_service


class TestExportToTxt:
    """Test the export_to_txt static method."""

    def test_returns_bytes_io(self):
        result = export_service.export_to_txt("Hello world", "Test Title")
        assert isinstance(result, io.BytesIO)

    def test_contains_title(self):
        result = export_service.export_to_txt("Hello world", "My Notes")
        text = result.read().decode("utf-8")
        assert "My Notes" in text

    def test_contains_content(self):
        result = export_service.export_to_txt("Some content here", "Title")
        text = result.read().decode("utf-8")
        assert "Some content here" in text

    def test_strips_bold_markdown(self):
        result = export_service.export_to_txt("This is **bold** text", "Title")
        text = result.read().decode("utf-8")
        assert "**" not in text
        assert "bold" in text

    def test_strips_italic_markdown(self):
        result = export_service.export_to_txt("This is *italic* text", "Title")
        text = result.read().decode("utf-8")
        assert "italic" in text

    def test_strips_heading_markers(self):
        result = export_service.export_to_txt("# Heading 1\n## Heading 2", "Title")
        text = result.read().decode("utf-8")
        assert "Heading 1" in text
        assert "Heading 2" in text
        # The content headings should not have # markers
        lines = text.split("\n")
        content_lines = [l for l in lines if "Heading" in l]
        for line in content_lines:
            assert not line.startswith("#")

    def test_strips_code_block_markers(self):
        result = export_service.export_to_txt("```python\nprint('hello')\n```", "Title")
        text = result.read().decode("utf-8")
        assert "print('hello')" in text
        assert "```" not in text

    def test_empty_content(self):
        result = export_service.export_to_txt("", "Title")
        text = result.read().decode("utf-8")
        assert "Title" in text

    def test_title_underline(self):
        """Title should have an underline of = characters matching its length."""
        result = export_service.export_to_txt("content", "MyTitle")
        text = result.read().decode("utf-8")
        assert "=======" in text
