"""A helper module for searching docstrings for citations."""

_CITATION_HEADER_KEYWORDS = [
    "citation",
    "citations",
    "reference",
    "references",
]
_CITATION_OTHER_KEYWORDS = [
    "acknowledgement",
    "acknowledgements",
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
    """Extracts citation(s) from a docstring.

    This function assumes that the citation is in the formatted to
    match this package using the "keyword: information" structure at
    the start of a line or underlined keyword.

    For example, if the docstring contains either

    "Citation:
        Author, Title, year.

    Other information..."

    or

    "Citation
     --------
        Author, Title, year.

    Other information..."

    The extracted citation will be "Author, Title, year".

    Parameters
    ----------
    docstring : str
        The docstring to extract the citation from.

    Returns
    -------
    extracted_citations: str or None
        The extracted citation or None if no citation is found.
    """
    if docstring is None or len(docstring) == 0:
        return None

    all_lines = [line.strip() for line in docstring.split("\n")]

    # We search for a line the starts with one of the citation keywords.
    extracted_citations = ""
    current_citation = ""
    block_type = "None"
    for idx, line in enumerate(all_lines):
        if block_type == "None":
            # We are not currently in a citation block, so we check if this
            # line is the start of that block.
            if (
                len(line) > 1
                and line == "-" * len(line)
                and idx > 0
                and all_lines[idx - 1].lower() in _CITATION_HEADER_KEYWORDS
            ):
                # Check for an underlined section header. Note the section title will
                # be on the previous line.
                current_citation = ""
                block_type = "-"
            else:
                # Check if we are in a citation block of the form 'keyword: information'.
                for keyword in _CITATION_SECTION_HEADERS:
                    if line.lower().startswith(keyword):
                        block_type = ":"
                        current_citation = line[len(keyword) + 1 :]
                        break
        else:
            # We are already in a block, so check for the end of the block.
            if (
                block_type == "-"
                and idx < len(all_lines) - 1
                and len(all_lines[idx + 1]) > 1
                and all_lines[idx + 1] == "-" * len(all_lines[idx + 1])
            ):
                # Section type citation blocks end when we hit the next section.
                # Check by looking for the underling of the section header. If found,
                # do not add the current line because it is the next section title.
                block_type = "Done"
            elif block_type == ":" and len(line) == 0:
                # End the 'keyword:' block when we hit a blank line.
                block_type = "Done"
            else:
                # We are still in the block, so add the line to the current citation.
                current_citation += " " + line

        # We have finished the block, so add the citation to the extracted_citations.
        # We do this outside the if-else block to ensure we get single line citations.
        if block_type == "Done" or idx == len(all_lines) - 1:
            if len(current_citation) > 0:
                extracted_citations += "\n" + current_citation.strip()
                current_citation = ""

            # We are no longer in a citation block.
            block_type = "None"

    # Remove leading and trailing whitespace.
    extracted_citations = extracted_citations.strip()
    if len(extracted_citations) > 0:
        return extracted_citations
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
