import fake_module

from citation_compass.citation import _get_full_name
from citation_compass import (
    cite_function,
    get_all_citations,
    get_all_imports,
    get_used_citations,
    reset_used_citations,
)


@cite_function()
def example_function_1():
    """function_citation_1"""
    return 1


@cite_function()
def example_function_2():
    """function_citation_2"""
    return 2


@cite_function()
def example_function_x(x):
    """function_citation_x"""
    return x


def test_get_full_name():
    """Check that the full name is correctly generated."""
    assert _get_full_name(example_function_1) == "test_citation.example_function_1"
    assert _get_full_name(_get_full_name) == "citation_compass.citation._get_full_name"
    assert _get_full_name(fake_module.fake_function) == "fake_module.fake_function"


def test_citations_all():
    """Check that all the citations are registered."""
    citations = get_all_citations()
    assert len(citations) == 4
    assert "test_citation.example_function_1: function_citation_1" in citations
    assert "test_citation.example_function_2: function_citation_2" in citations
    assert "test_citation.example_function_x: function_citation_x" in citations
    assert "fake_module: CitationCompass, 2025." in citations

    # Check that we have preserved the name and __doc__ string of the function
    # through the wrapping process.
    assert example_function_1.__name__ == "example_function_1"
    assert example_function_1.__doc__ == "function_citation_1"
    assert example_function_2.__name__ == "example_function_2"
    assert example_function_2.__doc__ == "function_citation_2"
    assert example_function_x.__name__ == "example_function_x"
    assert example_function_x.__doc__ == "function_citation_x"

    # A citation with no docstring, but a label.
    @cite_function("function_citation_3")
    def example_function_3():
        return 3

    citations = get_all_citations()
    assert len(citations) == 5
    assert "test_citation.example_function_1: function_citation_1" in citations
    assert "test_citation.example_function_2: function_citation_2" in citations
    assert "test_citation.test_citations_all.<locals>.example_function_3: function_citation_3" in citations
    assert "test_citation.example_function_x: function_citation_x" in citations
    assert example_function_3() == 3

    # We can add a citation without a label.
    @cite_function()
    def example_function_4():
        return 4

    citations = get_all_citations()
    assert len(citations) == 6
    assert "test_citation.example_function_1: function_citation_1" in citations
    assert "test_citation.example_function_2: function_citation_2" in citations
    assert "test_citation.test_citations_all.<locals>.example_function_3: function_citation_3" in citations
    assert "test_citation.test_citations_all.<locals>.example_function_4: No citation provided." in citations
    assert "test_citation.example_function_x: function_citation_x" in citations
    assert example_function_4() == 4

    # We can add a citation without parentheses.
    @cite_function
    def example_function_5():
        return 5

    citations = get_all_citations()
    assert len(citations) == 7
    assert "test_citation.example_function_1: function_citation_1" in citations
    assert "test_citation.example_function_2: function_citation_2" in citations
    assert "test_citation.test_citations_all.<locals>.example_function_3: function_citation_3" in citations
    assert "test_citation.test_citations_all.<locals>.example_function_4: No citation provided." in citations
    assert "test_citation.test_citations_all.<locals>.example_function_5: No citation provided." in citations
    assert "test_citation.example_function_x: function_citation_x" in citations
    assert example_function_5() == 5


def test_citations_used():
    """Check that the used citations are registered as they are used."""
    # Start by resetting the list of used citations, because they may
    # have been used in previous tests.
    reset_used_citations()
    assert len(get_used_citations()) == 0

    # We can use the functions as normal.
    assert example_function_1() == 1
    citations = get_used_citations()
    assert len(citations) == 1
    assert "test_citation.example_function_1: function_citation_1" in citations

    assert example_function_x(10) == 10
    citations = get_used_citations()
    assert len(citations) == 2
    assert "test_citation.example_function_1: function_citation_1" in citations
    assert "test_citation.example_function_x: function_citation_x" in citations

    # Reusing a function does not re-add it.
    assert example_function_x(-5) == -5
    citations = get_used_citations()
    assert len(citations) == 2
    assert "test_citation.example_function_1: function_citation_1" in citations
    assert "test_citation.example_function_x: function_citation_x" in citations

    # Creating a new function doesn't mark it as used.
    @cite_function()
    def example_function_5():
        return 5

    citations = get_used_citations()
    assert len(citations) == 2
    assert "test_citation.example_function_1: function_citation_1" in citations
    assert "test_citation.example_function_x: function_citation_x" in citations

    # Using an uncited function doesn't add it to the list.
    _ = fake_module.fake_function()
    citations = get_used_citations()
    assert len(citations) == 2

    # We can reset the list of used citation functions.
    reset_used_citations()
    assert len(get_used_citations()) == 0


def test_get_all_imports():
    """Check that the imports are registered."""
    imports = get_all_imports(skip_common=False)
    assert len(imports) > 0
    assert "sys" in imports
    assert "fake_module" in imports

    # We can filter out Python's base imports.
    imports = get_all_imports(skip_common=True)
    assert len(imports) > 0
    assert "sys" not in imports
    assert "fake_module" in imports

    # We can search for citation keywords in the module docstrings.
    old_len = len(imports)
    imports = get_all_imports(skip_common=True, use_keywords=True)
    assert len(imports) > 0
    assert len(imports) < old_len
    assert "fake_module" in imports
