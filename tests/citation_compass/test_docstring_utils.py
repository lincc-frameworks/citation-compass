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
    assert extract_citation(docstring) == "Author1, Author2, Title, journal, year"


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
    assert extract_citation(docstring) == "Author1, Author2, Title, year"


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
