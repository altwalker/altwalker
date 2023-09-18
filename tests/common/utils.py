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
from contextlib import contextmanager


@contextmanager
def run_isolation(runner, files, folders=None):
    with runner.isolated_filesystem():

        for file_path, content in files:
            path, _ = os.path.split(file_path)

            if path:
                if not os.path.exists(path):
                    os.makedirs(path)

            with open(file_path, "w") as f:
                if content:
                    f.write(content)

        if folders:
            for path in folders:
                if not os.path.exists(path):
                    os.makedirs(path)

        yield
