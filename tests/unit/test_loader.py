import unittest

from altwalker._loader import load


class TestLoad(unittest.TestCase):

    def test_load(self):
        module = load("tests/common/", "python", "simple")
        self.assertTrue(hasattr(module, "Simple"))

    def test_load_submodule(self):
        module = load("tests/common/", "python", "complex")
        self.assertTrue(hasattr(module, "ComplexA"))
        self.assertTrue(hasattr(module, "ComplexB"))
        self.assertTrue(hasattr(module, "Base"))
