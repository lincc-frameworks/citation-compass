# cite-by-function

A simple, automatic tracker for creating a citation list by function used.


## Installing

TODO: Write this once it is available on pypi.


## Getting Started

The cite_by_function module works via a series of function decorators. You can attach a decorator to a function you would like to cite using:

```
@citation("lincc_frameworks_paper_2025")
def function_that_uses_it():
    ...
```

This will add an entry mapping the citation name ("lincc_frameworks_paper_2025") to the function. You can access all functions in your module (and its dependencies) that have a citation annotation using:

```
citation_list = get_all_citations()
```

or

```
citation_list = get_all_citations(include_imports=True)
```

where `include_imports=True` indicates that the code should return a list of **all** imported modules as well.

Similarly you can get a list of the citations for only the called functions during a run of the code by using:

```
citation_list = get_used_citations()
```

or

```
citation_list = get_used_citations(include_imports=True)
```

## Acknowledgements

This project is supported by Schmidt Sciences.