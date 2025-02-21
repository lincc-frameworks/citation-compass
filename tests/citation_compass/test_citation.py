import fake_module
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


def test_citations_all():
    """Check that all the citations are registered."""
    citations = get_all_citations()
    assert len(citations) == 4
    assert "example_function_1: function_citation_1" in citations
    assert "example_function_2: function_citation_2" in citations
    assert "example_function_x: function_citation_x" in citations
    assert "fake_module: Fake module citation." in citations

    # A citation with no docstring, but a label.
    @cite_function("function_citation_3")
    def example_function_3():
        return 3

    citations = get_all_citations()
    assert len(citations) == 5
    assert "example_function_1: function_citation_1" in citations
    assert "example_function_2: function_citation_2" in citations
    assert "test_citations_all.<locals>.example_function_3: function_citation_3" in citations
    assert "example_function_x: function_citation_x" in citations
    assert example_function_3() == 3

    # We can add a citation without a label.
    @cite_function()
    def example_function_4():
        return 4

    citations = get_all_citations()
    assert len(citations) == 6
    assert "example_function_1: function_citation_1" in citations
    assert "example_function_2: function_citation_2" in citations
    assert "test_citations_all.<locals>.example_function_3: function_citation_3" in citations
    assert "test_citations_all.<locals>.example_function_4: No citation provided." in citations
    assert "example_function_x: function_citation_x" in citations
    assert example_function_4() == 4


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
    assert "example_function_1: function_citation_1" in citations

    assert example_function_x(10) == 10
    citations = get_used_citations()
    assert len(citations) == 2
    assert "example_function_1: function_citation_1" in citations
    assert "example_function_x: function_citation_x" in citations

    # Reusing a function does not re-add it.
    assert example_function_x(-5) == -5
    citations = get_used_citations()
    assert len(citations) == 2
    assert "example_function_1: function_citation_1" in citations
    assert "example_function_x: function_citation_x" in citations

    # Creating a new function doesn't mark it as used.
    @cite_function()
    def example_function_5():
        return 5

    citations = get_used_citations()
    assert len(citations) == 2
    assert "example_function_1: function_citation_1" in citations
    assert "example_function_x: function_citation_x" in citations

    # We can reset the list of used citation functions.
    reset_used_citations()
    assert len(get_used_citations()) == 0


def test_get_all_imports():
    """Check that the imports are registered."""
    imports = get_all_imports(skip_common=False)
    assert len(imports) > 0
    assert "sys" in imports

    # We can filter out Python's base imports.
    imports = get_all_imports(skip_common=True)
    assert len(imports) > 0
    assert "sys" not in imports
