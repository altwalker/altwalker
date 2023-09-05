import pytest

from altwalker._loader import ImportlibLoader, AppendLoader, PrependLoader


@pytest.mark.parametrize("loader", [ImportlibLoader, AppendLoader, PrependLoader])
def test_load(loader):
    module = loader.load("tests/data/python/simple.py", ".")

    assert hasattr(module, "Simple")


@pytest.mark.parametrize("loader", [ImportlibLoader, AppendLoader, PrependLoader])
def test_load_submodule(loader):
    module = loader.load("tests/data/python/complex.py", ".")

    assert hasattr(module, "ComplexA")
    assert hasattr(module, "ComplexB")
    assert hasattr(module, "Base")
