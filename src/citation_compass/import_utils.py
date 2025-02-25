"""A helper module for searching imports for citations."""

import sys

from citation_compass.docstring_utils import check_for_any_citation_keyword


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
