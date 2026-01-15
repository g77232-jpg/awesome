"""
Comprehensive tests for generate_book_primer.py

This test suite covers all functions in the book primer generator including:
- JSON data loading with error handling
- Date parsing and formatting
- Author list formatting
- Chronological sorting
- Markdown generation
- Task checklist generation
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, mock_open
import sys
import os

# Add parent directory to path to import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generate_book_primer import (
    load_books_data,
    sort_books_chronologically,
    format_date,
    format_authors,
    generate_summary_markdown,
    generate_task_checklist
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def sample_books_data():
    """Sample book data for testing"""
    return {
        "books": [
            {
                "title": "The Pragmatic Programmer",
                "authors": ["David Thomas", "Andrew Hunt"],
                "date": "1999-10-20",
                "category": "Software Engineering",
                "description": "A classic guide to software craftsmanship",
                "link": "https://example.com/pragmatic"
            },
            {
                "title": "Clean Code",
                "authors": ["Robert C. Martin"],
                "date": "2008-08-01",
                "category": "Software Engineering",
                "description": "A handbook of agile software craftsmanship",
                "link": "https://example.com/cleancode"
            },
            {
                "title": "Design Patterns",
                "authors": ["Erich Gamma", "Richard Helm", "Ralph Johnson", "John Vlissides"],
                "date": "1994-10-21",
                "category": "Software Design",
                "description": "Elements of reusable object-oriented software",
                "link": "https://example.com/patterns"
            }
        ]
    }


@pytest.fixture
def sample_books_list(sample_books_data):
    """Extract just the books list"""
    return sample_books_data["books"]


@pytest.fixture
def temp_json_file(sample_books_data):
    """Create a temporary JSON file with sample data"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(sample_books_data, f)
        temp_path = f.name
    yield temp_path
    # Cleanup
    Path(temp_path).unlink(missing_ok=True)


# ============================================================================
# Tests for load_books_data()
# ============================================================================

