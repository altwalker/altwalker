from altwalker._loader import load


def test_load():
    module = load("tests/data/python/simple.py", ".")

    assert hasattr(module, "Simple")


def test_load_submodule():
    module = load("tests/data/python/complex.py", ".")

    assert hasattr(module, "ComplexA")
    assert hasattr(module, "ComplexB")
    assert hasattr(module, "Base")
