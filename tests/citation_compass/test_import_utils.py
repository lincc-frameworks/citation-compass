import fake_module

from citation_compass.import_utils import get_all_imports


def test_get_all_imports():
    """Check that the imports are registered."""
    imports = get_all_imports(skip_common=False)
    assert len(imports) > 0
    assert "sys" in imports
    assert "fake_module" in imports

    # We can filter out Python's base imports.
    imports = get_all_imports(skip_common=True)
    assert len(imports) > 0
    assert "sys" not in imports
    assert "fake_module" in imports

    # We can search for citation keywords in the module docstrings.
    old_len = len(imports)
    imports = get_all_imports(skip_common=True, use_keywords=True)
    assert len(imports) > 0
    assert len(imports) < old_len
    assert "fake_module" in imports

    # We call fake_function to make sure it is correctly imported.
    assert fake_module.fake_function() == 0