class TestLoadBooksData:
    """Test suite for load_books_data function"""

    def test_load_valid_json_file(self, temp_json_file, sample_books_data):
        """Test loading a valid JSON file"""
        result = load_books_data(temp_json_file)
        assert result == sample_books_data
        assert "books" in result
        assert len(result["books"]) == 3

    def test_load_nonexistent_file(self):
        """Test loading a file that doesn't exist"""
        with pytest.raises(SystemExit) as exc_info:
            load_books_data("nonexistent_file.json")
        assert exc_info.value.code == 1

    def test_load_invalid_json(self):
        """Test loading a file with invalid JSON"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            f.write("{ invalid json content }")
            temp_path = f.name

        try:
            with pytest.raises(SystemExit) as exc_info:
                load_books_data(temp_path)
            assert exc_info.value.code == 1
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_load_empty_json_file(self):
        """Test loading an empty JSON object"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump({}, f)
            temp_path = f.name

        try:
            result = load_books_data(temp_path)
            assert result == {}
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_load_json_with_special_characters(self):
        """Test loading JSON with unicode and special characters"""
        data = {
            "books": [{
                "title": "Cracking the Coding Interview",
                "authors": ["Gayle Laakmann McDowell"],
                "date": "2015-07-01",
                "category": "Interview Prep",
                "description": "189 programming questions & solutions 📚",
                "link": "https://example.com/ctci"
            }]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
            temp_path = f.name

        try:
            result = load_books_data(temp_path)
            assert result == data
            assert "📚" in result["books"][0]["description"]
        finally:
            Path(temp_path).unlink(missing_ok=True)


# ============================================================================
# Tests for sort_books_chronologically()
# ============================================================================

class TestSortBooksChronologically:
    """Test suite for sort_books_chronologically function"""

    def test_sort_books_ascending_order(self, sample_books_list):
        """Test that books are sorted from oldest to newest"""
        sorted_books = sort_books_chronologically(sample_books_list)

        # Verify order: 1994 -> 1999 -> 2008
        assert sorted_books[0]["title"] == "Design Patterns"  # 1994
        assert sorted_books[1]["title"] == "The Pragmatic Programmer"  # 1999
        assert sorted_books[2]["title"] == "Clean Code"  # 2008

    def test_sort_already_sorted_books(self):
        """Test sorting books that are already in order"""
        books = [
            {"title": "Book A", "date": "2000-01-01"},
            {"title": "Book B", "date": "2001-01-01"},
            {"title": "Book C", "date": "2002-01-01"}
        ]
        sorted_books = sort_books_chronologically(books)

        assert sorted_books[0]["title"] == "Book A"
        assert sorted_books[1]["title"] == "Book B"
        assert sorted_books[2]["title"] == "Book C"

    def test_sort_reverse_order_books(self):
        """Test sorting books in reverse chronological order"""
        books = [
            {"title": "Book C", "date": "2002-01-01"},
            {"title": "Book B", "date": "2001-01-01"},
            {"title": "Book A", "date": "2000-01-01"}
        ]
        sorted_books = sort_books_chronologically(books)

        assert sorted_books[0]["title"] == "Book A"
        assert sorted_books[1]["title"] == "Book B"
        assert sorted_books[2]["title"] == "Book C"

    def test_sort_books_same_date(self):
        """Test sorting books published on the same date"""
        books = [
            {"title": "Book B", "date": "2000-06-15"},
            {"title": "Book A", "date": "2000-06-15"},
            {"title": "Book C", "date": "2000-06-15"}
        ]
        sorted_books = sort_books_chronologically(books)

        # All should have the same date, order may vary but should be stable
        assert len(sorted_books) == 3
        for book in sorted_books:
            assert book["date"] == "2000-06-15"

    def test_sort_empty_list(self):
        """Test sorting an empty list of books"""
        sorted_books = sort_books_chronologically([])
        assert sorted_books == []

    def test_sort_single_book(self):
        """Test sorting a list with a single book"""
        books = [{"title": "Solo Book", "date": "2000-01-01"}]
        sorted_books = sort_books_chronologically(books)

        assert len(sorted_books) == 1
        assert sorted_books[0]["title"] == "Solo Book"

    def test_sort_books_different_date_formats(self):
        """Test sorting books with different ISO date formats"""
        books = [
            {"title": "Book A", "date": "2000-12-31"},
            {"title": "Book B", "date": "2000-01-01"},
            {"title": "Book C", "date": "2000-06-15"}
        ]
        sorted_books = sort_books_chronologically(books)

        assert sorted_books[0]["title"] == "Book B"  # Jan
        assert sorted_books[1]["title"] == "Book C"  # Jun
        assert sorted_books[2]["title"] == "Book A"  # Dec

    def test_sort_preserves_original_data(self, sample_books_list):
        """Test that sorting doesn't modify the original data structure"""
        import copy
        original = copy.deepcopy(sample_books_list)
        sorted_books = sort_books_chronologically(sample_books_list)

        # Original should be unchanged
        assert sample_books_list == original
        # But sorted should be different (unless already sorted)
        assert sorted_books != original


# ============================================================================
# Tests for format_date()
# ============================================================================

class TestFormatDate:
    """Test suite for format_date function"""

    def test_format_standard_date(self):
        """Test formatting a standard ISO date"""
        result = format_date("2024-03-15")
        assert result == "March 15, 2024"

    def test_format_first_of_month(self):
        """Test formatting the first day of a month"""
        result = format_date("2024-01-01")
        assert result == "January 01, 2024"

    def test_format_last_of_month(self):
        """Test formatting the last day of a month"""
        result = format_date("2024-12-31")
        assert result == "December 31, 2024"

    @pytest.mark.parametrize("date_str,expected", [
        ("2000-01-15", "January 15, 2000"),
        ("1999-02-28", "February 28, 1999"),
        ("2024-07-04", "July 04, 2024"),
        ("2008-11-20", "November 20, 2008"),
        ("1994-10-21", "October 21, 1994"),
    ])
    def test_format_various_dates(self, date_str, expected):
        """Test formatting various dates"""
        assert format_date(date_str) == expected

    def test_format_leap_year_date(self):
        """Test formatting February 29 on a leap year"""
        result = format_date("2024-02-29")
        assert result == "February 29, 2024"

    def test_format_millennium_date(self):
        """Test formatting Y2K date"""
        result = format_date("2000-01-01")
        assert result == "January 01, 2000"


# ============================================================================
# Tests for format_authors()
# ============================================================================

class TestFormatAuthors:
    """Test suite for format_authors function"""

    def test_format_single_author(self):
        """Test formatting a single author"""
        result = format_authors(["Robert C. Martin"])
        assert result == "Robert C. Martin"

    def test_format_two_authors(self):
        """Test formatting two authors with 'and'"""
        result = format_authors(["David Thomas", "Andrew Hunt"])
        assert result == "David Thomas and Andrew Hunt"

    def test_format_three_authors(self):
        """Test formatting three authors with Oxford comma"""
        result = format_authors(["Author A", "Author B", "Author C"])
        assert result == "Author A, Author B, and Author C"

    def test_format_four_authors(self):
        """Test formatting four authors (Gang of Four pattern)"""
        authors = ["Erich Gamma", "Richard Helm", "Ralph Johnson", "John Vlissides"]
        result = format_authors(authors)
        assert result == "Erich Gamma, Richard Helm, Ralph Johnson, and John Vlissides"

    def test_format_many_authors(self):
        """Test formatting many authors"""
        authors = ["Author 1", "Author 2", "Author 3", "Author 4", "Author 5"]
        result = format_authors(authors)
        assert result == "Author 1, Author 2, Author 3, Author 4, and Author 5"
        assert result.count(",") == 4
        assert " and " in result

    def test_format_authors_with_special_characters(self):
        """Test formatting authors with special characters in names"""
        result = format_authors(["O'Reilly", "García", "Müller"])
        assert result == "O'Reilly, García, and Müller"

    def test_format_authors_preserves_order(self):
        """Test that author order is preserved"""
        authors = ["Zebra Author", "Alpha Author", "Middle Author"]
        result = format_authors(authors)
        assert result.startswith("Zebra Author")
        assert result.endswith("Middle Author")


# ============================================================================
# Tests for generate_summary_markdown()
# ============================================================================

class TestGenerateSummaryMarkdown:
    """Test suite for generate_summary_markdown function"""

    @patch('generate_book_primer.datetime')
    def test_generate_basic_structure(self, mock_datetime, sample_books_list):
        """Test that generated markdown has the correct basic structure"""
        # Mock the current time
        mock_now = datetime(2024, 3, 15, 10, 30)
        mock_datetime.now.return_value = mock_now
        mock_datetime.fromisoformat = datetime.fromisoformat

        result = generate_summary_markdown(sample_books_list)

        # Check header
        assert "# Book Primer Summary" in result
        assert "*Last updated:" in result

        # Check sections exist
        assert "## Books in Chronological Order" in result
        assert "## Statistics" in result

        # Check footer
        assert "*This summary is automatically generated daily" in result

    @patch('generate_book_primer.datetime')
    def test_generate_groups_by_decade(self, mock_datetime, sample_books_list):
        """Test that books are grouped by decade"""
        mock_now = datetime(2024, 3, 15, 10, 30)
        mock_datetime.now.return_value = mock_now
        mock_datetime.fromisoformat = datetime.fromisoformat

        result = generate_summary_markdown(sample_books_list)

        # Should have 1990s and 2000s sections
        assert "### 1990s" in result
        assert "### 2000s" in result

    @patch('generate_book_primer.datetime')
    def test_generate_includes_all_book_fields(self, mock_datetime, sample_books_list):
        """Test that all book fields are included in the output"""
        mock_now = datetime(2024, 3, 15, 10, 30)
        mock_datetime.now.return_value = mock_now
        mock_datetime.fromisoformat = datetime.fromisoformat

        result = generate_summary_markdown(sample_books_list)

        # Check that all books are included
        assert "Clean Code" in result
        assert "The Pragmatic Programmer" in result
        assert "Design Patterns" in result

        # Check that metadata is included
        assert "**Authors:**" in result
        assert "**Category:**" in result
        assert "**Published:**" in result

        # Check specific author formatting
        assert "Robert C. Martin" in result
        assert "David Thomas and Andrew Hunt" in result

    @patch('generate_book_primer.datetime')
    def test_generate_statistics_section(self, mock_datetime, sample_books_list):
        """Test that statistics are calculated correctly"""
        mock_now = datetime(2024, 3, 15, 10, 30)
        mock_datetime.now.return_value = mock_now
        mock_datetime.fromisoformat = datetime.fromisoformat

        result = generate_summary_markdown(sample_books_list)

        # Check total count
        assert "**Total Books:** 3" in result

        # Check category counts
        assert "**By Category:**" in result
        assert "Software Engineering: 2" in result
        assert "Software Design: 1" in result

        # Check date range
        assert "**Date Range:**" in result

    @patch('generate_book_primer.datetime')
    def test_generate_with_empty_list(self, mock_datetime):
        """Test generating markdown with an empty book list"""
        mock_now = datetime(2024, 3, 15, 10, 30)
        mock_datetime.now.return_value = mock_now
        mock_datetime.fromisoformat = datetime.fromisoformat

        result = generate_summary_markdown([])

        assert "# Book Primer Summary" in result
        assert "**Total Books:** 0" in result

    @patch('generate_book_primer.datetime')
    def test_generate_with_single_book(self, mock_datetime):
        """Test generating markdown with a single book"""
        mock_now = datetime(2024, 3, 15, 10, 30)
        mock_datetime.now.return_value = mock_now
        mock_datetime.fromisoformat = datetime.fromisoformat

        books = [{
            "title": "Solo Book",
            "authors": ["Solo Author"],
            "date": "2020-01-01",
            "category": "Test Category",
            "description": "A test book",
            "link": "https://example.com/solo"
        }]

        result = generate_summary_markdown(books)

        assert "**Total Books:** 1" in result
        assert "Solo Book" in result
        assert "Solo Author" in result
        assert "### 2020s" in result

    @patch('generate_book_primer.datetime')
    def test_generate_books_same_decade(self, mock_datetime):
        """Test generating markdown when all books are from the same decade"""
        mock_now = datetime(2024, 3, 15, 10, 30)
        mock_datetime.now.return_value = mock_now
        mock_datetime.fromisoformat = datetime.fromisoformat

        books = [
            {"title": "Book 1", "authors": ["Author 1"], "date": "2020-01-01",
             "category": "Cat1", "description": "Desc 1", "link": "https://example.com/1"},
            {"title": "Book 2", "authors": ["Author 2"], "date": "2021-06-15",
             "category": "Cat1", "description": "Desc 2", "link": "https://example.com/2"},
            {"title": "Book 3", "authors": ["Author 3"], "date": "2022-12-31",
             "category": "Cat1", "description": "Desc 3", "link": "https://example.com/3"}
        ]

        result = generate_summary_markdown(books)

        # Should only have 2020s section
        assert "### 2020s" in result
        assert "### 2010s" not in result
        assert "### 2030s" not in result

    @patch('generate_book_primer.datetime')
    def test_generate_markdown_link_format(self, mock_datetime, sample_books_list):
        """Test that book titles are formatted as markdown links"""
        mock_now = datetime(2024, 3, 15, 10, 30)
        mock_datetime.now.return_value = mock_now
        mock_datetime.fromisoformat = datetime.fromisoformat

        result = generate_summary_markdown(sample_books_list)

        # Check markdown link format [Title](URL)
        assert "[Clean Code](https://example.com/cleancode)" in result
        assert "[The Pragmatic Programmer](https://example.com/pragmatic)" in result

    @patch('generate_book_primer.datetime')
    def test_generate_chronological_order_in_decades(self, mock_datetime):
        """Test that books within decades are in chronological order when pre-sorted"""
        mock_now = datetime(2024, 3, 15, 10, 30)
        mock_datetime.now.return_value = mock_now
        mock_datetime.fromisoformat = datetime.fromisoformat

        books = [
            {"title": "Book 2020C", "authors": ["Author"], "date": "2020-12-31",
             "category": "Cat", "description": "Desc", "link": "https://example.com/c"},
            {"title": "Book 2020A", "authors": ["Author"], "date": "2020-01-01",
             "category": "Cat", "description": "Desc", "link": "https://example.com/a"},
            {"title": "Book 2020B", "authors": ["Author"], "date": "2020-06-15",
             "category": "Cat", "description": "Desc", "link": "https://example.com/b"}
        ]

        # Sort books first (as the function expects pre-sorted input)
        sorted_books = sort_books_chronologically(books)
        result = generate_summary_markdown(sorted_books)

        # Find positions in the string
        pos_a = result.find("Book 2020A")
        pos_b = result.find("Book 2020B")
        pos_c = result.find("Book 2020C")

        # Verify chronological order
        assert pos_a < pos_b < pos_c


# ============================================================================
# Tests for generate_task_checklist()
# ============================================================================

class TestGenerateTaskChecklist:
    """Test suite for generate_task_checklist function"""

    @patch('generate_book_primer.datetime')
    def test_generate_checklist_structure(self, mock_datetime):
        """Test that checklist has correct structure"""
        mock_now = datetime(2024, 3, 15, 10, 30)
        mock_datetime.now.return_value = mock_now
        mock_datetime.strftime = datetime.strftime

        result = generate_task_checklist()

        # Check header with date
        assert "# Daily Book Primer Task - 2024-03-15" in result

        # Check sections
        assert "## Today's Tasks" in result
        assert "## Quick Commands" in result

        # Check that tasks have checkboxes
        assert "- [ ]" in result

    @patch('generate_book_primer.datetime')
    def test_generate_checklist_includes_all_tasks(self, mock_datetime):
        """Test that all expected tasks are in the checklist"""
        mock_now = datetime(2024, 3, 15, 10, 30)
        mock_datetime.now.return_value = mock_now
        mock_datetime.strftime = datetime.strftime

        result = generate_task_checklist()

        # Check for all expected task items
        expected_tasks = [
            "Review the chronologically sorted book list",
            "Add any new books to `books-data.json`",
            "Verify all publication dates are accurate",
            "Check that all links are working",
            "Update book descriptions if needed",
            "Review categorization",
            "Commit any changes"
        ]

        for task in expected_tasks:
            assert task in result

    @patch('generate_book_primer.datetime')
    def test_generate_checklist_includes_example_json(self, mock_datetime):
        """Test that checklist includes example JSON structure"""
        mock_now = datetime(2024, 3, 15, 10, 30)
        mock_datetime.now.return_value = mock_now
        mock_datetime.strftime = datetime.strftime

        result = generate_task_checklist()

        # Check for JSON example
        assert "```json" in result
        assert '"title"' in result
        assert '"authors"' in result
        assert '"date"' in result
        assert '"category"' in result

    @patch('generate_book_primer.datetime')
    def test_generate_checklist_includes_commands(self, mock_datetime):
        """Test that checklist includes command examples"""
        mock_now = datetime(2024, 3, 15, 10, 30)
        mock_datetime.now.return_value = mock_now
        mock_datetime.strftime = datetime.strftime

        result = generate_task_checklist()

        # Check for command example
        assert "```bash" in result
        assert "python3 generate_book_primer.py" in result

    @patch('generate_book_primer.datetime')
    def test_generate_checklist_footer(self, mock_datetime):
        """Test that checklist has proper footer with timestamp"""
        mock_now = datetime(2024, 3, 15, 10, 30)
        mock_datetime.now.return_value = mock_now
        mock_datetime.strftime = datetime.strftime

        result = generate_task_checklist()

        # Check footer
        assert "*Generated:" in result
        assert "March 15, 2024 at 10:30 UTC" in result

    @patch('generate_book_primer.datetime')
    def test_generate_checklist_different_dates(self, mock_datetime):
        """Test checklist generation on different dates"""
        # Test New Year's Day
        mock_datetime.now.return_value = datetime(2025, 1, 1, 0, 0)
        mock_datetime.strftime = datetime.strftime

        result = generate_task_checklist()
        assert "2025-01-01" in result

        # Test leap year day
        mock_datetime.now.return_value = datetime(2024, 2, 29, 12, 0)
        result = generate_task_checklist()
        assert "2024-02-29" in result


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for the entire workflow"""

    def test_full_workflow(self, temp_json_file):
        """Test loading, sorting, and generating markdown"""
        # Load data
        data = load_books_data(temp_json_file)
        books = data.get('books', [])

        # Sort books
        sorted_books = sort_books_chronologically(books)

        # Verify sorting worked
        assert len(sorted_books) == 3
        assert sorted_books[0]['date'] == "1994-10-21"  # Design Patterns
        assert sorted_books[-1]['date'] == "2008-08-01"  # Clean Code

        # Generate markdown
        markdown = generate_summary_markdown(sorted_books)

        # Verify markdown contains expected content
        assert "Design Patterns" in markdown
        assert "Clean Code" in markdown
        assert "The Pragmatic Programmer" in markdown

        # Verify statistics
        assert "**Total Books:** 3" in markdown

    @patch('generate_book_primer.datetime')
    def test_markdown_and_checklist_consistency(self, mock_datetime, sample_books_list):
        """Test that both outputs can be generated consistently"""
        mock_now = datetime(2024, 3, 15, 10, 30)
        mock_datetime.now.return_value = mock_now
        mock_datetime.strftime = datetime.strftime
        mock_datetime.fromisoformat = datetime.fromisoformat

        # Generate both outputs
        markdown = generate_summary_markdown(sample_books_list)
        checklist = generate_task_checklist()

        # Both should be non-empty strings
        assert isinstance(markdown, str)
        assert isinstance(checklist, str)
        assert len(markdown) > 0
        assert len(checklist) > 0

        # Both should have proper markdown structure
        assert markdown.startswith("# ")
        assert checklist.startswith("# ")


# ============================================================================
# Edge Case Tests
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_books_spanning_century(self):
        """Test books from different centuries"""
        books = [
            {"title": "Old Book", "authors": ["Old Author"], "date": "1899-12-31",
             "category": "Historical", "description": "19th century", "link": "https://example.com/old"},
            {"title": "Modern Book", "authors": ["Modern Author"], "date": "2024-01-01",
             "category": "Contemporary", "description": "21st century", "link": "https://example.com/modern"}
        ]

        sorted_books = sort_books_chronologically(books)
        assert sorted_books[0]['title'] == "Old Book"
        assert sorted_books[1]['title'] == "Modern Book"

    def test_format_authors_empty_list(self):
        """Test formatting an empty authors list (edge case)"""
        # This would be invalid data, but test graceful handling
        with pytest.raises(IndexError):
            format_authors([])

    def test_very_long_author_list(self):
        """Test formatting a very long list of authors"""
        authors = [f"Author {i}" for i in range(1, 21)]  # 20 authors
        result = format_authors(authors)

        assert result.startswith("Author 1")
        assert result.endswith("and Author 20")
        assert result.count(",") == 19

    @patch('generate_book_primer.datetime')
    def test_single_category_statistics(self, mock_datetime):
        """Test statistics when all books are in one category"""
        mock_now = datetime(2024, 3, 15, 10, 30)
        mock_datetime.now.return_value = mock_now
        mock_datetime.fromisoformat = datetime.fromisoformat

        books = [
            {"title": "Book 1", "authors": ["Author 1"], "date": "2020-01-01",
             "category": "Python", "description": "Desc", "link": "https://example.com/1"},
            {"title": "Book 2", "authors": ["Author 2"], "date": "2021-01-01",
             "category": "Python", "description": "Desc", "link": "https://example.com/2"}
        ]

        result = generate_summary_markdown(books)

        assert "Python: 2" in result
        assert "**Total Books:** 2" in result

    def test_format_date_edge_of_year(self):
        """Test date formatting at year boundaries"""
        assert format_date("2024-01-01") == "January 01, 2024"
        assert format_date("2023-12-31") == "December 31, 2023"

    @patch('generate_book_primer.datetime')
    def test_generate_with_unicode_content(self, mock_datetime):
        """Test generating markdown with unicode characters"""
        mock_now = datetime(2024, 3, 15, 10, 30)
        mock_datetime.now.return_value = mock_now
        mock_datetime.fromisoformat = datetime.fromisoformat

        books = [{
            "title": "Le Petit Prince 👑",
            "authors": ["Antoine de Saint-Exupéry"],
            "date": "1943-04-06",
            "category": "Fiction littéraire",
            "description": "Un conte poétique et philosophique 🌟",
            "link": "https://example.com/prince"
        }]

        result = generate_summary_markdown(books)

        assert "Le Petit Prince 👑" in result
        assert "Antoine de Saint-Exupéry" in result
        assert "Fiction littéraire" in result
        assert "🌟" in result
