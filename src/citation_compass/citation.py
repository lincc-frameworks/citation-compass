"""A helper module to collect citations from a software package."""

from functools import wraps
from os import urandom
import sys
import types

from citation_compass.citation_registry import (
    CitationEntry,
    CITATION_COMPASS_REGISTRY,
)
from citation_compass.docstring_utils import extract_citation


def cite_inline(name, citation):
    """Add a manual citation entry. This is used when the citation is specific
    to a block of code (e.g. an if-else statement) instead of a function or class.

    Parameters
    ----------
    name : str
        The name of the citation entry. This should be unique key.
    citation : str
        The citation text.
    """
    entry = CitationEntry(name, citation)
    CITATION_COMPASS_REGISTRY.add(entry)
    CITATION_COMPASS_REGISTRY.mark_used(name)


def cite_module(name, citation=None):
    """Add a citation to a entire module.

    Parameters
    ----------
    name : str
        The name of the module.
    citation : str, optional
        The citation string. If None the code automatically tries to extract the citation text
        from the module's docstring.
    """
    if citation is None and name in sys.modules:
        module = sys.modules[name]
        if hasattr(module, "__doc__"):
            citation = extract_citation(module.__doc__)
            if citation is None or len(citation) == 0:
                citation = module.__doc__

    entry = CitationEntry(name, citation)
    CITATION_COMPASS_REGISTRY.add(entry)
    CITATION_COMPASS_REGISTRY.mark_used(name)


class CiteClass:
    """A super class for adding a citation to a class."""

    def __init__(self):
        pass

    def __init_subclass__(cls):
        entry = CitationEntry.from_object(cls)
        cls._citation_compass_name = entry.key
        CITATION_COMPASS_REGISTRY.add(entry)

        # Wrap the constructor so the class is marked used when
        # the first object is instantiated.
        original_init = cls.__init__

        @wraps(original_init)
        def init_wrapper(*args, **kwargs):
            # Save the citation as USED when it is first called.
            CITATION_COMPASS_REGISTRY.mark_used(cls._citation_compass_name)
            return original_init(*args, **kwargs)

        cls.__init__ = init_wrapper


def cite_function(callable=None, *, label=None, track_used=True):
    """A function wrapper for adding a citation to a function or
    class method.

    Parameters
    ----------
    callable : function or method, optional
        The function or method to add a citation to. This is automatically passed as
        the first argument when using the decorator without parentheses.
    label : str, optional
        The (optional) user-defined label for the citation. If not provided,
        the label will be auto-extracted from the function's docstring.
    track_used : bool
        If True, the function will be marked as used when it is called.
        This adds a small amount of overhead to each function call.
        Default: True.

    Returns
    -------
    function
        The wrapped function or method.
    """
    # This decorator is designed as a two-layer decorator. The first layer handles the (optional)
    # arguments. The second handles the actual function wrapping.

    def _inner_decorator(callable):
        # The inner decorator is used to set the "all" citations entry and handle
        # the correct return types when wrapping the function.

        # Add the function to the registry (for the "all" citations).
        entry = CitationEntry.from_object(callable, label=label)
        CITATION_COMPASS_REGISTRY.add(entry)

        # If we are not tracking when the function is used, we don't need to wrap it.
        # We can just return the original callable.
        if not track_used:
            # We mark as used by default so the citation does not get dropped.
            CITATION_COMPASS_REGISTRY.mark_used(entry.key)
            return callable

        # If the callable is a classmethod or method, we need to get the function that has
        # the self or cls argument.
        func = callable.__func__ if isinstance(callable, (classmethod, types.MethodType)) else callable

        # Define the actual wrapper for the callable we passed in. This wrapper function will
        # be called each time the internal function is called.
        @wraps(func)
        def citation_wrapper(*args, **kwargs):
            # Save the citation as USED when it is first called.
            CITATION_COMPASS_REGISTRY.mark_used(entry.key)
            return func(*args, **kwargs)

        # We cast the wrapped function as the correct type.
        if isinstance(callable, classmethod):
            return classmethod(citation_wrapper)
        elif isinstance(callable, staticmethod):
            return staticmethod(citation_wrapper)
        elif isinstance(callable, types.MethodType):
            return types.MethodType(citation_wrapper, callable.__self__)
        return citation_wrapper

    # Handle the optional parentheses in the decorator.
    return _inner_decorator if callable is None else _inner_decorator(callable)


