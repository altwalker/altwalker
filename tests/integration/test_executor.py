import unittest

import pytest

from altwalker.executor import DotnetExecutorService


@pytest.mark.dotnet
class TestDotExecutorService(unittest.TestCase):

    def test_start_service(self):
        service = DotnetExecutorService("./tests/common/dotnet/simple-project", "http://0.0.0.0:1137")

        self.assertTrue(service._process.poll() is None)

        service.kill()
        service._process.wait()

        self.assertTrue(service._process.poll() is not None)
