"""A helper module to collect citations from a software package."""

import sys

CITATION_REGISTRY_ALL = {}
CITATION_REGISTRY_USED = set()


class CitationEntry:
    """A (data)class to store information about a citation.

    Attributes
    ----------
    function_name : str
        The name of the module and function where the citation is needed.
    citation : str, optional
        The citation string.
    docstring : str, optional
        The docstring of the function.
    label : str, optional
        The (optional) user-defined label for the citation.
    """

    def __init__(self, function_name, docstring=None, label=None):
        self.function_name = function_name
        self.docstring = docstring
        self.label = label

        if label is not None and len(label) > 0:
            self.citation = label
        elif docstring is not None and len(docstring) > 0:
            # TODO: Parse the docstring for the actual citation.
            self.citation = docstring
        else:
            self.citation = "No citation provided."

    def __hash__(self):
        return hash(self.function_name)

    def __str__(self):
        return f"{self.function_name}: {self.citation}"

    def __repr__(self):
        return f"{self.function_name}:\n{self.citation}"


def citation(label=None):
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
            citation = CitationEntry(
                function_name=func.__qualname__,
                docstring=func.__doc__,
                label=label,
            )

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
        elif module.__spec__ is not None:
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
