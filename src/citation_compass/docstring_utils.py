"""A helper module for searching docstrings for citations."""

_CITATION_HEADER_KEYWORDS = [
    "acknowledgement",
    "acknowledgements",
    "citation",
    "citations",
    "reference",
    "references",
]
_CITATION_OTHER_KEYWORDS = [
    "acknowledge",
    "arxiv",
    "attribute",
    "attribution",
    "bibliography",
    "cite",
]

_CITATION_SECTION_HEADERS = set([f"{keyword}:" for keyword in _CITATION_HEADER_KEYWORDS])
_CITATION_ALL_KEYWORDS = _CITATION_HEADER_KEYWORDS + _CITATION_OTHER_KEYWORDS


def check_for_any_citation_keyword(string):
    """Checks a string for any of the keywords that indicate a citation,
    which can include the words in the middle of a sentence. As such, this approach
    is a heuristic and does not require the citation to be in a specific format. It
    is meant to be used to assess whether a module that is not tagged by this one
    may contain citations.

    Parameters
    ----------
    string : str
        The string to check.

    Returns
    -------
    bool
        Whether the docstring contains a keyword that indicates a citation.
    """
    if string is None or len(string) == 0:
        return False

    for line in [line.lower() for line in string.split("\n")]:
        for keyword in _CITATION_ALL_KEYWORDS:
            if keyword in line:
                return True
    return False


def extract_citation(docstring):
    """Extracts the citation from a docstring.

    This function assumes that the citation is in the formatted to
    match this package using the "keyword: information" structure at
    the start of a line.

    For example, if the docstring contains:
    "Citation:
        Author, Title, year.

    Other information..."

    The extracted citation will be "Author, Title, year".

    Parameters
    ----------
    docstring : str
        The docstring to extract the citation from.

    Returns
    -------
    str or None
        The extracted citation or None if no citation is found.
    """
    if docstring is None or len(docstring) == 0:
        return None

    all_lines = [line.strip() for line in docstring.split("\n")]

    # We search for a line the starts with one of the citation keywords.
    for idx, line in enumerate(all_lines):
        for keyword in _CITATION_SECTION_HEADERS:
            if line.lower().startswith(keyword):
                # We have a reference of the form "keyword: information".
                # Take the rest of what is on that line and all following lines until
                # we reach a blank line.
                citation = line[len(keyword) + 1 :]

                idx += 1
                while idx < len(all_lines) and len(all_lines[idx]) > 0:
                    citation += " " + all_lines[idx]
                    idx += 1

                return citation.strip()
    return None


def extract_urls(string):
    """Extracts URLs from a string.

    Parameters
    ----------
    string : str
        The string to extract URLs from.

    Returns
    -------
    urls : list of str
        The extracted URLs.
    """
    if string is None or len(string) == 0:
        return []

    urls = []
    for word in string.split():
        if "http" in word:
            urls.append(word)
    return urls
