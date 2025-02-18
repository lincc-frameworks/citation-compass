import pytest
from cite_by_function.citation_utils import (
    citation,
    get_all_citations,
    get_used_citations,
)


@citation(reference="function_citation_1")
def example_function_1():
    """Test function that returns 1."""
    return 1


@citation(reference="function_citation_2")
def example_function_2():
    """Test function that returns 2."""
    return 2


@citation(reference="function_citation_x")
def example_function_x(x):
    """Test function that returns the input value."""
    return x


def test_citations_all():
    """Check that all the citations are registered."""
    citations = get_all_citations()
    assert len(citations) == 3
    assert "function_citation_1: test_citation_utils.example_function_1" in citations
    assert "function_citation_2: test_citation_utils.example_function_2" in citations
    assert "function_citation_x: test_citation_utils.example_function_x" in citations

    citations = get_all_citations(include_imports=True)
    assert len(citations) > 3
    assert "function_citation_1: test_citation_utils.example_function_1" in citations
    assert "function_citation_2: test_citation_utils.example_function_2" in citations
    assert "function_citation_x: test_citation_utils.example_function_x" in citations
    assert "import: sys" in citations


def test_citations_duplicate():
    """Check that we have an error when duplicate citation references are used."""
    with pytest.raises(ValueError):

        @citation(reference="function_citation_1")
        def example_function_4():
            return 4


def test_citations_used():
    """Check that the used citations are registered as they are used."""
    assert len(get_used_citations()) == 0

    # We can use the functions as normal.
    assert example_function_1() == 1
    citations = get_used_citations()
    assert len(citations) == 1
    assert "function_citation_1: test_citation_utils.example_function_1" in citations

    assert example_function_x(10) == 10
    citations = get_used_citations()
    assert len(citations) == 2
    assert "function_citation_1: test_citation_utils.example_function_1" in citations
    assert "function_citation_x: test_citation_utils.example_function_x" in citations

    # Reusing a function does not re-add it.
    assert example_function_x(-5) == -5
    citations = get_used_citations()
    assert len(citations) == 2
    assert "function_citation_1: test_citation_utils.example_function_1" in citations
    assert "function_citation_x: test_citation_utils.example_function_x" in citations

    # We get a longer list when including imports.
    citations = get_used_citations(include_imports=True)
    assert len(citations) > 2
    assert "function_citation_1: test_citation_utils.example_function_1" in citations
    assert "function_citation_x: test_citation_utils.example_function_x" in citations
    assert "import: sys" in citations
