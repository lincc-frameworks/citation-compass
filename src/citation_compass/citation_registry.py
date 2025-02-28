"""A helper module to collect citations from a software package."""

import inspect

from citation_compass.docstring_utils import (
    extract_citation,
    extract_urls,
)


def get_object_full_name(obj):
    """Return the maximally qualified name of a thing.

    Parameters
    ----------
    obj : object
        The obj to get the name of.

    Returns
    -------
    str
        The fully qualified name of the thing.
    """
    # Try to determine the name of the "thing".
    if hasattr(obj, "__qualname__"):
        base_name = obj.__qualname__
    elif hasattr(obj, "__name__"):
        base_name = obj.__name__
    elif hasattr(obj, "__class__"):
        # If this is an object, use the class's name.
        base_name = obj.__class__.__qualname__
    else:
        raise ValueError(f"Could not determine the name of {obj}")

    # Get the string for the module (if we can find it).
    module = inspect.getmodule(obj)
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

        full_name = get_object_full_name(obj)

        return cls(
            key=full_name,
            citation=citation_text,
            label=label,
        )


class CitationRegistry:
    """A class to store and manage citations for a software package.

    Attributes
    ----------
    all_entries : dict
        A dictionary mapping a annotation's key to its CitationEntry object.
    used_entries : set
        A set of keys for the "used" citations that have been used. This key matches
        the citation's key in the `all_entries` dictionary.
    used_trackers : dict
        A dictionary of additional user-defined trackers for used citations. Each
        tracker is a set of keys for the citations that have been used.
    """

    def __init__(self):
        self.all_entries = {}

        # We include a separate set of all used entries (instead of adding a "global"
        # entry to used_trackers) to avoid having to avoid having to do a dictionary
        # lookup for the "global" tracker. This adds some code complexity, but should
        # be faster in the common case.
        self.used_entries = set()
        self.used_trackers = {}

    def __len__(self):
        return len(self.all_entries)

    def __contains__(self, key):
        return key in self.all_entries

    def __getitem__(self, key):
        return self.all_entries[key]

    def add(self, key, citation):
        """Add a citation to the registry.

        Parameters
        ----------
        key : str
            The key for the citation.
        citation : CitationEntry, str, or object
            The citation entry to add.
        """
        if key not in self.all_entries:
            if isinstance(citation, CitationEntry):
                self.all_entries[key] = citation
            elif isinstance(citation, str):
                self.all_entries[key] = CitationEntry(key, citation)
            else:
                self.all_entries[key] = CitationEntry.from_object(citation)

    def mark_used(self, key):
        """Mark a citation as used.

        Parameters
        ----------
        key : str
            The key for the citation.
        """
        if key not in self.used_entries:
            # Check if we already have a global "used" citation for this key
            # and, if not, add it.
            self.used_entries.add(key)
        if len(self.used_trackers) > 0:
            # We avoid the loop if there are no trackers.  This is slightly
            # after than iterating over an empty dictionary.
            for tracker in self.used_trackers.values():
                if key not in tracker:
                    tracker.add(key)

    def num_trackers(self):
        """Return the number of trackers in use.

        Returns
        -------
        int
            The number of trackers.
        """
        # The number of custom trackers, plus the glabl used tracker.
        return len(self.used_trackers) + 1

    def start_used_tracker(self, name):
        """Add another tracker of used citations.

        Parameters
        ----------
        name : str
            The name of the tracker.
        """
        if name not in self.used_trackers:
            self.used_trackers[name] = set()
        else:
            raise KeyError(f"Tracker {name} already exists.")

    def stop_used_tracker(self, name):
        """Stop tracking used citations.

        Parameters
        ----------
        name : str
            The name of the tracker.

        Returns
        -------
        list of CitationEntry
            The list of used citations in the tracker.
        """
        if name in self.used_trackers:
            used = [self.all_entries[key] for key in self.used_trackers[name]]
            del self.used_trackers[name]
        else:
            raise KeyError(f"Tracker {name} does not exist.")
        return used

    def get_all_citations(self):
        """Return a list of all citations in the software package.

        Returns
        -------
        list of CitationEntry
            A list of all citations in the software package.
        """
        return list(self.all_entries.values())

    def get_used_citations(self, tracker_name=None):
        """Return a list of the used citations in the software package.

        Parameters
        ----------
        tracker_name : str, optional
            The name of the tracker to get the used citations for.
            If None, the global tracker is used.

        Returns
        -------
        list of CitationEntry
            A list of the citations used within the scope of the tracker.
        """
        if tracker_name is None:
            tracker = self.used_entries
        elif tracker_name in self.used_trackers:
            tracker = self.used_trackers[tracker_name]
        else:
            raise KeyError(f"Tracker {tracker_name} does not exist.")
        return [self.all_entries[key] for key in tracker]

    def reset_used_citations(self, tracker_name=None):
        """Reset the used citations for a tracker.

        Parameters
        ----------
        tracker_name : str, optional
            The name of the tracker to reset.
            If None, the global tracker is reset.
        """
        if tracker_name is None:
            self.used_entries = set()
        elif tracker_name in self.used_trackers:
            self.used_trackers[tracker_name] = set()
        else:
            raise KeyError(f"Tracker {tracker_name} does not exist.")


# ----------------------------------------------------------------------------
# The GLOBAL citation registry -----------------------------------------------
# ----------------------------------------------------------------------------

CITATION_COMPASS_REGISTRY = CitationRegistry()
