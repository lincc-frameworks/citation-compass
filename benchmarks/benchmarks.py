"""Two sample benchmarks to compute runtime and memory usage.

For more information on writing benchmarks:
https://asv.readthedocs.io/en/stable/writing_benchmarks.html."""

import citation_compass as cc


@cc.cite_function("fake")
def fake_function():
    """A fake function to demonstrate the use of the citation_compass package."""
    return 1


def time_create_function():
    """Time the use of a wrapper with a label."""

    @cc.cite_function("example")
    def test_function():
        return 1


def time_call_function():
    """Time the cost of calling a wrapped function."""
    _ = fake_function()
