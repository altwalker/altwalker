import unittest

import pytest

from altwalker.executor import DotnetExecutorService, load


@pytest.mark.dotnet
class TestDotExecutorService(unittest.TestCase):

    def test_start_service(self):
        service = DotnetExecutorService("./tests/common/dotnet/simple-project", "http://0.0.0.0:1137")

        self.assertTrue(service._process.poll() is None)

        service.kill()
        service._process.wait()

        self.assertTrue(service._process.poll() is not None)


class TestLoad(unittest.TestCase):

    def test_load_same_module_from_different_paths(self):
        mymodule = load("./tests/common/load/v1", "tests", "test")
        self.assertFalse(mymodule.my_method())

        mymodule = load("./tests/common/load/v2", "tests", "test")
        self.assertTrue(mymodule.my_method())
