from citation_compass.docstring_utils import (
    _CITATION_ALL_KEYWORDS,
    check_for_any_citation_keyword,
    extract_citation,
    extract_urls,
)


def test_check_docstring_for_keyword():
    """Check that the function correctly identifies citation keywords."""
    assert check_for_any_citation_keyword("This is a docstring.") is False
    assert check_for_any_citation_keyword("This is a citation.") is True
    assert check_for_any_citation_keyword("This is a reference.") is True

    for keyword in _CITATION_ALL_KEYWORDS:
        assert check_for_any_citation_keyword(f"{keyword}: other stuff") is True

    # Check empty docstrings.
    assert check_for_any_citation_keyword("") is False
    assert check_for_any_citation_keyword(None) is False


def test_check_docstring_for_keyword_custom():
    """Check that the function correctly identifies docstrings with custom keywords."""
    assert check_for_any_citation_keyword("This is a docstring.") is False
    assert check_for_any_citation_keyword("This is a docstring.", keywords=["docstring"]) is True
    assert check_for_any_citation_keyword("This is a citation.") is True
    assert check_for_any_citation_keyword("This is a citation.", keywords=["nonexistent"]) is False


def test_extract_citation_colon():
    """Test that we can extract a citation using the 'keyword:' format."""
    # Check an empty docstring.
    assert extract_citation("") is None
    assert extract_citation(None) is None

    # Start with single line docstrings.
    assert extract_citation("Citation: Author, Title, year.") == "Author, Title, year."
    assert extract_citation("Reference: Author, Title, year.") == "Author, Title, year."
    assert extract_citation("Info: Nothing to see here") is None

    # Test multi-line docstrings.
    docstring = """Top material:
    Stuff here.

    Citation:
        Author1, Author2, Title, year.

    Bottom material:
    More stuff."""
    assert extract_citation(docstring) == "Author1, Author2, Title, year."

    docstring = """Function description.

    Reference:
        Author1, Author2, Title, year.

    Parameters
    ----------
    Stuff here.

    Returns
    -------
    More stuff."""
    assert extract_citation(docstring) == "Author1, Author2, Title, year."

    docstring = """Function description.

    Parameters
    ----------
    Stuff here.

    Returns
    -------
    More stuff.

    Citation:
        Author1, Author2,
        Title,
        journal,
        year
    """
    assert extract_citation(docstring) == "Author1, Author2,\nTitle,\njournal,\nyear"


def test_extract_citation_underline():
    """Test that we can extract a citation using the underline section format."""
    docstring = """
    Top material
    ------------
    Stuff here.

    Citation
    ------
        Author1, Author2, Title, year.

    Bottom material
    ---------------
    More stuff."""
    assert extract_citation(docstring) == "Author1, Author2, Title, year."

    docstring = """Function description.

    Reference
    -----------
        Author1,
        Author2,
        Title,
        year

    Parameters
    ----------
    Stuff here.

    Returns
    -------
    More stuff."""
    assert extract_citation(docstring) == "Author1,\nAuthor2,\nTitle,\nyear"

    # Sections end after two blank lines.
    docstring = """Function description.

    Reference
    -----------
        Author1,
        Author2,
        Title2,
        year


    This is not part of the citation.

    Parameters
    ----------
    Stuff here.

    Returns
    -------
    More stuff."""
    assert extract_citation(docstring) == "Author1,\nAuthor2,\nTitle2,\nyear"

    # Formatting perserved for multiple citations in a block.
    docstring = """Function description.

    References
    -----------
    * Author1, Author2, Title1, year1
    * Author3, Author4, Title2, year2
    * Author5, Author6, Title3, year3

    Parameters
    ----------
    Stuff here.

    Returns
    -------
    More stuff."""
    expected = (
        "* Author1, Author2, Title1, year1\n* Author3, Author4, Title2, year2\n"
        "* Author5, Author6, Title3, year3"
    )
    assert extract_citation(docstring) == expected


def test_extract_citation_multiple():
    """Test that we can extract multiple citations from a string."""
    # Test multi-line docstrings.
    docstring = """Top material:
    Stuff here.

    Citation: Author1, Author2, Title1, year.

    Citation: Author3, Author4, Title2, year.

    Bottom material:
    More stuff."""
    assert extract_citation(docstring) == "Author1, Author2, Title1, year.\nAuthor3, Author4, Title2, year."

    docstring = """Function description.

    Reference
    ---------
        Author1, Author2, Title1, year.

    Reference
    ---------
        Author3, Author4, Title2, year.

    Parameters
    ----------
    Stuff here.

    Returns
    -------
    More stuff."""
    assert extract_citation(docstring) == "Author1, Author2, Title1, year.\nAuthor3, Author4, Title2, year."


def test_extract_urls():
    """Test that we can extract urls from a docstring."""
    # Check an empty docstring.
    assert extract_urls("") == []
    assert extract_urls(None) == []

    # Start with single line docstrings.
    assert extract_urls("https://my_paper_url") == ["https://my_paper_url"]
    assert extract_urls("Please cite: https://my_paper_url") == ["https://my_paper_url"]
    assert extract_urls("Citation:\n    http://my_paper_url") == ["http://my_paper_url"]
    assert extract_urls("Info: Nothing to see here") == []

    # Test multi-line docstrings.
    docstring = """Top material:
    Stuff here.

    Citation:
        https://my_paper_url1
        https://my_paper_url2

    Bottom material:
    More stuff."""
    assert extract_urls(docstring) == ["https://my_paper_url1", "https://my_paper_url2"]
