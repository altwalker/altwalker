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

from altwalker.loader import (AppendLoader, ImportlibLoader, ImportModes,
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
    ImportModes.IMPORTLIB,
    ImportModes.APPEND,
    ImportModes.PREPEND,
])
def test_create_loader(mode):
    loader = create_loader(mode=mode)
    module = loader.load("tests/data/python/simple.py", ".")

    assert hasattr(module, "Simple")
