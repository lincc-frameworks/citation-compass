import fake_module

from citation_compass.citation import _get_full_name
from citation_compass import (
    cite_function,
    cite_object,
    find_in_citations,
    get_all_citations,
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
    assert _get_full_name(fake_module.fake_uncited_function) == "fake_module.fake_uncited_function"
    assert _get_full_name(fake_module.FakeClass) == "fake_module.FakeClass"

    obj = fake_module.FakeClass()
    assert _get_full_name(obj) == "fake_module.FakeClass"
    assert _get_full_name(obj.fake_method) == "fake_module.FakeClass.fake_method"


def test_citations_all():
    """Check that all the citations are registered."""
    known_citations = [
        # The functions defined in this file.
        "test_citation.example_function_1: function_citation_1",
        "test_citation.example_function_2: function_citation_2",
        "test_citation.example_function_x: function_citation_x",
        # The items defined in fake_module.
        "fake_module: CitationCompass, 2025.",
        "fake_module.FakeClass.fake_method: A fake class method for testing.",
        "fake_module.FakeCitedClass: A 2nd fake class for testing.",
    ]

    citations = get_all_citations()
    assert len(citations) == len(known_citations)
    for item in known_citations:
        assert item in citations

    # Check that we have preserved the name and __doc__ string of the function
    # through the wrapping process.
    assert example_function_1.__name__ == "example_function_1"
    assert example_function_1.__doc__ == "function_citation_1"
    assert example_function_2.__name__ == "example_function_2"
    assert example_function_2.__doc__ == "function_citation_2"
    assert example_function_x.__name__ == "example_function_x"
    assert example_function_x.__doc__ == "function_citation_x"

    assert fake_module.FakeCitedClass.__name__ == "FakeCitedClass"
    assert fake_module.FakeCitedClass.__doc__ == "A 2nd fake class for testing."
    obj = fake_module.FakeCitedClass()
    assert isinstance(obj, fake_module.FakeCitedClass)

    # A citation with no docstring, but a label.
    @cite_function("function_citation_3")
    def example_function_3():
        return 3

    assert example_function_3() == 3

    # Check we have added the citation.
    known_citations.append(
        "test_citation.test_citations_all.<locals>.example_function_3: function_citation_3"
    )
    citations = get_all_citations()
    assert len(citations) == len(known_citations)
    for item in known_citations:
        assert item in citations

    # We can add a citation without a label.
    @cite_function()
    def example_function_4():
        return 4

    assert example_function_4() == 4

    # Check we have added the citation.
    known_citations.append(
        "test_citation.test_citations_all.<locals>.example_function_4: No citation provided."
    )
    citations = get_all_citations()
    assert len(citations) == len(known_citations)
    for item in known_citations:
        assert item in citations

    # We can add a citation without parentheses in the decorator.
    @cite_function
    def example_function_5():
        return 5

    assert example_function_5() == 5

    # Check we have added the citation.
    known_citations.append(
        "test_citation.test_citations_all.<locals>.example_function_5: No citation provided."
    )
    citations = get_all_citations()
    assert len(citations) == len(known_citations)
    for item in known_citations:
        assert item in citations

    # We can add a citation that does not track used.
    @cite_function(track_used=False)
    def example_function_6():
        return 6

    assert example_function_6() == 6

    # Check we have added the citation.
    known_citations.append(
        "test_citation.test_citations_all.<locals>.example_function_6: No citation provided."
    )
    citations = get_all_citations()
    assert len(citations) == len(known_citations)
    for item in known_citations:
        assert item in citations


def test_citations_used():
    """Check that the used citations are registered as they are used."""
    # Start by resetting the list of used citations, because they may
    # have been used in previous tests.
    reset_used_citations()
    used_citations = []
    assert len(get_used_citations()) == 0

    # We can use the functions as normal - add example_function_1.
    assert example_function_1() == 1
    used_citations.append("test_citation.example_function_1: function_citation_1")

    citations = get_used_citations()
    assert len(citations) == len(used_citations)
    for item in used_citations:
        assert item in citations

    # We can use the functions as normal - add example_function_x.
    assert example_function_x(10) == 10
    used_citations.append("test_citation.example_function_x: function_citation_x")

    citations = get_used_citations()
    assert len(citations) == len(used_citations)
    for item in used_citations:
        assert item in citations

    # Reusing a function (example_function_x) does not re-add it.
    assert example_function_x(-5) == -5
    assert example_function_x(15) == 15
    citations = get_used_citations()
    assert len(citations) == len(used_citations)
    for item in used_citations:
        assert item in citations

    # Creating a new function doesn't mark it as used.
    @cite_function()
    def example_function_5():
        """Test"""
        return 5

    citations = get_used_citations()
    assert len(citations) == len(used_citations)
    for item in used_citations:
        assert item in citations

    # We can use the function and it will be marked as used.
    assert example_function_5() == 5
    used_citations.append("test_citation.test_citations_used.<locals>.example_function_5: Test")

    citations = get_used_citations()
    assert len(citations) == len(used_citations)
    for item in used_citations:
        assert item in citations

    # Using an uncited function doesn't add it to the list.
    _ = fake_module.fake_uncited_function()
    citations = get_used_citations()
    assert len(citations) == len(used_citations)
    for item in used_citations:
        assert item in citations

    # We can add a citation that does not track used.
    @cite_function(track_used=False)
    def example_function_no_track_used():
        return 6

    assert example_function_no_track_used() == 6

    citations = get_used_citations()
    assert len(citations) == len(used_citations)
    for item in used_citations:
        assert item in citations

    # We can manually cite an object.
    obj = fake_module.FakeClass()
    cite_object(obj)
    used_citations.append("fake_module.FakeClass: A fake class for testing.")

    citations = get_used_citations()
    assert len(citations) == len(used_citations)
    for item in used_citations:
        assert item in citations

    # We can cite a class method.
    assert obj.fake_method() == 0
    used_citations.append("fake_module.FakeClass.fake_method: A fake class method for testing.")

    citations = get_used_citations()
    assert len(citations) == len(used_citations)
    for item in used_citations:
        assert item in citations

    # The CitedClass is added to used the first time it is instantiated.
    obj2 = fake_module.FakeCitedClass()
    used_citations.append("fake_module.FakeCitedClass: A 2nd fake class for testing.")
    citations = get_used_citations()
    assert len(citations) == len(used_citations)
    for item in used_citations:
        assert item in citations

    # Calling object methods does not change anything.
    assert obj2.fake_method() == 1
    assert len(get_used_citations()) == len(used_citations)

    # Instantiating the class again does not change anything.
    _ = fake_module.FakeCitedClass()
    assert len(get_used_citations()) == len(used_citations)

    # We can reset the list of used citation functions.
    reset_used_citations()
    assert len(get_used_citations()) == 0


def test_find_in_citations():
    """Test the find_in_citations() function."""

    # Test we can find text by the key.
    assert len(find_in_citations("function_citation_1")) == 1
    assert len(find_in_citations("function_citation_2")) == 1
    assert len(find_in_citations("function_citation_300")) == 0
    assert len(find_in_citations("function")) >= 3
    assert len(find_in_citations("FakeCitedClass")) == 1

    # Test we can find text by the citation.
    assert len(find_in_citations("A 2nd fake class for testing.")) == 1
    assert len(find_in_citations("A fake class method for testing.")) == 1
    assert len(find_in_citations("This string does not exist.")) == 0

    # Check used citations.
    reset_used_citations()
    assert len(find_in_citations("function_citation_1", True)) == 0
    assert len(find_in_citations("FakeCitedClass", True)) == 0
    assert len(find_in_citations("A 2nd fake class for testing.", True)) == 0

    _ = example_function_1()
    assert len(find_in_citations("function_citation_1", True)) == 1

    _ = fake_module.FakeCitedClass()
    assert len(find_in_citations("FakeCitedClass", True)) == 1
