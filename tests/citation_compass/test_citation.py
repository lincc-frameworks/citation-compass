import fake_module
import pytest

from citation_compass import (
    cite_function,
    cite_inline,
    cite_object,
    find_in_citations,
    get_all_citations,
    get_used_citations,
    reset_used_citations,
    CitationContext,
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
    known_citations = [
        # The functions defined in this file.
        "test_citation.example_function_1: function_citation_1",
        "test_citation.example_function_2: function_citation_2",
        "test_citation.example_function_x: function_citation_x",
        # The items defined in fake_module.
        "fake_module: CitationCompass, 2025.",
        "fake_module.FakeClass.fake_method: A fake class method for testing.",
        "fake_module.FakeCitedClass: A 2nd fake class for testing.",
        "fake_module.InheritedFakeClass: A 3rd fake class for testing.",
    ]
    assert sorted(get_all_citations()) == sorted(known_citations)

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
    assert sorted(get_all_citations()) == sorted(known_citations)

    # We can add a citation without a label.
    @cite_function()
    def example_function_4():
        return 4

    assert example_function_4() == 4

    # Check we have added the citation.
    known_citations.append(
        "test_citation.test_citations_all.<locals>.example_function_4: No citation provided."
    )
    assert sorted(get_all_citations()) == sorted(known_citations)

    # We can add a citation without parentheses in the decorator.
    @cite_function
    def example_function_5():
        return 5

    assert example_function_5() == 5

    # Check we have added the citation.
    known_citations.append(
        "test_citation.test_citations_all.<locals>.example_function_5: No citation provided."
    )
    assert sorted(get_all_citations()) == sorted(known_citations)

    # We can add a citation that does not track used.
    @cite_function(track_used=False)
    def example_function_6():
        return 6

    assert example_function_6() == 6

    # Check we have added the citation.
    known_citations.append(
        "test_citation.test_citations_all.<locals>.example_function_6: No citation provided."
    )
    assert sorted(get_all_citations()) == sorted(known_citations)

    # Test adding a manual citation for an object.
    cite_inline("test_citation", "Citation string")
    assert "test_citation: Citation string" in get_all_citations()


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
    assert sorted(get_used_citations()) == sorted(used_citations)

    # We can use the functions as normal - add example_function_x.
    assert example_function_x(10) == 10
    used_citations.append("test_citation.example_function_x: function_citation_x")
    assert sorted(get_used_citations()) == sorted(used_citations)

    # Reusing a function (example_function_x) does not re-add it.
    assert example_function_x(-5) == -5
    assert example_function_x(15) == 15
    assert sorted(get_used_citations()) == sorted(used_citations)

    # Creating a new function doesn't mark it as used.
    @cite_function()
    def example_function_5():
        """Test"""
        return 5

    assert sorted(get_used_citations()) == sorted(used_citations)

    # We can use the function and it will be marked as used.
    assert example_function_5() == 5
    used_citations.append("test_citation.test_citations_used.<locals>.example_function_5: Test")
    assert sorted(get_used_citations()) == sorted(used_citations)

    # Using an uncited function doesn't add it to the list.
    _ = fake_module.fake_uncited_function()
    citations = get_used_citations()
    assert len(citations) == len(used_citations)
    for item in used_citations:
        assert item in citations

    # We can add a citation that does not track used. This function is
    # added to the "used" list immediately.
    @cite_function(track_used=False)
    def not_used():
        """Test"""
        return 6

    used_citations.append("test_citation.test_citations_used.<locals>.not_used: Test")
    assert sorted(get_used_citations()) == sorted(used_citations)
    assert not_used() == 6

    # We can manually cite an object.
    obj = fake_module.FakeClass()
    cite_object(obj)
    used_citations.append("fake_module.FakeClass: A fake class for testing.")

    # We can cite a class method.
    assert obj.fake_method() == 0
    used_citations.append("fake_module.FakeClass.fake_method: A fake class method for testing.")
    assert sorted(get_used_citations()) == sorted(used_citations)

    # The CitedClass is added to used the first time it is instantiated.
    obj2 = fake_module.FakeCitedClass()
    used_citations.append("fake_module.FakeCitedClass: A 2nd fake class for testing.")
    assert sorted(get_used_citations()) == sorted(used_citations)

    # Calling object methods does not change anything.
    assert obj2.fake_method() == 1
    assert sorted(get_used_citations()) == sorted(used_citations)

    # Instantiating the class again does not change anything.
    _ = fake_module.FakeCitedClass()
    assert sorted(get_used_citations()) == sorted(used_citations)

    # Instantiating a subclass adds that to the used list.
    _ = fake_module.InheritedFakeClass()
    used_citations.append("fake_module.InheritedFakeClass: A 3rd fake class for testing.")
    assert sorted(get_used_citations()) == sorted(used_citations)

    # Test adding a manual citation for an object.
    cite_inline("test_citation", "Citation string")
    assert "test_citation: Citation string" in get_used_citations()

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


def test_citation_context():
    """Test the CitationContext class."""
    reset_used_citations()

    # Add some global citations.
    _ = example_function_1()
    _ = example_function_2()
    assert len(get_used_citations()) == 2

    # We don't have a tracker for this context (yet).
    context_name = "my_context"
    with pytest.raises(KeyError):
        _ = get_used_citations(context_name)

    with CitationContext(context_name) as context:
        # Tracker now exists (with nothing in the context originally).
        assert get_used_citations(context_name) == []
        assert context.get_citations() == []

        # We can add something specific to that context.
        _ = example_function_x(10)
        citations = context.get_citations()
        assert len(citations) == 1
        assert "test_citation.example_function_x: function_citation_x" in citations

        # We can use multiple trackers.
        with CitationContext("subcontext") as context2:
            assert context.get_citations() == ["test_citation.example_function_x: function_citation_x"]
            assert context2.get_citations() == []

            _ = example_function_1()
            citations = context.get_citations()
            assert len(citations) == 2
            assert "test_citation.example_function_1: function_citation_1" in citations
            assert "test_citation.example_function_x: function_citation_x" in citations

            assert context2.get_citations() == ["test_citation.example_function_1: function_citation_1"]

        # The subcontext is now gone.
        with pytest.raises(KeyError):
            _ = get_used_citations("subcontext")

    # Test the tracker is automatically deleted.
    with pytest.raises(KeyError):
        _ = get_used_citations(context_name)

    # We can create a citation context without a name.
    with CitationContext() as context:
        assert len(context.name) > 0
