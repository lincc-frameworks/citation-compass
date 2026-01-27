import citation_compass


def test_version():
    """Check to see that we can get the package version"""
    assert citation_compass.__version__ is not None
