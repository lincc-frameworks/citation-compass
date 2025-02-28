"""Two sample benchmarks to compute runtime and memory usage.

For more information on writing benchmarks:
https://asv.readthedocs.io/en/stable/writing_benchmarks.html."""

import citation_compass as cc


@cc.cite_function("fake")
def fake_function():
    """A fake function to demonstrate the use of the citation_compass package."""
    return 1


@cc.cite_function("fake", track_used=False)
def fake_function2():
    """A fake function to demonstrate the use of the citation_compass package."""
    return 1


class FakeClass(cc.CiteClass):
    """A fake class for benchmarking."""

    def __init__(self):
        pass


def time_create_function():
    """Time the use of a wrapper with a label."""

    @cc.cite_function("example")
    def test_function():
        return 1


def time_call_function():
    """Time the cost of calling a wrapped function."""
    _ = fake_function()


def time_call_function_untracked():
    """Time the cost of calling an untracked function."""
    _ = fake_function2()


def time_instantiate_class():
    """Time the cost of instantiating a class with a wrapped method."""
    _ = FakeClass()


def time_cite_module():
    """Time the cost of citing a module."""
    cc.cite_module("citation_compass")