def cite_object(obj, label=None):
    """Add a citation for a specific object.

    Parameters
    ----------
    obj : object
        The object to add a citation for.
    label : str, optional
        The (optional) user-defined label for the citation.
    """
    entry = CitationEntry.from_object(obj, label=label)
    CITATION_COMPASS_REGISTRY.add(entry)
    CITATION_COMPASS_REGISTRY.mark_used(entry.key)


class CitationContext:
    """A context manager for tracking citations used within a block of code.

    Parameters
    ----------
    name : str, optional
        The name of the tracker. If None, a random name is generated.
    """

    def __init__(self, name=None):
        if name is None:
            # If no name is given, generate a random one.
            name = str(urandom(4))
        self.name = name

    def __enter__(self):
        CITATION_COMPASS_REGISTRY.start_used_tracker(self.name)
        return self

    def __exit__(self, *args):
        CITATION_COMPASS_REGISTRY.stop_used_tracker(self.name)

    def get_citations(self):
        """Return a list of all citations used within the context manager."""
        return [str(entry) for entry in CITATION_COMPASS_REGISTRY.get_used_citations(self.name)]


def get_all_citations():
    """Return a list of all citations in the software package.

    Returns
    -------
    citations : list of str
        A list of all citations in the software package.
    """
    citations = [str(entry) for entry in CITATION_COMPASS_REGISTRY.get_all_citations()]
    return citations


def get_used_citations(tracker_name=None):
    """Return a list of all citations in the software package.

    Parameters
    ----------
    tracker_name : str, optional
        The name of the tracker to get the used citations for.
        If None, the global tracker is used.

    Returns
    -------
    list of str
            A list of the citations used within the scope of the tracker.
    """
    citations = [str(entry) for entry in CITATION_COMPASS_REGISTRY.get_used_citations(tracker_name)]
    return citations


def find_in_citations(query, used_only=False, tracker_name=None):
    """Find a query string in the citation text. This is primarily used for
    testing, where a user might want to check if a citation is present.

    Parameters
    ----------
    query : str
        The query string to search for.
    used_only : bool, optional
        If True, only search in the used citations. If False, search in all citations.
    tracker_name : str, optional
        The name of the tracker to get the used citations for. Ignored if used_only is False.
        If None, and used_only=True, the global tracker is used.

    Returns
    -------
    matches : list of str
        A list of matching citation strings. This list is empty if no matches are found.
    """
    search_set = get_used_citations(tracker_name) if used_only else get_all_citations()
    matches = []
    for entry in search_set:
        if query in entry:
            matches.append(entry)
    return matches


def reset_used_citations(tracker_name=None):
    """Reset the list of used citations.

    Parameters
    ----------
    tracker_name : str, optional
        The name of the tracker to reset. If None, the global tracker is reset.
    """
    CITATION_COMPASS_REGISTRY.reset_used_citations(tracker_name)


def print_all_citations():
    """Print all citations in the software package in a user-friendly way."""
    for entry in CITATION_COMPASS_REGISTRY.get_all_citations():
        print(f"{entry.key}:\n{entry.citation}\n")


def print_used_citations(tracker_name=None):
    """Print the used citations in the software package in a user-friendly way.

    Parameters
    ----------
    tracker_name : str, optional
        The name of the tracker to reset. If None, the global tracker is reset.
    """
    for entry in CITATION_COMPASS_REGISTRY.get_used_citations(tracker_name):
        print(f"{entry.key}:\n{entry.citation}\n")
