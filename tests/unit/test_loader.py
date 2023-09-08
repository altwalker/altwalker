import pytest

from altwalker.loader import (AppendLoader, ImportingModes, ImportlibLoader,
                              PrependLoader, create_loader)


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


@pytest.mark.parametrize("mode", [
    ImportingModes.IMPORTLIB,
    ImportingModes.APPEND,
    ImportingModes.PREPEND,
])
def test_create_loader(mode):
    loader = create_loader(mode=mode)
    module = loader.load("tests/data/python/simple.py", ".")

    assert hasattr(module, "Simple")
