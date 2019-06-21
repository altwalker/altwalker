import platform
import unittest

from altwalker._utils import get_command, url_join


class TestGetCommand(unittest.TestCase):

    def test_get_command(self):
        if platform.system() == "Windows":
            self.assertListEqual(get_command("gw"), ["cmd.exe", "/C", "gw"])
        else:
            self.assertListEqual(get_command("gw"), ["gw"])


class TestUrlJoin(unittest.TestCase):

    def test_url_join(self):
        expected = "http://localhost:5000/altwalker"

        self.assertEqual(url_join("http://localhost:5000", "altwalker"), expected)
        self.assertEqual(url_join("http://localhost:5000", "/altwalker"), expected)
        self.assertEqual(url_join("http://localhost:5000", "/altwalker/"), expected)
        self.assertEqual(url_join("http://localhost:5000/", "altwalker"), expected)
        self.assertEqual(url_join("http://localhost:5000/", "/altwalker"), expected)
        self.assertEqual(url_join("http://localhost:5000/", "/altwalker/"), expected)
