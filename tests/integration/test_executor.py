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

import pytest

from altwalker.executor import DotnetExecutorService
from altwalker.loader import ImportlibLoader


@pytest.mark.dotnet
def test_dotnet_executor_service():
    service = DotnetExecutorService("./tests/common/dotnet/simple-project", "http://0.0.0.0:1137")

    assert service._process.poll() is None

    service.kill()

    assert service._process.poll() is not None


def test_load_same_module_from_different_paths():
    test_module = ImportlibLoader.load("./tests/common/python/v1/tests/test.py", ".")
    assert not test_module.test_method()

    test_module = ImportlibLoader.load("./tests/common/python/v2/tests/test.py", ".")
    assert test_module.test_method()
