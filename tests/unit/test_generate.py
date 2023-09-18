#    Copyright(C) 2023 Altom Consulting
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <https://www.gnu.org/licenses/>.

import os

import pytest

from altwalker.generate import DotnetGenerator, EmptyGenerator, PythonGenerator


class TestGenerator:
    pass


class TestEmptyGenerator:

    @pytest.fixture(autouse=True)
    def setup(self, tmpdir):
        self.tmpdir = tmpdir
        self.generator = EmptyGenerator(tmpdir, model_paths=[], git=False)

    def test_generate_methods(self):
        code = self.generator.generate_methods(methods=["vertex_A", "edge_A", "vertex_B"])
        expected = ""

        assert code == expected

    def test_generate_class(self):
        code = self.generator.generate_class(class_name="DefaultModel", methods=["vertex_A", "edge_A", "vertex_B"])
        expected = ""

        assert code == expected

    def test_generate_code(self):
        code = self.generator.generate_code(
            {
                "ModelA": ["vertex_A", "edge_A", "vertex_B"],
                "ModelB": ["vertex_C", "edge_D", "vertex_E"]
            }
        )
        expected = ""

        assert code == expected

    def test_generate_tests(self):
        self.generator.generate_tests(
            {
                "ModelA": ["vertex_A", "edge_A", "vertex_B"],
                "ModelB": ["vertex_C", "edge_D", "vertex_E"]
            }
        )

        package_path = os.path.join(self.tmpdir, "tests")
        assert os.path.isdir(package_path)


class TestPythonGenerator:

    @pytest.fixture(autouse=True)
    def setup(self, tmpdir):
        self.tmpdir = tmpdir
        self.generator = PythonGenerator(tmpdir, model_paths=[], git=False)

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
            "",
        ]

        assert code == "\n".join(expected)

    def test_generate_class(self):
        code = self.generator.generate_class(class_name="DefaultModel", methods=["vertex_A", "edge_A", "vertex_B"])
        expected = [
            "class DefaultModel:",
            "",
            "    def vertex_A(self):",
            "        pass",
            "",
            "    def edge_A(self):",
            "        pass",
            "",
            "    def vertex_B(self):",
            "        pass",
            "",
            ""
        ]

        assert code == "\n".join(expected)

    def test_generate_code(self):
        code = self.generator.generate_code(
            {
                "ModelA": ["vertex_A", "edge_A", "vertex_B"],
                "ModelB": ["vertex_C", "edge_D", "vertex_E"]
            }
        )
        expected = [
            "class ModelA:",
            "",
            "    def vertex_A(self):",
            "        pass",
            "",
            "    def edge_A(self):",
            "        pass",
            "",
            "    def vertex_B(self):",
            "        pass",
            "",
            "",
            "class ModelB:",
            "",
            "    def vertex_C(self):",
            "        pass",
            "",
            "    def edge_D(self):",
            "        pass",
            "",
            "    def vertex_E(self):",
            "        pass",
            "",
            "",
            ""
        ]

        assert code == "\n".join(expected)

    def test_generate_requirements(self):
        self.generator.generate_requirements()
        assert os.path.isfile(os.path.join(self.tmpdir, "requirements.txt"))

    def test_generate_tests(self):
        self.generator.generate_tests(
            {
                "ModelA": ["vertex_A", "edge_A", "vertex_B"],
                "ModelB": ["vertex_C", "edge_D", "vertex_E"]
            }
        )

        package_path = os.path.join(self.tmpdir, "tests")

        assert os.path.isfile(os.path.join(self.tmpdir, "requirements.txt"))
        assert os.path.isdir(package_path)
        assert os.path.isfile(os.path.join(package_path, "__init__.py"))
        assert os.path.isfile(os.path.join(package_path, "test.py"))


class TestDotnetGenerator:

    @pytest.fixture(autouse=True)
    def setup(self, tmpdir):
        self.tmpdir = tmpdir
        self.generator = DotnetGenerator(tmpdir, model_paths=[], git=False)

    def test_generate_methods(self):
        code = self.generator.generate_methods(methods=["vertex_A", "edge_A", "vertex_B"])
        expected = [
            "",
            "        public void vertex_A()",
            "        {",
            "        }",
            "",
            "        public void edge_A()",
            "        {",
            "        }",
            "",
            "        public void vertex_B()",
            "        {",
            "        }",
            ""
        ]

        assert code == "\n".join(expected)

    def test_generate_class(self):
        code = self.generator.generate_class(class_name="DefaultModel", methods=["vertex_A", "edge_A", "vertex_B"])
        expected = [
            "    public class DefaultModel",
            "    {",
            "",
            "        public void vertex_A()",
            "        {",
            "        }",
            "",
            "        public void edge_A()",
            "        {",
            "        }",
            "",
            "        public void vertex_B()",
            "        {",
            "        }",
            "",
            "    }",
        ]

        assert code == "\n".join(expected)

    def test_generate_code(self):
        code = self.generator.generate_code(
            {
                "ModelA": ["vertex_A", "edge_A", "vertex_B"],
                "ModelB": ["vertex_C", "edge_D", "vertex_E"]
            }
        )
        expected = [
            "using Altom.AltWalker;",
            "",
            "namespace Tests",
            "{",
            "",
            "    public class ModelA",
            "    {",
            "",
            "        public void vertex_A()",
            "        {",
            "        }",
            "",
            "        public void edge_A()",
            "        {",
            "        }",
            "",
            "        public void vertex_B()",
            "        {",
            "        }",
            "",
            "    }",
            "",
            "    public class ModelB",
            "    {",
            "",
            "        public void vertex_C()",
            "        {",
            "        }",
            "",
            "        public void edge_D()",
            "        {",
            "        }",
            "",
            "        public void vertex_E()",
            "        {",
            "        }",
            "",
            "    }",
            "",
            "    public class Program",
            "    {",
            "        public static void Main(string[] args)",
            "        {",
            "            ExecutorService service = new ExecutorService();",
            "            service.RegisterModel<ModelA>();",
            "            service.RegisterModel<ModelB>();",
            "            service.Run(args);",
            "        }",
            "    }",
            "}",
        ]

        assert code == "\n".join(expected)

    def test_generate_tests(self):
        self.generator.generate_tests(
            {
                "ModelA": ["vertex_A", "edge_A", "vertex_B"],
                "ModelB": ["vertex_C", "edge_D", "vertex_E"]
            }
        )

        package_path = os.path.join(self.tmpdir, "tests")

        assert os.path.isdir(package_path)
        assert os.path.isfile(os.path.join(package_path, "tests.csproj"))
