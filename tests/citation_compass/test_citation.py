from citation_compass.citation import (
    citation,
    get_all_citations,
    get_all_imports,
    get_used_citations,
    reset_used_citations,
)


@citation("function_citation_1")
def example_function_1():
    """Test function that returns 1."""
    return 1


@citation("function_citation_2")
def example_function_2():
    """Test function that returns 2."""
    return 2


@citation("function_citation_x")
def example_function_x(x):
    """Test function that returns the input value."""
    return x


def test_citations_all():
    """Check that all the citations are registered."""
    citations = get_all_citations()
    assert len(citations) == 3
    assert "example_function_1: function_citation_1" in citations
    assert "example_function_2: function_citation_2" in citations
    assert "example_function_x: function_citation_x" in citations


def test_citations_new():
    """Check that new citations are registered."""

    @citation("function_citation_3")
    def example_function_3():
        return 3

    citations = get_all_citations()
    print(citations)
    assert len(citations) == 4
    assert "example_function_1: function_citation_1" in citations
    assert "example_function_2: function_citation_2" in citations
    assert "test_citations_new.<locals>.example_function_3: function_citation_3" in citations
    assert "example_function_x: function_citation_x" in citations
    assert example_function_3() == 3

    # We can add a citation without a label.
    @citation()
    def example_function_4():
        return 4

    citations = get_all_citations()
    assert len(citations) == 5
    assert "example_function_1: function_citation_1" in citations
    assert "example_function_2: function_citation_2" in citations
    assert "test_citations_new.<locals>.example_function_3: function_citation_3" in citations
    assert "test_citations_new.<locals>.example_function_4: No citation provided." in citations
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

    # We can reset the list of used citation functions.
    reset_used_citations()
    assert len(get_used_citations()) == 0


def test_get_all_imports():
    """Check that the imports are registered."""
    imports = get_all_imports(skip_common=False)
    assert len(imports) > 0
    assert "sys" in imports
