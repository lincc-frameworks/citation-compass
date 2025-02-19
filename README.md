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