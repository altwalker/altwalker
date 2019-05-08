import platform
import unittest

from altwalker._utils import get_command


class TestGetCommand(unittest.TestCase):

    def test_get_command(self):
        if platform.system() == "Windows":
            self.assertListEqual(get_command("gw"), ["cmd.exe", "/C", "gw"])
        else:
            self.assertListEqual(get_command("gw"), ["gw"])
