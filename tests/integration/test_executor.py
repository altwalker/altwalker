import pytest

from altwalker.executor import load, DotnetExecutorService


@pytest.mark.dotnet
def test_dotnet_executor_service():
    service = DotnetExecutorService("./tests/common/dotnet/simple-project", "http://0.0.0.0:1137")

    assert service._process.poll() is None

    service.kill()

    assert service._process.poll() is not None


def test_load_same_module_from_different_paths():
    test_module = load("./tests/common/python/v1", "tests", "test")
    assert not test_module.test_method()

    test_module = load("./tests/common/python/v2", "tests", "test")
    assert test_module.test_method()
