import os
import unittest
from contextlib import contextmanager

from click.testing import CliRunner


@contextmanager
def run_isolation(runner, files, folders=None):
    with runner.isolated_filesystem():

        for file_path, content in files:
            path, _ = os.path.split(file_path)
            
            if path:
                if not os.path.exists(path):
                    os.makedirs(path)
                
            with open(file_path, "w") as f:
                f.write(content)

        if folders:
            for path in folders: 
                if not os.path.exists(path):
                    os.makedirs(path)

        yield
