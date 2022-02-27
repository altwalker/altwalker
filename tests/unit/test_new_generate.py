import pytest

from altwalker.generate import PythonGenerator


class TestGenerator:

    @pytest.fixture(autouse=True)
    def setUp(self):
        self.generator = PythonGenerator(".", model_paths=[], git=False)

    def test_generate_methods(self):
        code = self.generator.generate_methods(methods=["vertex_A", "edge_A", "vertex_B"])
        expected = [
            "",
            "def vertex_A(self):",
            "    pass",
            "",
            "def edge_A(self):",
            "    pass",
            "",
            "def vertex_B(self):",
            "    pass",
            ""
        ]

        assert code == "\n".join(expected)

    def test_generate_class(self):
        code = self.generator.generate_class(class_name="DefaultModel", methods=["vertex_A", "edge_A", "vertex_B"])
        expected = [
            "",
            "class DefaultModel:",
            "    ",
            "    def vertex_A(self):",
            "        pass",
            "    ",
            "    def edge_A(self):",
            "        pass",
            "    ",
            "    def vertex_B(self):",
            "        pass",
            "    "
        ]

        assert code == "\n".join(expected)