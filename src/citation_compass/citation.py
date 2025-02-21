"""A helper module to collect citations from a software package."""

from functools import wraps
import inspect
import logging
import sys

from .docstring_utils import check_docstring_for_keyword, extract_citation

CITATION_REGISTRY_ALL = {}
CITATION_REGISTRY_USED = set()


def _get_full_name(thing):
    """Return the maximally qualified name of a thing.

    Parameters
    ----------
    thing : object
        The thing to get the name of.

    Returns
    -------
    str
        The fully qualified name of the thing.
    """
    module = inspect.getmodule(thing)
    full_name = f"{module.__name__}.{thing.__qualname__}" if module else thing.__qualname__
    return full_name


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
        # Try to parse a citation from the
        citation_text = extract_citation(func.__doc__)
        if citation_text is None:
            citation_text = func.__doc__

        full_name = _get_full_name(func)

        return cls(
            key=full_name,
            citation=citation_text,
            label=label,
        )


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
    # If the label is callable, there were no parentheses on the
    # dectorator and it passed in the function instead. So use None
    # as the label.
    use_label = label if not callable(label) else None

    def decorator(func):
        full_name = _get_full_name(func)

        @wraps(func)
        def fun_wrapper(*args, **kwargs):
            # Save the citation as USED when it is first called.
            if func.__qualname__ not in CITATION_REGISTRY_USED:
                CITATION_REGISTRY_USED.add(full_name)
            return func(*args, **kwargs)

        # Save the citation as ALL when it is first defined.
        if full_name not in CITATION_REGISTRY_ALL:
            citation = CitationEntry.from_function(func, label=use_label)
            CITATION_REGISTRY_ALL[full_name] = citation
        else:
            logging.warning(f"Duplicated citation tag for function: {full_name}")

        return fun_wrapper

    if callable(label):
        return decorator(label)
    return decorator


def get_all_citations():
    """Return a list of all citations in the software package.

    Returns
    -------
    citations : list of str
        A list of all citations in the software package.
    """
    citations = [str(entry) for entry in CITATION_REGISTRY_ALL.values()]
    return citations


def get_used_citations():
    """Return a list of all citations in the software package.

    Returns
    -------
    list of str
        A list of all citations in the software package.
    """
    citations = [str(CITATION_REGISTRY_ALL[func_name]) for func_name in CITATION_REGISTRY_USED]
    return citations


def reset_used_citations():
    """Reset the list of used citations."""
    CITATION_REGISTRY_USED.clear()


def get_all_imports(skip_common=True, use_keywords=False):
    """Return a list of all imports in the software package.

    Parameters
    ----------
    skip_common : bool
        Whether to skip the common imports, such as the built-in modules.
    use_keywords : bool
        Check the import's docstring for keywords that indicate a citation.

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
            if origin is None:
                skip = False
            elif origin == "built-in":
                skip = True
            elif origin == "frozen":
                skip = True
            elif "Python.framework" in origin:
                skip = True

        if not skip_common or not skip:
            if use_keywords and hasattr(module, "__doc__"):
                if check_docstring_for_keyword(module.__doc__):
                    imports.append(name)
            else:
                imports.append(name)
    return imports
