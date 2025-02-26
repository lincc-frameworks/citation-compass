"""Fake module for testing.

Citation: CitationCompass, 2025.
"""

from citation_compass import cite_module, cite_function, CiteClass

cite_module(__name__)


def fake_uncited_function():
    """This is a fake function for testing purposes."""
    return 0


class FakeClass:
    """A fake class for testing."""

    def __init__(self):
        pass

    @cite_function
    def fake_method(self):
        """A fake class method for testing."""
        return 0


class FakeCitedClass(CiteClass):
    """A 2nd fake class for testing."""

    def __init__(self):
        pass

    def fake_method(self):
        """A fake (uncited) class method for testing."""
        return 1
