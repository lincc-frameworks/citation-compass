"""A helper module to collect citations from a software package."""

import sys

CITATION_REGISTRY_ALL = {}
CITATION_REGISTRY_USED = set()


class CitationEntry:
    """A (data)class to store information about a citation.

    Attributes
    ----------
    key : str
        The name of the module, function, or other aspect where the citation is needed.
    citation : str, optional
        The citation string.
    label : str, optional
        The (optional) user-defined label for the citation.
    """

    def __init__(self, key, citation=None, label=None):
        self.key = key
        self.citation = citation
        self.label = label

        if citation is None:
            if label is not None and len(label) > 0:
                self.citation = label
            else:
                self.citation = "No citation provided."

    def __hash__(self):
        return hash(self.key)

    def __str__(self):
        return f"{self.key}: {self.citation}"

    def __repr__(self):
        return f"{self.key}:\n{self.citation}"

    @classmethod
    def from_function(cls, func, label=None):
        """Create a CitationEntry from a function.

        Parameters
        ----------
        func : function
            The function to create the citation entry from.
        label : str, optional
            The (optional) user-defined label for the citation.

        Returns
        -------
        CitationEntry
            The citation entry.
        """
        # TODO: Parse the docstring to see if it has a specific citation.
        return cls(
            key=func.__qualname__,
            citation=func.__doc__,
            label=label,
        )


def cite_module(name, citation):
    """Add a citation to a entire module.

    Parameters
    ----------
    name : str
        The name of the module.
    citation : str
        The citation string.
    """
    CITATION_REGISTRY_ALL[name] = CitationEntry(name, citation)
    CITATION_REGISTRY_USED.add(name)


def cite_function(label=None):
    """A function wrapper for adding a citation to a function.

    Parameters
    ----------
    label : str
        The (optional) user-defined label for the citation.

    Returns
    -------
    function
        The wrapped function.
    """

    def decorator(func):
        def fun_wrapper(*args, **kwargs):
            # Save the citation as USED when it is first called.
            if func.__qualname__ not in CITATION_REGISTRY_USED:
                CITATION_REGISTRY_USED.add(func.__qualname__)
            return func(*args, **kwargs)

        # Save the citation as ALL when it is first defined.
        if func.__qualname__ not in CITATION_REGISTRY_ALL:
            citation = CitationEntry.from_function(func, label=label)
            CITATION_REGISTRY_ALL[func.__qualname__] = citation
        return fun_wrapper

    return decorator


def get_all_citations():
    """Return a list of all citations in the software package.

    Returns
    -------
    citations : list of str
        A list of all citations in the software package.
    """
    citations = []
    for entry in CITATION_REGISTRY_ALL.values():
        citations.append(str(entry))
    return citations


def get_used_citations():
    """Return a list of all citations in the software package.

    Returns
    -------
    list of str
        A list of all citations in the software package.
    """
    citations = []
    for func_name in CITATION_REGISTRY_USED:
        citations.append(str(CITATION_REGISTRY_ALL[func_name]))
    return citations


def reset_used_citations():
    """Reset the list of used citations."""
    CITATION_REGISTRY_USED.clear()


def get_all_imports(skip_common=True):
    """Return a list of all imports in the software package.

    Parameters
    ----------
    skip_common : bool
        Whether to skip the common imports, such as the built-in modules.

    Returns
    -------
    imports : list of str
        A list of all imports in the software package.
    """
    imports = []
    for name, module in sys.modules.items():
        skip = False
        if name == "__main__":
            # Skip the main module
            skip = True
        elif hasattr(module, "__spec__") and module.__spec__ is not None:
            # Skip the built-in modules or ones from the python framework.
            origin = module.__spec__.origin
            if origin == "built-in":
                skip = True
            if origin == "frozen":
                skip = True
            if "Python.framework" in origin:
                skip = True

        if not skip_common or not skip:
            imports.append(name)
    return imports
