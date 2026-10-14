"""Display basic version information to standard out."""

from citation_compass._version import __version__


def main():
    """The main function for the example file."""
    print(f"citation_compass: {__version__}")


if __name__ == "__main__":
    main()
