# citation-compass

A lightweight package for annotating and extracting citable portions of scientific code from Python modules.

The citation-compass module use a combination of author-specified tags and heuristics to discover citable portions of the code. It is not guaranteed to be complete, but rather serve as a helper to citable code discovery. All users should be careful to confirm they are citing all necessary code.

**Note: This module is currently under development and may still see significant API changes.**


## Installing

TODO: Write this once it is available on pypi.


## Getting Started

The citation-compase module works via a series of function decorators. You can attach a decorator to a function you would like to cite using:

```
@cite_function()
def function_that_uses_something():
    ...
```

This will add an entry mapping the function's identifier to citation information, which may include the docstring, a user defined label, or extracted information.

Users can access all functions in their module (and its dependencies) that have a citation annotation using:

```
citation_list = get_all_citations()
```

Similarly you can get a list of the citations for only the called functions during a run of the code by using:

```
citation_list = get_used_citations()
```

Since some packages need to be cited when they are used, you can also call

```
import_list = get_all_imports()
```

To get a list of all modules that were imported.


## Acknowledgements

This project is supported by Schmidt Sciences.