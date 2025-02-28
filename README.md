# citation-compass

A lightweight package for annotating and extracting citable portions of scientific code from Python modules.

The citation-compass module use a combination of author-specified tags and heuristics to discover citable portions of the code. It is not guaranteed to be complete, but rather serve as a helper to citable code discovery. All users should be careful to confirm they are citing all necessary code.

**Note: This module is currently under development and may still see significant API changes.**


## Installing

Citation-compass can be installed from pypi with:

```
pip install citation-compass
```

## Getting Started

The citation-compass module provides mechanisms for code authors to annotate portions of their code that should be cited. The author’s can annotate:

* **modules** - An author can add an annotation for a module (or submodule) by adding `cite_module(__name__)` function to the module's file. This will automatically determine the name of the current (sub)module and mark it for citation. Author's can also mark imported modules by passing in a string with the name of that module, such as `cite_module("astropy")`. Cited modules will automatically be included on both the all citations and used citations lists.

* **classes** - An author can annotate a class by inheriting from `CiteClass`, such as `my_class(dependency1, CiteClass):`. Cited classes will be included on the all citations list when they are defined and the used citation list when the first object is instantiated.

* **functions** - An author can annotate a function using the `@cite_function` decorator. Cited functions will be included on the all citations list when they are defined and the used citation list when they are first called.

* **methods** - An author can annotate a class method using the `@cite_function` decorator as well. Cited functions will be included on the all citations list when they are defined and the used citation list when they are first called.

* **objects** - An author can cite an instantiated object using the `cite_object(obj)` function. Note that we do not expect this to be a typical use case. Most users will want to use a class-level citation instead. However citing an object can be used with objects from external packages. Cited objects will be referenced by the object's class information. Cited objects are added to both the all citations and used citations list as soon as the `cite_object` function is called.

### Example: Citing a Function

Users can annotate a function using the `@cite_function` decorator. This will add an entry mapping the function's identifier to citation information, which may include the docstring, a user defined label, or extracted information.

```
@cite_function
def function_that_uses_something():
    """My docstring..."
    ...
```

### Example: Citing a Class

Users can annotate a class by inheriting from `CiteClass`:

```
my_class(dependency1, CiteClass):
    """My docstring..."
    def __init__(self, param1):
        ...
    ...
```

## Listing Citations

Users can access all functions in their module (and its dependencies) that have a citation annotation using:

```
citation_list = get_all_citations()
```

Similarly you can get a list of the citations for only the called functions during a run of the code by using:

```
citation_list = get_used_citations()
```

## Citation Formats

Citation information is pulled from the object's docstring. The extractor looks for sections denoted by keywords 'citation', 'citations', 'reference', or 'references'. These citation sections can be provided in either numpy or Google format. Here are some valid citation notations:

**Underlined section**

Underlined sections look for section delimiters of the form "keyword\n-------" with at least 2 dashes making up the underline. The citation section includes all text until the end of the string or the next section header.

Examples:

```
Citation
--------
    Author, Title, etc.
```

or

```
Citations
---------
    Author1, Title2, etc.
    Author2, Title2, etc.
```

**Colon-specified section**

Colon-specified sections look for section header where a line starts with "keyword:". The citation section includes all text until the end of the string or the next section header, including text following the section header itself.

Example single line citation:

```
Citation: Author, title, etc.
```

Example multi-line citation:

```
Citation:
    Author,
    title,
    etc.
```

## Exploring Imports

Since some packages need to be cited when they are used, you can also call

```
import_list = get_all_imports()
```

To get a list of all modules that were imported. This function includes two very rough heuristics for filtering the modules:

* **skip_common** (default: True): Use a heuristic to ignore files that are common python imports, such as anything in "built-in" or "frozen".

* **use_keywords** (default: False): Searches the module's docstring for words that could indicate the need to cite, such as "cite", "arxiv", or "acknowledgement".

## Acknowledgements

This project is supported by Schmidt Sciences.