"""A helper module to collect citations from a software package."""

from functools import wraps
import inspect
import logging
import sys

from .docstring_utils import (
    check_for_any_citation_keyword,
    extract_citation,
    extract_urls,
)

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
    # Try to determine the name of the "thing".
    if hasattr(thing, "__qualname__"):
        base_name = thing.__qualname__
    elif hasattr(thing, "__name__"):
        base_name = thing.__name__
    elif hasattr(thing, "__class__"):
        # If this is an object, use the class's name.
        base_name = thing.__class__.__qualname__
    else:
        raise ValueError(f"Could not determine the name of {thing}")

    # Get the string for the module (if we can find it).
    module = inspect.getmodule(thing)
    full_name = base_name if module is None else f"{module.__name__}.{base_name}"
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
    urls : list of str
        A list of URLs extracted from the citation string.
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

        self.urls = extract_urls(self.citation)

    def __hash__(self):
        return hash(self.key)

    def __str__(self):
        return f"{self.key}: {self.citation}"

    def __repr__(self):
        return f"{self.key}:\n{self.citation}"

    @classmethod
    def from_object(cls, obj, label=None):
        """Create a CitationEntry from any object (including a function or method).

        Parameters
        ----------
        obj : object
            The object from which to create the citation.
        label : str, optional
            The (optional) user-defined label for the citation.

        Returns
        -------
        CitationEntry
            The citation entry.
        """
        # Try to parse a citation from the object's docstring (if there is one).
        if hasattr(obj, "__doc__"):
            docstring = obj.__doc__
        elif hasattr(obj, "__class__") and hasattr(obj.__class__, "__doc__"):
            docstring = obj.__class__.__doc__
        else:
            docstring = ""
        citation_text = extract_citation(docstring)
        if citation_text is None:
            citation_text = docstring

        full_name = _get_full_name(obj)

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
            if citation is None or len(citation) == 0:
                citation = module.__doc__

    CITATION_REGISTRY_ALL[name] = CitationEntry(name, citation)
    CITATION_REGISTRY_USED.add(name)


class CiteClass:
    """A super class for adding a citation to a class."""

    def __init__(self):
        pass

    def __init_subclass__(cls):
        # Add the class's full name
        full_name = _get_full_name(cls)
        cls._citation_compass_name = full_name

        # Save the citation as ALL when it is first defined.
        if full_name not in CITATION_REGISTRY_ALL:
            CITATION_REGISTRY_ALL[full_name] = CitationEntry.from_object(cls)
        else:
            logging.warning(f"Duplicated citation tag for class: {full_name}")

        # Wrap the constructor so the class is marked used when
        # the first object is instantiated.
        original_init = cls.__init__

        @wraps(original_init)
        def init_wrapper(*args, **kwargs):
            # Save the citation as USED when it is first called.
            if cls._citation_compass_name not in CITATION_REGISTRY_USED:
                CITATION_REGISTRY_USED.add(cls._citation_compass_name)
            return original_init(*args, **kwargs)

        cls.__init__ = init_wrapper


def cite_function(label=None):
    """A function wrapper for adding a citation to a function or
    class method.

    Parameters
    ----------
    label : str
        The (optional) user-defined label for the citation.

    Returns
    -------
    function
        The wrapped function or method.
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
            citation = CitationEntry.from_object(func, label=use_label)
            CITATION_REGISTRY_ALL[full_name] = citation
        else:
            logging.warning(f"Duplicated citation tag for function: {full_name}")

        return fun_wrapper

    if callable(label):
        return decorator(label)
    return decorator


def cite_object(obj, label=None):
    """Add a citation for a specific object.

    Parameters
    ----------
    obj : object
        The object to add a citation for.
    label : str, optional
        The (optional) user-defined label for the citation.
    """
    full_name = _get_full_name(obj)
    if full_name not in CITATION_REGISTRY_ALL:
        CITATION_REGISTRY_ALL[full_name] = CitationEntry.from_object(obj, label=label)
    else:
        logging.warning(f"Duplicated citation tag for object: {full_name}")

    CITATION_REGISTRY_USED.add(full_name)


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
        Uses a heuristic that checks if the import's docstring contains
        keywords that may indicate a citation.

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
                if check_for_any_citation_keyword(module.__doc__):
                    imports.append(name)
            else:
                imports.append(name)
    return imports
