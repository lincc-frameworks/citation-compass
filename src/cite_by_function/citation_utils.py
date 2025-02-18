"""A helper module to collect citations from a software package."""

import sys

CITATION_REGISTRY_ALL = {}
CITATION_REGISTRY_USED = {}


def citation(reference):
    """A function wrapper for adding a citation to a function.

    Parameters
    ----------
    func : function
        The function to wrap.
    reference : str
        A unique reference for this citation.

    Returns
    -------
    function
        The wrapped function.
    """

    def decorator(func):
        def fun_wrapper(*args, **kwargs):
            print(f"Calling {func.__module__}.{func.__name__} with citation {reference}")

            # Save the citation as USED when it is first called.
            if reference not in CITATION_REGISTRY_USED:
                cite_str = f"{reference}: {func.__module__}.{func.__name__}"
                CITATION_REGISTRY_USED[reference] = cite_str
            return func(*args, **kwargs)

        # Save the citation as ALL when it is first defined.
        cite_str = f"{reference}: {func.__module__}.{func.__name__}"
        if reference not in CITATION_REGISTRY_ALL:
            CITATION_REGISTRY_ALL[reference] = cite_str
        elif CITATION_REGISTRY_ALL[reference] != cite_str:
            raise ValueError(
                f"Duplicate citation reference '{reference}' for function "
                f"{cite_str}. Previously used for {CITATION_REGISTRY_ALL[reference]}."
            )
        return fun_wrapper

    return decorator


def get_all_imports():
    """Return a list of all imports in the software package.

    Returns
    -------
    imports : list of str
        A list of all imports in the software package.
    """
    imports = []
    for m in sys.modules:
        imports.append(str(m))
    return imports


def get_all_citations(include_imports=False):
    """Return a list of all citations in the software package.

    Parameters
    ----------
    include_imports : bool, optional
        Whether to include the import citations in the list.
        Default: True

    Returns
    -------
    citations : list of str
        A list of all citations in the software package.
    """
    citations = list(CITATION_REGISTRY_ALL.values())

    if include_imports:
        for m in get_all_imports():
            citations.append(f"import: {m}")

    return citations


def get_used_citations(include_imports=False):
    """Return a list of all citations in the software package.

    Parameters
    ----------
    include_imports : bool, optional
        Whether to include the import citations in the list.
        Default: True

    Returns
    -------
    list of str
        A list of all citations in the software package.
    """
    citations = list(CITATION_REGISTRY_USED.values())

    if include_imports:
        for m in get_all_imports():
            citations.append(f"import: {m}")

    return citations
