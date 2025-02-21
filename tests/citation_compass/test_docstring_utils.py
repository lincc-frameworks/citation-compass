from citation_compass.docstring_utils import (
    _CITATION_KEYWORDS,
    check_docstring_for_keyword,
    extract_citation,
)


def test_check_docstring_for_keyword():
    """Check that the function correctly identifies citation keywords."""
    assert check_docstring_for_keyword("This is a docstring.") is False
    assert check_docstring_for_keyword("This is a citation.") is True
    assert check_docstring_for_keyword("This is a reference.") is True

    for keyword in _CITATION_KEYWORDS:
        assert check_docstring_for_keyword(f"{keyword}: other stuff") is True

    # Check empty docstrings.
    assert check_docstring_for_keyword("") is False
    assert check_docstring_for_keyword(None) is False


def test_extract_citation():
    """Test that we can extract a citation from a docstring."""
    # Check an empty docstring.
    assert extract_citation("") is None
    assert extract_citation(None) is None

    # Start with single line docstrings.
    assert extract_citation("Citation: Author, Title, year.") == "Author, Title, year."
    assert extract_citation("Reference: Author, Title, year.") == "Author, Title, year."
    assert extract_citation("Acknowledge: Author, Title, year.") == "Author, Title, year."
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

    Acknowledgements:
        Author1, Author2,
        Title,
        journal,
        year
    """
    assert extract_citation(docstring) == "Author1, Author2, Title, journal, year"
