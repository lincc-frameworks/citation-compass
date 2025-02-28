import pytest

from citation_compass.citation_registry import (
    get_object_full_name,
    CitationEntry,
    CitationRegistry,
)


def example_function_1():
    """function_citation_1"""
    return 1


class ExampleClass:
    """A fake class for testing."""

    def __init__(self):
        pass

    def example_method(self):
        """A fake class method for testing."""
        return 0


def test_get_object_full_name():
    """Check that the full name is correctly generated."""
    assert get_object_full_name(example_function_1) == "test_citation_registry.example_function_1"
    assert (
        get_object_full_name(get_object_full_name)
        == "citation_compass.citation_registry.get_object_full_name"
    )
    assert get_object_full_name(ExampleClass) == "test_citation_registry.ExampleClass"
    assert (
        get_object_full_name(ExampleClass.example_method)
        == "test_citation_registry.ExampleClass.example_method"
    )

    obj = ExampleClass()
    assert get_object_full_name(obj) == "test_citation_registry.ExampleClass"
    assert get_object_full_name(obj.example_method) == "test_citation_registry.ExampleClass.example_method"


def test_citations_entry():
    """Check that we can create and query a citation entry."""
    entry = CitationEntry("key", "citation", "label")
    assert entry.key == "key"
    assert entry.citation == "citation"

    # If no citation is provided, the label is used.
    entry = CitationEntry("key", None, "label")
    assert entry.citation == "label"

    # We automatically extract URLs.
    entry = CitationEntry("key", "http://example.com")
    assert entry.urls == ["http://example.com"]

    # We can create a citation entry from an object.
    entry = CitationEntry.from_object(example_function_1)
    assert entry.key == "test_citation_registry.example_function_1"
    assert entry.citation == "function_citation_1"


def test_citations_registry():
    """Test that we can create and query a citation registry."""
    reg = CitationRegistry()
    assert len(reg) == 0

    # We can add a citation entry as a CitationEntry object.
    reg.add("key1", CitationEntry("key1", "citation1"))
    assert len(reg) == 1
    assert "key1" in reg
    assert reg["key1"].citation == "citation1"
    assert len(reg.get_all_citations()) == 1
    assert reg.get_all_citations()[0].key == "key1"

    # We can add a citation entry as a citation string.
    reg.add("key2", "citation2")
    assert len(reg) == 2
    assert "key2" in reg
    assert reg["key2"].citation == "citation2"
    assert len(reg.get_all_citations()) == 2

    # We can add a citation entry from an object.
    reg.add("key3", example_function_1)
    assert len(reg) == 3
    assert "key3" in reg
    assert reg["key3"].citation == "function_citation_1"
    assert len(reg.get_all_citations()) == 3

    # We can mark an entry as used.
    assert len(reg.get_used_citations()) == 0
    reg.mark_used("key1")
    assert len(reg.get_used_citations()) == 1
    assert reg.get_used_citations()[0].key == "key1"

    # We can add a custom tracker. Initially it has nothing seen.
    assert reg.num_trackers() == 1
    reg.start_used_tracker("tracker1")
    assert reg.num_trackers() == 2
    assert len(reg.get_used_citations()) == 1
    assert len(reg.get_used_citations("tracker1")) == 0

    # We can mark an entry as used in a custom tracker.
    reg.mark_used("key2")
    assert len(reg.get_used_citations()) == 2  # Global has 2
    assert len(reg.get_used_citations("tracker1")) == 1

    # We can reset the used citations for a tracker.
    reg.reset_used_citations("tracker1")
    assert len(reg.get_used_citations()) == 2  # Global still has 2
    assert len(reg.get_used_citations("tracker1")) == 0

    # We can re-mark an entry as used in a custom tracker.
    reg.mark_used("key2")
    assert len(reg.get_used_citations()) == 2  # Global still has 2
    assert len(reg.get_used_citations("tracker1")) == 1

    # We can't start another tracker with the same name.
    with pytest.raises(KeyError):
        reg.start_used_tracker("tracker1")

    # We can stop a tracker and get the used citations.
    used = reg.stop_used_tracker("tracker1")
    assert len(used) == 1
    assert used[0].key == "key2"
    assert len(reg.get_used_citations()) == 2  # Global still has 2

    assert reg.num_trackers() == 1
    with pytest.raises(KeyError):
        _ = reg.get_used_citations("tracker1")

    # We cannot stop or reset trackers that do not exist.
    with pytest.raises(KeyError):
        _ = reg.stop_used_tracker("tracker2")
    with pytest.raises(KeyError):
        reg.reset_used_citations("tracker2")
